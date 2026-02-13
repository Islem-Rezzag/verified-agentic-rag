from __future__ import annotations

import hashlib
import json
import re
import time
from collections import Counter
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


_POLICY_CONTEXT_PATTERNS: List[str] = [
    r"\bpolicy\b",
    r"\bpolicy pack\b",
    r"\bdocument status\b",
    r"\bversion history\b",
    r"\bresponsible committee\b",
    r"\bresponsible officer\b",
    r"\bpolicy group\b",
    r"\breview date\b",
    r"\breview frequency\b",
    r"\bdata protection\b",
    r"\bequality\b",
    r"\bdiversity\b",
    r"\brecruitment\b",
    r"\bemployee handbook\b",
    r"\bacceptable use\b",
    r"\btown clerk\b",
    r"\bline manager\b",
    r"\blawful basis\b",
    r"\bdocument retention\b",
]

_OFFTOPIC_PATTERNS: List[str] = [
    r"\bkubernetes\b",
    r"\bterraform\b",
    r"\bdocker\b",
    r"\baws\b",
    r"\bbitcoin\b",
    r"\bpremier league\b",
    r"\bexchange rate\b",
    r"\bweather\b",
    r"\brestaurants?\b",
    r"\bimmigration\b",
    r"\bopenai\b",
    r"\bcrewai\b",
    r"\btransformer model\b",
    r"\bcapital of france\b",
    r"\bbash script\b",
]


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


def _norm_rel_path(rel_path: str) -> str:
    return (rel_path or "").replace("\\", "/").strip().lower()


def _question_has_policy_context(question: str, retrieved: List[RetrievedChunk]) -> bool:
    q = question or ""

    if any(question_mentions_doc(q, c.rel_path) for c in retrieved):
        return True

    if any(re.search(p, q, flags=re.IGNORECASE) for p in _OFFTOPIC_PATTERNS):
        return False

    return any(re.search(p, q, flags=re.IGNORECASE) for p in _POLICY_CONTEXT_PATTERNS)


def _heuristic_retrieval_relevant(question: str, retrieved: List[RetrievedChunk]) -> bool:
    """
    Fallback guardrail when LLM retrieval grading is too strict.

    We only enable this for clearly in-domain policy questions and only when
    retrieval is concentrated on one policy file with reasonable similarity.
    """
    if not retrieved:
        return False
    if not _question_has_policy_context(question, retrieved):
        return False

    top_similarity = float(retrieved[0].similarity) if retrieved else 0.0
    if top_similarity < 0.35:
        return False

    by_doc = Counter(c.rel_path for c in retrieved if c.rel_path)
    if not by_doc:
        return False
    _doc, count = by_doc.most_common(1)[0]
    return count >= max(3, len(retrieved) // 2)


def _extract_policy_field_with_doc_scan(
    *,
    question: str,
    retrieved: List[RetrievedChunk],
    retriever: Retriever,
) -> Optional[PolicyFieldMatch]:
    if detect_policy_field_question(question) is None:
        return None

    if not _question_has_policy_context(question, retrieved):
        return None

    best_doc = _best_matching_doc(question, retrieved)
    if best_doc:
        same_doc_retrieved = [c for c in retrieved if _norm_rel_path(c.rel_path) == _norm_rel_path(best_doc)]
        if same_doc_retrieved:
            doc_first = extract_policy_field(question=question, chunks=same_doc_retrieved)
            if doc_first is not None:
                return doc_first

        doc_chunks = retriever.get_document_chunks(best_doc)
        if doc_chunks:
            doc_scan = extract_policy_field(question=question, chunks=doc_chunks)
            if doc_scan is not None:
                return doc_scan

    # Fallback when document mention is unclear: use retrieved set.
    return extract_policy_field(question=question, chunks=retrieved)


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

        # Fallback for in-domain policy questions where retrieval is concentrated
        # on a single document but strict grading is inconclusive.
        if _heuristic_retrieval_relevant(question=question, retrieved=retrieved):
            retrieval_relevant = True
            grade_reason = "heuristic relevance fallback (in-domain concentrated retrieval)"
            grade_supporting_labels = [
                f"{c.rel_path}:{c.start_line}-{c.end_line}"
                for c in retrieved[:2]
                if c.rel_path and c.start_line > 0 and c.end_line > 0
            ]
            final_query = query
            break

        # Not relevant: rewrite query for the next attempt
        rewritten = grade.suggested_rewrite.strip() or llm.rewrite_query(question)
        if debug:
            print(f"\n[Agent] Retrieval not good enough. Rewriting query to: {rewritten}")
        query = rewritten
        final_query = query

    if (not retrieval_relevant) and _question_has_policy_context(question, retrieved):
        best_doc = _best_matching_doc(question, retrieved)
        if best_doc:
            doc_chunks = retriever.get_document_chunks(best_doc)
            if doc_chunks:
                # For policy questions, scan the full best-matching document
                # (bounded) before refusing.
                retrieved = doc_chunks[: max(cfg.top_k, 12)]
                retrieval_relevant = True
                grade_reason = f"document-scan fallback ({best_doc})"
                grade_supporting_labels = [
                    f"{c.rel_path}:{c.start_line}-{c.end_line}"
                    for c in retrieved[:2]
                    if c.rel_path and c.start_line > 0 and c.end_line > 0
                ]

                if deterministic_match is None:
                    deterministic_match = _extract_policy_field_with_doc_scan(
                        question=question,
                        retrieved=retrieved,
                        retriever=retriever,
                    )
                    if deterministic_match is not None:
                        grade_supporting_labels = [deterministic_match.label]

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
