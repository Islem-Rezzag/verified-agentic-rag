from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple

from tqdm import tqdm

from .chunking import Chunk, chunk_lines, read_file_lines
from .config import AppConfig


def _is_excluded_dir(dir_name: str, exclude_dirs: Sequence[str]) -> bool:
    return dir_name in exclude_dirs


def iter_source_files(cfg: AppConfig) -> Iterator[Path]:
    """
    Yield file paths from the corpus based on cfg.scope.

    scope="docs":
      - repo_root/README.md
      - repo_root/docs/**

    scope="full":
      - README.md
      - docs/**
      - lib/**  (common location for python package code in crewai repo)
    """
    repo = cfg.repo_path

    allowed_roots: List[Path] = []

    readme = repo / "README.md"
    if readme.exists():
        allowed_roots.append(readme)

    docs_root = repo / "docs"
    if docs_root.exists():
        allowed_roots.append(docs_root)

    if cfg.scope == "full":
        lib_root = repo / "lib"
        if lib_root.exists():
            allowed_roots.append(lib_root)

    for root in allowed_roots:
        if root.is_file():
            yield root
            continue

        for dirpath, dirnames, filenames in os.walk(root):
            # prune excluded dirs
            dirnames[:] = [d for d in dirnames if not _is_excluded_dir(d, cfg.exclude_dirs)]
            for fn in filenames:
                p = Path(dirpath) / fn

                if p.suffix.lower() not in cfg.include_exts:
                    continue
                if p.stat().st_size > cfg.max_file_size_bytes:
                    continue
                yield p


def iter_chunks_from_files(cfg: AppConfig, files: Iterable[Path]) -> Iterator[Chunk]:
    """
    Read each file and yield line-based chunks with metadata.
    """
    repo = cfg.repo_path

    for p in files:
        try:
            rel = str(p.relative_to(repo)).replace("\\", "/")
        except Exception:
            rel = str(p).replace("\\", "/")

        lines = read_file_lines(p)
        yield from chunk_lines(
            lines=lines,
            rel_path=rel,
            source=cfg.source_name,
            chunk_size_lines=cfg.chunk_size_lines,
            overlap_lines=cfg.overlap_lines,
        )


def ingest(cfg: AppConfig) -> Iterator[Chunk]:
    """
    Main ingest generator.

    Returns an iterator of Chunk objects.
    """
    files = list(iter_source_files(cfg))
    for ch in iter_chunks_from_files(cfg, files):
        yield ch


def count_files(cfg: AppConfig) -> int:
    return sum(1 for _ in iter_source_files(cfg))
