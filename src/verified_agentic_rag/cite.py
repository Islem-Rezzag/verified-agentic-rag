from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Set, Tuple

from .retrieve import RetrievedChunk


_CITATION_RE = re.compile(r"\[([^\[\]\n]+?:\d+-\d+)\]")


def make_label(rel_path: str, start_line: int, end_line: int) -> str:
    """
    Create the citation label used inside brackets.

    Example label:
    docs/intro.md:120-180

    In the answer text it becomes:
    [docs/intro.md:120-180]
    """
    rel_path = rel_path.replace("\\", "/")
    return f"{rel_path}:{start_line}-{end_line}"


def label_to_bracket(label: str) -> str:
    return f"[{label}]"


def parse_labels_from_text(text: str) -> List[str]:
    """
    Extract all citation labels from answer text.

    We look for patterns like:
    [path/to/file:10-30]
    """
    return _CITATION_RE.findall(text or "")


def allowed_labels_from_chunks(chunks: Iterable[RetrievedChunk]) -> Set[str]:
    """
    Build the set of valid labels from retrieved chunks.
    """
    return {make_label(c.rel_path, c.start_line, c.end_line) for c in chunks}


def format_sources_for_prompt(chunks: List[RetrievedChunk], max_chars_per_chunk: int = 1200) -> str:
    """
    Convert retrieved chunks into a text block that the LLM sees.

    Why:
    - LLM needs both the chunk text and the correct citation label to copy.
    - We limit length to reduce token usage.
    """
    parts: List[str] = []
    for c in chunks:
        label = make_label(c.rel_path, c.start_line, c.end_line)
        text = c.text
        if len(text) > max_chars_per_chunk:
            text = text[:max_chars_per_chunk] + "\n...[TRUNCATED]..."
        parts.append(f"[{label}]\n{text}")
    return "\n\n".join(parts)


def validate_citations(answer_text: str, allowed: Set[str]) -> Tuple[bool, List[str]]:
    """
    Returns:
    - (all_valid, invalid_labels)
    """
    labels = parse_labels_from_text(answer_text)
    invalid = [lab for lab in labels if lab not in allowed]
    return (len(invalid) == 0, invalid)
