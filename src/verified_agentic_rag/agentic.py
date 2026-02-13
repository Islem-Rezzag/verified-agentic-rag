from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .config import AppConfig
from .index import VectorIndex
from .retrieve import RetrievalTrace, Retriever, RetrievedChunk, question_mentions_doc
from .generate import LLMClient, AnswerOut
from .cite import allowed_labels_from_chunks, validate_citations
from .policy_fields import (
    PolicyFieldMatch,
    detect_policy_field_question,
    extract_policy_field,
    format_extracted_answer,
)
from .verify import verify_answer_grounding, VerificationResult


@dataclass
class AgentRun:
    question: str
    final_query_used: str
    attempts: int
    retrieved: List[RetrievedChunk]
    answer: AnswerOut
    retrieval_grade_reason: str = ""
    retrieval_supporting_labels: List[str] = field(default_factory=list)
    verification: Optional[Dict[str, Any]] = None
    retrieval_trace: Optional[RetrievalTrace] = None


def _now_ts() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def _hash_question(q: str) -> str:
    return hashlib.sha1(q.encode("utf-8")).hexdigest()[:10]


def _to_confidence_level(
    *,
    answer: AnswerOut,
    retrieval: List[RetrievedChunk],
    supporting_labels: List[str],
    verification: Optional[VerificationResult],
    extraction_used: bool,
) -> str:
    if answer.cannot_answer:
        return "low"

    if verification is not None and (not verification.all_supported):
        return "low"

    if extraction_used:
        return "high"

    top1 = retrieval[0].similarity if retrieval else 0.0
    top2 = retrieval[1].similarity if len(retrieval) > 1 else 0.0
    margin = top1 - top2
    support_count = len(supporting_labels)

    if top1 >= 0.5 and margin >= 0.02 and support_count >= 1:
        return "high"
    if top1 >= 0.35 and support_count >= 1:
        return "medium"
    return "low"


def _best_matching_doc(question: str, retrieved: List[RetrievedChunk]) -> Optional[str]:
    if not retrieved:
        return None

    mentioned = [c.rel_path for c in retrieved if question_mentions_doc(question, c.rel_path)]
    if mentioned:
        return mentioned[0]

    scores: Dict[str, float] = {}
    n = len(retrieved)
    for idx, c in enumerate(retrieved, start=1):
        rank_bonus = float(n - idx + 1)
        sim_bonus = max(0.0, float(c.similarity))
        header_bonus = 0.5 if c.chunk_type == "header" else 0.0
        scores[c.rel_path] = scores.get(c.rel_path, 0.0) + rank_bonus + sim_bonus + header_bonus

    return max(scores.items(), key=lambda x: x[1])[0]


def _extract_policy_field_with_doc_scan(
    *,
    question: str,
    retrieved: List[RetrievedChunk],
    retriever: Retriever,
) -> Optional[PolicyFieldMatch]:
    if detect_policy_field_question(question) is None:
        return None

    direct = extract_policy_field(question=question, chunks=retrieved)
    if direct is not None:
        return direct

    best_doc = _best_matching_doc(question, retrieved)
    if not best_doc:
        return None

    doc_chunks = retriever.get_document_chunks(best_doc)
    if not doc_chunks:
        return None

    return extract_policy_field(question=question, chunks=doc_chunks)


