from __future__ import annotations

from pathlib import Path
import typer

from .config import AppConfig
from .index import VectorIndex
from .ingest import ingest, count_files
from .agentic import ask_question

app = typer.Typer(add_completion=False)


@app.command()
def ingest_cmd(
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

    chunks_iter = ingest(cfg)
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


if __name__ == "__main__":
    app()
