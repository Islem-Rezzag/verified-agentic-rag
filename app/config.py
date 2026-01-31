from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Tuple

from dotenv import load_dotenv

# Loads variables from .env into os.environ
load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    """
    Central place for settings.

    Beginner note:
    - We keep settings in one class so every file can read consistent values.
    - Values can be overridden using environment variables (from .env).
    """

    # Source (your local corpus)
    source_name: str = os.getenv("RAG_SOURCE_NAME", "crewai")
    repo_path: Path = Path(os.getenv("RAG_REPO_PATH", "data/source_repos/crewai"))

    # Where Chroma (vector database) is stored on disk
    persist_dir: Path = Path(os.getenv("RAG_PERSIST_DIR", "data/vector_store"))
    collection_name: str = os.getenv("RAG_COLLECTION_NAME", "crewai_docs")

    # "docs" = only index README.md + docs/
    # "full" = also index code folders (lib/)
    scope: Literal["docs", "full"] = os.getenv("RAG_SCOPE", "docs")  # type: ignore[assignment]

    # File filtering
    include_exts: Tuple[str, ...] = (".md", ".mdx", ".rst", ".txt", ".py")
    exclude_dirs: Tuple[str, ...] = (
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
        ".pytest_cache",
        ".mypy_cache",
    )
    max_file_size_bytes: int = int(os.getenv("RAG_MAX_FILE_SIZE_BYTES", str(1_000_000)))  # 1 MB default

    # Chunking (line-based)
    chunk_size_lines: int = int(os.getenv("RAG_CHUNK_SIZE_LINES", "120"))
    overlap_lines: int = int(os.getenv("RAG_OVERLAP_LINES", "20"))

    # Embeddings
    embedding_model: str = os.getenv("RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # Retrieval
    top_k: int = int(os.getenv("RAG_TOP_K", "6"))

    # Agentic loop settings
    agentic_max_rounds: int = int(os.getenv("RAG_AGENTIC_MAX_ROUNDS", "2"))

    # LLM settings
    llm_provider: Literal["openai", "none"] = os.getenv("RAG_LLM_PROVIDER", "openai")  # type: ignore[assignment]
    openai_model: str = os.getenv("OPENAI_MODEL", "")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))

    # Logs
    logs_dir: Path = Path(os.getenv("RAG_LOGS_DIR", "data/logs"))

    def ensure_dirs(self) -> None:
        """
        Create directories that must exist.
        """
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
