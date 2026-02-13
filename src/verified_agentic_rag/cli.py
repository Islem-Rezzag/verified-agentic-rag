from __future__ import annotations

import typer

from .config import AppConfig
from .index import VectorIndex
from .ingest import count_files, ingest as ingest_chunks
from .agentic import ask_question
from .evals import run_eval_gold_silver
from .report_figures import generate_result_figures

app = typer.Typer(add_completion=False)


@app.command("ingest")
def ingest_command(
    reset: bool = typer.Option(False, help="Delete and rebuild the collection"),
    scope: str = typer.Option("", help='Override scope: "docs" or "full"'),
):
    """
    Build the vector index from your local repo corpus.
    """
    cfg = AppConfig()
    if scope:
        object.__setattr__(cfg, "scope", scope)  # frozen dataclass workaround

    cfg.ensure_dirs()

    idx = VectorIndex(cfg.persist_dir, cfg.collection_name, cfg.embedding_model)
    if reset:
        typer.echo(f"Resetting collection: {cfg.collection_name}")
        idx.reset_collection()

    typer.echo(f"Indexing from: {cfg.repo_path}  (scope={cfg.scope})")
    typer.echo(f"Files to scan (estimate): {count_files(cfg)}")

    chunks_iter = ingest_chunks(cfg)
    total = idx.upsert_chunks(chunks_iter, batch_size=64)

    typer.echo(f"Done. Stored chunks: {total}")
    typer.echo(f"Vector store directory: {cfg.persist_dir}")


@app.command()
def ask(
    question: str = typer.Argument(..., help="User question"),
    debug: bool = typer.Option(False, help="Print retrieved chunks and agent decisions"),
    no_llm: bool = typer.Option(False, help="Retrieval-only mode (no OpenAI calls)"),
):
    """
    Ask a question to the agentic RAG system.
    """
    cfg = AppConfig()
    run = ask_question(cfg, question=question, debug=debug, no_llm=no_llm)

    typer.echo("\n=== Answer (JSON) ===")
    typer.echo(run.answer.model_dump_json(indent=2))

    if no_llm:
        typer.echo("\n=== Retrieved sources ===")
        for c in run.retrieved:
            typer.echo(f"- {c.rel_path}:{c.start_line}-{c.end_line}  sim={c.similarity:.3f}")


@app.command()
def eval_suite(
    mode: str = typer.Option("full", help="Eval mode: full or retrieval"),
    output_path: str = typer.Option("data/eval_results_suite.json", help="Output JSON path"),
    gold_path: str = typer.Option("evalset/gold.jsonl", help="Gold evalset JSONL path"),
    silver_path: str = typer.Option("evalset/silver.jsonl", help="Silver evalset JSONL path"),
):
    """
    Run the gold/silver evaluation suite.
    """
    run_eval_gold_silver(
        gold_path=gold_path,
        silver_path=silver_path,
        output_path=output_path,
        mode=mode,
    )
    typer.echo(f"Wrote eval suite: {output_path}")


@app.command()
def report_figures(
    csv_path: str = typer.Option(
        "data/reports/full_system_eval_question_results_20260212.csv",
        help="Question-level CSV to visualize",
    ),
    output_dir: str = typer.Option("reports/figures", help="Directory for PNG figures"),
):
    """
    Generate showcase charts from question-level evaluation CSV.
    """
    paths = generate_result_figures(csv_path=csv_path, output_dir=output_dir)
    for p in paths:
        typer.echo(f"Wrote: {p}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
