from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


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
) -> Iterable[Chunk]:
    """
    Split file lines into overlapping windows.

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

    n = len(lines)
    start = 0
    idx = 0

    while start < n:
        end = min(n, start + chunk_size_lines)
        text = "".join(lines[start:end])

        # A stable chunk_id so re-indexing creates the same ids.
        chunk_id = f"{source}:{rel_path}:{start+1}-{end}:{idx}"

        yield Chunk(
            chunk_id=chunk_id,
            text=text,
            rel_path=rel_path,
            start_line=start + 1,
            end_line=end,
            source=source,
        )

        idx += 1
        if end == n:
            break

        # Next start overlaps the previous chunk by overlap_lines.
        start = max(0, end - overlap_lines)