def ask_question(cfg: AppConfig, question: str, debug: bool = False, no_llm: bool = False) -> AgentRun:
    """
    Main entry point for your agentic RAG.

    Steps:
    1) retrieve chunks
    2) grade retrieval (LLM)
    3) if weak, rewrite query and retrieve again
    4) generate final answer with citations
    5) validate citations
    6) log to data/logs
    """
    cfg.ensure_dirs()

    index = VectorIndex(
        persist_dir=cfg.persist_dir,
        collection_name=cfg.collection_name,
        embedding_model=cfg.embedding_model,
    )
    retriever = Retriever(index=index, cfg=cfg)

    retrieved: List[RetrievedChunk] = []
    final_query = question
    attempts = 0
    grade_reason = ""
    grade_supporting_labels: List[str] = []
    retrieval_relevant = False
    retrieval_trace = RetrievalTrace()
    deterministic_match: Optional[PolicyFieldMatch] = None

    if no_llm:
        # Retrieval-only mode: useful before you have an API key.
        retrieved, retrieval_trace = retriever.retrieve_with_trace(query=question, top_k=cfg.top_k)
        dummy = AnswerOut(
            answer="LLM disabled. Showing retrieved sources only.",
            citations=[],
            confidence="low",
            cannot_answer=True,
            follow_ups=[],
            model_confidence="low",
            computed_confidence="low",
        )
        run = AgentRun(
            question=question,
            final_query_used=question,
            attempts=1,
            retrieved=retrieved,
            answer=dummy,
            retrieval_grade_reason="LLM disabled",
            retrieval_supporting_labels=[],
            verification=None,
            retrieval_trace=retrieval_trace,
        )
        _log_run(cfg, run)
        return run

    llm = LLMClient(cfg)

    # Agentic loop: at most cfg.agentic_max_rounds retrieval attempts
    query = question
    for attempt in range(cfg.agentic_max_rounds):
        attempts += 1
        retrieved, retrieval_trace = retriever.retrieve_with_trace(query=query, top_k=cfg.top_k)

        if debug:
            print("\n--- Retrieved chunks ---")
            for i, c in enumerate(retrieved, 1):
                print(
                    f"{i}. {c.rel_path}:{c.start_line}-{c.end_line}"
                    f"  type={c.chunk_type}  sim={c.similarity:.3f}"
                    f"  d_rank={c.dense_rank} s_rank={c.sparse_rank}"
                    f"  fuse={c.fusion_score} rerank={c.rerank_score}"
                )

        deterministic_match = _extract_policy_field_with_doc_scan(
            question=question,
            retrieved=retrieved,
            retriever=retriever,
        )
        if deterministic_match is not None:
            retrieval_relevant = True
            grade_reason = "deterministic metadata extraction matched"
            grade_supporting_labels = [deterministic_match.label]
            final_query = query
            break

        grade = llm.grade_retrieval(question=question, chunks=retrieved)
        grade_reason = grade.reason
        grade_supporting_labels = list(grade.supporting_labels)

        # Strict relevance: grader must both mark relevant and point to explicit supporting labels.
        if grade.relevant and len(grade_supporting_labels) > 0:
            retrieval_relevant = True
            final_query = query
            break

        # Not relevant: rewrite query for the next attempt
        rewritten = grade.suggested_rewrite.strip() or llm.rewrite_query(question)
        if debug:
            print(f"\n[Agent] Retrieval not good enough. Rewriting query to: {rewritten}")
        query = rewritten
        final_query = query

    if not retrieval_relevant:
        if debug:
            print("\n[Agent] Retrieval not relevant after max rounds. Refusing to answer.")
        answer = AnswerOut(
            answer="I cannot answer from the repository based on the retrieved sources.",
            citations=[],
            confidence="low",
            cannot_answer=True,
            follow_ups=[],
            model_confidence="low",
            computed_confidence="low",
        )
        run = AgentRun(
            question=question,
            final_query_used=final_query,
            attempts=attempts,
            retrieved=retrieved,
            answer=answer,
            retrieval_grade_reason=grade_reason,
            retrieval_supporting_labels=grade_supporting_labels,
            verification=None,
            retrieval_trace=retrieval_trace,
        )
        _log_run(cfg, run)
        return run

    extraction_used = deterministic_match is not None
    if deterministic_match is not None:
        # Deterministic value extraction for policy metadata questions.
        answer = AnswerOut(
            answer=format_extracted_answer(question, deterministic_match),
            citations=[deterministic_match.label],
            confidence="high",
            cannot_answer=False,
            follow_ups=[],
            model_confidence="high",
            computed_confidence=None,
        )
    else:
        # Generate answer using the best retrieved chunks.
        answer = llm.answer_with_citations(question=question, chunks=retrieved)

    # Validate citations one more time at orchestration layer
    allowed = allowed_labels_from_chunks(retrieved)
    all_valid, invalid = validate_citations(answer.answer, allowed)
    if debug and (not all_valid):
        print(f"\n[Warning] Invalid citations found: {invalid}")

    llm_judge = None
    if cfg.grounded_judge_enabled:
        llm_judge = lambda q, claim, cited: llm.judge_claim_support(q, claim, cited).supported

    verification = verify_answer_grounding(
        question=question,
        answer_text=answer.answer,
        retrieved=retrieved,
        llm_claim_judge=llm_judge,
    )

    if (not answer.cannot_answer) and (not verification.all_supported):
        if debug:
            print("\n[Agent] Unsupported claims detected. Attempting one grounded rewrite.")
        answer = llm.rewrite_to_supported(
            question=question,
            chunks=retrieved,
            previous_answer=answer.answer,
            unsupported_sentences=verification.unsupported_sentences,
        )
        verification = verify_answer_grounding(
            question=question,
            answer_text=answer.answer,
            retrieved=retrieved,
            llm_claim_judge=llm_judge,
        )

    if (not answer.cannot_answer) and (not verification.all_supported):
        answer = AnswerOut(
            answer="I cannot answer from the repository based on the retrieved sources.",
            citations=[],
            confidence="low",
            cannot_answer=True,
            follow_ups=[],
            model_confidence=answer.model_confidence or answer.confidence,
            computed_confidence="low",
        )

    computed = _to_confidence_level(
        answer=answer,
        retrieval=retrieved,
        supporting_labels=grade_supporting_labels,
        verification=verification,
        extraction_used=extraction_used,
    )
    answer.computed_confidence = computed  # type: ignore[assignment]
    answer.confidence = computed  # type: ignore[assignment]
    if answer.model_confidence is None:
        answer.model_confidence = answer.confidence  # type: ignore[assignment]

    run = AgentRun(
        question=question,
        final_query_used=final_query,
        attempts=attempts,
        retrieved=retrieved,
        answer=answer,
        retrieval_grade_reason=grade_reason,
        retrieval_supporting_labels=grade_supporting_labels,
        verification={
            "all_supported": verification.all_supported,
            "checks": [
                {
                    "sentence": c.sentence,
                    "citations": c.citations,
                    "supported": c.supported,
                    "reason": c.reason,
                }
                for c in verification.checks
            ],
        },
        retrieval_trace=retrieval_trace,
    )
    _log_run(cfg, run)
    return run


