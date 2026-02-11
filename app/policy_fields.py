from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern, Tuple

from .cite import make_label
from .retrieve import RetrievedChunk


@dataclass(frozen=True)
class PolicyFieldMatch:
    field_key: str
    field_name: str
    value: str
    label: str
    chunk: RetrievedChunk


FIELD_DEFS: Dict[str, Dict[str, object]] = {
    "responsible_committee": {
        "name": "responsible committee",
        "question_patterns": [
            r"\bresponsible committee\b",
            r"\bcommittee\b.*\bresponsible\b",
        ],
        "value_patterns": [
            r"responsible committee\s*[:\-]\s*([A-Za-z0-9&/,\- ]{2,120})",
        ],
    },
    "policy_group": {
        "name": "policy group",
        "question_patterns": [
            r"\bpolicy group\b",
        ],
        "value_patterns": [
            r"policy group\s*[:\-]\s*([A-Za-z0-9&/,\- ]{2,120})",
        ],
    },
    "last_updated": {
        "name": "last updated",
        "question_patterns": [
            r"\blast updated\b",
            r"\bdate updated\b",
        ],
        "value_patterns": [
            r"(?:last updated|date updated)\s*[:\-]?\s*([A-Za-z0-9./,\- ]{2,120})",
        ],
    },
    "review_date": {
        "name": "review date",
        "question_patterns": [
            r"\bnext review date\b",
            r"\breview date\b",
            r"\bcurrent document review date\b",
        ],
        "value_patterns": [
            r"(?:next review date|review date|current document review date)\s*[:\-]?\s*([A-Za-z0-9./,\- ]{2,120})",
        ],
    },
    "review_frequency": {
        "name": "review frequency",
        "question_patterns": [
            r"\breview frequency\b",
            r"\bfrequency\b.*\breview\b",
            r"\bhow often\b.*\breview\b",
        ],
        "value_patterns": [
            r"(annual(?:ly)?(?:\s+or\s+if\s+required\s+by\s+legislation)?)",
            r"(?:review frequency)\s*[:\-]?\s*([A-Za-z0-9./,\- ]{2,120})",
        ],
    },
}


def _clean_value(raw: str) -> str:
    val = re.sub(r"\s+", " ", (raw or "").strip())
    val = val.strip(" :;,-")
    return val


def detect_policy_field_question(question: str) -> Optional[Tuple[str, str]]:
    q = (question or "").lower()
    for key, meta in FIELD_DEFS.items():
        patterns = meta["question_patterns"]  # type: ignore[index]
        if any(re.search(pat, q, flags=re.IGNORECASE) for pat in patterns):
            return key, str(meta["name"])  # type: ignore[index]
    return None


def extract_field_from_text(field_key: str, text: str) -> Optional[str]:
    meta = FIELD_DEFS.get(field_key)
    if not meta:
        return None

    value_patterns = meta["value_patterns"]  # type: ignore[index]
    for pat in value_patterns:
        m = re.search(pat, text or "", flags=re.IGNORECASE)
        if not m:
            continue
        value = _clean_value(m.group(1))
        if value:
            return value
    return None


def extract_policy_field(question: str, chunks: List[RetrievedChunk]) -> Optional[PolicyFieldMatch]:
    field = detect_policy_field_question(question)
    if field is None:
        return None

    field_key, field_name = field

    # Prefer header chunks first, then by retrieval order.
    ordered = sorted(chunks, key=lambda c: (0 if c.chunk_type == "header" else 1))
    for chunk in ordered:
        value = extract_field_from_text(field_key, chunk.text)
        if not value:
            continue
        label = make_label(chunk.rel_path, chunk.start_line, chunk.end_line)
        return PolicyFieldMatch(
            field_key=field_key,
            field_name=field_name,
            value=value,
            label=label,
            chunk=chunk,
        )
    return None


def format_extracted_answer(question: str, match: PolicyFieldMatch) -> str:
    q = (question or "").lower()
    if "what" in q or "which" in q:
        return f"The {match.field_name} is {match.value}.[{match.label}]"
    return f"{match.value}.[{match.label}]"
