from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .config import AppConfig
from .index import VectorIndex
from .retrieve import Retriever, RetrievedChunk
from .generate import LLMClient, AnswerOut
from .cite import allowed_labels_from_chunks, validate_citations


@dataclass
class AgentRun:
    question: str
    final_query_used: str
    attempts: int
    retrieved: List[RetrievedChunk]
    answer: AnswerOut
    retrieval_grade_reason: str = ""


def _now_ts() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def _hash_question(q: str) -> str:
    return hashlib.sha1(q.encode("utf-8")).hexdigest()[:10]


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
    retriever = Retriever(index=index)

    retrieved: List[RetrievedChunk] = []
    final_query = question
    attempts = 0
    grade_reason = ""
    retrieval_relevant = False

    if no_llm:
        # Retrieval-only mode: useful before you have an API key.
        retrieved = retriever.retrieve(query=question, top_k=cfg.top_k)
        dummy = AnswerOut(
            answer="LLM disabled. Showing retrieved sources only.",
            citations=[],
            confidence="low",
            cannot_answer=True,
            follow_ups=[],
        )
        run = AgentRun(
            question=question,
            final_query_used=question,
            attempts=1,
            retrieved=retrieved,
            answer=dummy,
            retrieval_grade_reason="LLM disabled",
        )
        _log_run(cfg, run)
        return run

    llm = LLMClient(cfg)

    # Agentic loop: at most cfg.agentic_max_rounds retrieval attempts
    query = question
    for attempt in range(cfg.agentic_max_rounds):
        attempts += 1
        retrieved = retriever.retrieve(query=query, top_k=cfg.top_k)

        if debug:
            print("\n--- Retrieved chunks ---")
            for i, c in enumerate(retrieved, 1):
                print(f"{i}. {c.rel_path}:{c.start_line}-{c.end_line}  sim={c.similarity:.3f}")

        grade = llm.grade_retrieval(question=question, chunks=retrieved)
        grade_reason = grade.reason

        if grade.relevant:
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
        )
        run = AgentRun(
            question=question,
            final_query_used=final_query,
            attempts=attempts,
            retrieved=retrieved,
            answer=answer,
            retrieval_grade_reason=grade_reason,
        )
        _log_run(cfg, run)
        return run

    # Generate answer using the best retrieved chunks.
    answer = llm.answer_with_citations(question=question, chunks=retrieved)

    # Validate citations one more time at orchestration layer
    allowed = allowed_labels_from_chunks(retrieved)
    all_valid, invalid = validate_citations(answer.answer, allowed)
    if debug and (not all_valid):
        print(f"\n[Warning] Invalid citations found: {invalid}")

    run = AgentRun(
        question=question,
        final_query_used=final_query,
        attempts=attempts,
        retrieved=retrieved,
        answer=answer,
        retrieval_grade_reason=grade_reason,
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
        "retrieved": [
            {
                "chunk_id": c.chunk_id,
                "rel_path": c.rel_path,
                "start_line": c.start_line,
                "end_line": c.end_line,
                "distance": c.distance,
                "similarity": c.similarity,
            }
            for c in run.retrieved
        ],
        "answer": run.answer.model_dump(),
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