def _log_run(cfg: AppConfig, run: AgentRun) -> None:
    """
    Save a JSON log record for debugging and learning.
    """
    cfg.logs_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{_now_ts()}_{_hash_question(run.question)}.json"
    path = cfg.logs_dir / filename

    payload: Dict[str, Any] = {
        "question": run.question,
        "final_query_used": run.final_query_used,
        "attempts": run.attempts,
        "retrieval_grade_reason": run.retrieval_grade_reason,
        "retrieval_supporting_labels": run.retrieval_supporting_labels,
        "retrieved": [
            {
                "chunk_id": c.chunk_id,
                "rel_path": c.rel_path,
                "start_line": c.start_line,
                "end_line": c.end_line,
                "chunk_type": c.chunk_type,
                "distance": c.distance,
                "similarity": c.similarity,
                "dense_rank": c.dense_rank,
                "sparse_rank": c.sparse_rank,
                "fusion_score": c.fusion_score,
                "rerank_score": c.rerank_score,
            }
            for c in run.retrieved
        ],
        "answer": run.answer.model_dump(),
        "verification": run.verification,
    }
    if run.retrieval_trace is not None:
        payload["retrieval_trace"] = {
            "dense_candidates": [
                {
                    "chunk_id": c.chunk_id,
                    "rel_path": c.rel_path,
                    "start_line": c.start_line,
                    "end_line": c.end_line,
                    "chunk_type": c.chunk_type,
                    "distance": c.distance,
                    "similarity": c.similarity,
                    "dense_rank": c.dense_rank,
                    "sparse_rank": c.sparse_rank,
                    "fusion_score": c.fusion_score,
                    "rerank_score": c.rerank_score,
                }
                for c in run.retrieval_trace.dense_candidates
            ],
            "sparse_candidates": [
                {
                    "chunk_id": c.chunk_id,
                    "rel_path": c.rel_path,
                    "start_line": c.start_line,
                    "end_line": c.end_line,
                    "chunk_type": c.chunk_type,
                    "distance": c.distance,
                    "similarity": c.similarity,
                    "dense_rank": c.dense_rank,
                    "sparse_rank": c.sparse_rank,
                    "fusion_score": c.fusion_score,
                    "rerank_score": c.rerank_score,
                }
                for c in run.retrieval_trace.sparse_candidates
            ],
            "fused_candidates": [
                {
                    "chunk_id": c.chunk_id,
                    "rel_path": c.rel_path,
                    "start_line": c.start_line,
                    "end_line": c.end_line,
                    "chunk_type": c.chunk_type,
                    "distance": c.distance,
                    "similarity": c.similarity,
                    "dense_rank": c.dense_rank,
                    "sparse_rank": c.sparse_rank,
                    "fusion_score": c.fusion_score,
                    "rerank_score": c.rerank_score,
                }
                for c in run.retrieval_trace.fused_candidates
            ],
            "reranked_candidates": [
                {
                    "chunk_id": c.chunk_id,
                    "rel_path": c.rel_path,
                    "start_line": c.start_line,
                    "end_line": c.end_line,
                    "chunk_type": c.chunk_type,
                    "distance": c.distance,
                    "similarity": c.similarity,
                    "dense_rank": c.dense_rank,
                    "sparse_rank": c.sparse_rank,
                    "fusion_score": c.fusion_score,
                    "rerank_score": c.rerank_score,
                }
                for c in run.retrieval_trace.reranked_candidates
            ],
            "final_top_k": [
                {
                    "chunk_id": c.chunk_id,
                    "rel_path": c.rel_path,
                    "start_line": c.start_line,
                    "end_line": c.end_line,
                    "chunk_type": c.chunk_type,
                    "distance": c.distance,
                    "similarity": c.similarity,
                    "dense_rank": c.dense_rank,
                    "sparse_rank": c.sparse_rank,
                    "fusion_score": c.fusion_score,
                    "rerank_score": c.rerank_score,
                }
                for c in run.retrieval_trace.final_top_k
            ],
        }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
