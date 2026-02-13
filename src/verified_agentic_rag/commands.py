from __future__ import annotations

import argparse

from .agentic import ask_question
from .config import AppConfig
from .evals import run_eval_gold_silver
from .index import VectorIndex
from .ingest import count_files, ingest
from .report_figures import generate_result_figures


def ingest_main() -> None:
    parser = argparse.ArgumentParser(description="Build or refresh the local vector index.")
    parser.add_argument("--reset", action="store_true", help="Reset the collection before indexing")
    parser.add_argument("--scope", choices=["docs", "full"], default="", help="Override ingest scope")
    args = parser.parse_args()

    cfg = AppConfig()
    if args.scope:
        object.__setattr__(cfg, "scope", args.scope)
    cfg.ensure_dirs()

    idx = VectorIndex(cfg.persist_dir, cfg.collection_name, cfg.embedding_model)
    if args.reset:
        print(f"Resetting collection: {cfg.collection_name}")
        idx.reset_collection()

    print(f"Indexing from: {cfg.repo_path} (scope={cfg.scope})")
    print(f"Files to scan (estimate): {count_files(cfg)}")
    total = idx.upsert_chunks(ingest(cfg), batch_size=64)
    print(f"Done. Stored chunks: {total}")


def chat_main() -> None:
    parser = argparse.ArgumentParser(description="Ask one question to the agent.")
    parser.add_argument("question", help="Question to ask")
    parser.add_argument("--debug", action="store_true", help="Print debug retrieval details")
    parser.add_argument("--no-llm", action="store_true", help="Retrieval-only mode")
    args = parser.parse_args()

    run = ask_question(AppConfig(), question=args.question, debug=args.debug, no_llm=args.no_llm)
    print(run.answer.model_dump_json(indent=2))


def eval_main() -> None:
    parser = argparse.ArgumentParser(description="Run the gold/silver evaluation suite.")
    parser.add_argument("--mode", choices=["full", "retrieval"], default="full")
    parser.add_argument("--gold-path", default="evalset/gold.jsonl")
    parser.add_argument("--silver-path", default="evalset/silver.jsonl")
    parser.add_argument("--output-path", default="data/eval_results_suite.json")
    args = parser.parse_args()

    run_eval_gold_silver(
        mode=args.mode,
        gold_path=args.gold_path,
        silver_path=args.silver_path,
        output_path=args.output_path,
    )


def report_main() -> None:
    parser = argparse.ArgumentParser(description="Generate result figures from question-level CSV.")
    parser.add_argument("--csv-path", default="data/reports/full_system_eval_question_results_20260212.csv")
    parser.add_argument("--output-dir", default="reports/figures")
    args = parser.parse_args()

    out = generate_result_figures(csv_path=args.csv_path, output_dir=args.output_dir)
    for p in out:
        print(f"Wrote: {p}")
