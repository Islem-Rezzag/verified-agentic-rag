from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Literal


@dataclass(frozen=True)
class Chunk:
    """
    One retrievable unit.

    Beginner note:
    - We keep chunk metadata (path + line range) so we can cite it later.
    """
    chunk_id: str
    text: str
    rel_path: str
    start_line: int
    end_line: int
    source: str
    chunk_type: Literal["header", "body"]


def read_file_lines(path: Path) -> List[str]:
    """
    Read a text file safely.

    Beginner note:
    - encoding errors happen in real repos.
    - errors="ignore" prevents crashes.
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.readlines()


def chunk_lines(
    *,
    lines: List[str],
    rel_path: str,
    source: str,
    chunk_size_lines: int,
    overlap_lines: int,
    header_chunk_lines: int = 0,
) -> Iterable[Chunk]:
    """
    Split file lines into metadata-first chunks.

    Strategy:
    - Optional single "header" chunk from the first N lines.
    - Existing overlapping sliding-window "body" chunks across the full file.

    Example:
    - chunk_size_lines = 120
    - overlap_lines = 20

    That means:
    chunk1 = lines 1..120
    chunk2 = lines 101..220  (overlap 20 lines: 101-120 are shared)
    """

    if chunk_size_lines <= 0:
        raise ValueError("chunk_size_lines must be > 0")
    if overlap_lines < 0 or overlap_lines >= chunk_size_lines:
        raise ValueError("overlap_lines must be >= 0 and < chunk_size_lines")
    if header_chunk_lines < 0:
        raise ValueError("header_chunk_lines must be >= 0")

    n = len(lines)
    start = 0
    body_idx = 0

    if n == 0:
        return

    if header_chunk_lines > 0:
        header_end = min(n, header_chunk_lines)
        header_text = "".join(lines[:header_end])
        header_chunk_id = f"{source}:{rel_path}:header:1-{header_end}:0"
        yield Chunk(
            chunk_id=header_chunk_id,
            text=header_text,
            rel_path=rel_path,
            start_line=1,
            end_line=header_end,
            source=source,
            chunk_type="header",
        )

    while start < n:
        end = min(n, start + chunk_size_lines)
        text = "".join(lines[start:end])

        # A stable chunk_id so re-indexing creates the same ids.
        chunk_id = f"{source}:{rel_path}:body:{start+1}-{end}:{body_idx}"

        yield Chunk(
            chunk_id=chunk_id,
            text=text,
            rel_path=rel_path,
            start_line=start + 1,
            end_line=end,
            source=source,
            chunk_type="body",
        )

        body_idx += 1
        if end == n:
            break

        # Next start overlaps the previous chunk by overlap_lines.
        start = max(0, end - overlap_lines)
