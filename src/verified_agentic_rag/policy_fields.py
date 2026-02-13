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
            r"\bwhich committee\b",
            r"\bcommittee\b.*\b(owns|oversees|accountable)\b",
        ],
        "value_patterns": [
            r"responsible committee\s*[:\-]\s*([A-Za-z0-9&/,\- ]{2,120})",
        ],
    },
    "policy_group": {
        "name": "policy group",
        "question_patterns": [
            r"\bpolicy group\b",
            r"\bwhich group\b.*\bpolicy\b",
            r"\bwho\b.*\bpolicy\b.*\bapply\b",
            r"\baudience\b",
        ],
        "value_patterns": [
            r"policy group\s*[:\-]\s*([A-Za-z0-9&/,\- ]{2,120})",
        ],
    },
    "responsible_officer": {
        "name": "responsible officer",
        "question_patterns": [
            r"\bresponsible officer\b",
            r"\bwhich officer\b.*\bresponsible\b",
            r"\bofficer\b.*\bpolicy\b",
        ],
        "value_patterns": [
            r"responsible\s+officer\s*[:\-]?\s*([A-Za-z0-9&/.,\- ]{1,120})",
        ],
    },
    "approved_by": {
        "name": "approved by",
        "question_patterns": [
            r"\bapproved by\b",
            r"\bapprov(?:ed|ing)\b.*\b(body|committee|group)\b",
            r"\bwho approved\b",
        ],
        "value_patterns": [
            r"approved\s+by\s*[:\-]?\s*([A-Za-z0-9&/.,\- ]{1,120})",
        ],
    },
    "version": {
        "name": "version",
        "question_patterns": [
            r"\bwhat is the version\b",
            r"\bcurrent version\b",
            r"\bversion\b",
        ],
        "value_patterns": [
            r"\bversion\s*[:\-]?\s*([A-Za-z0-9./,\-]{2,40})",
        ],
    },
    "last_updated": {
        "name": "last updated",
        "question_patterns": [
            r"\blast updated\b",
            r"\bdate updated\b",
            r"\bwhen was\b.*\bupdated\b",
            r"\bwhat date\b.*\bupdated\b",
            r"\bwhat date\b.*\bcurrent document status\b",
            r"\bdate\b.*\brecorded\b",
        ],
        "value_patterns": [
            r"(?:last updated|date updated)\s*[:\-]?\s*([A-Za-z0-9./,\- ]{2,120})",
            r"\bdate\s*[:\-]?\s*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})\b",
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
            r"\bnext review\b",
            r"\breview timing\b",
            r"\bnext review due\b",
        ],
        "value_patterns": [
            r"(annual(?:ly)?\s+or\s+(?:as|if)\s+required(?:\s+by\s+legislation)?)",
            r"(?:review frequency)\s*[:\-]?\s*([A-Za-z0-9./,\- ]{2,120})",
        ],
    },
    "minute_no": {
        "name": "minute number",
        "question_patterns": [
            r"\bminute\s+no\b",
            r"\bminute\s+number\b",
        ],
        "value_patterns": [
            r"minute\s+no\.?\s*[:\-]?\s*([A-Za-z0-9/().,\-]{2,80})",
        ],
    },
    "document_retention_period": {
        "name": "document retention period",
        "question_patterns": [
            r"\bdocument retention\b",
            r"\bretention period\b",
            r"\bhow long\b.*\bretain\b",
            r"\bhow long\b.*\bkept\b",
        ],
        "value_patterns": [
            r"document\s+retention\s+period\s*[:\-]?\s*([A-Za-z0-9&/.,\- ]{2,120})",
        ],
    },
}


def _clean_value(raw: str) -> str:
    val = re.sub(r"\s+", " ", (raw or "").strip())
    val = val.strip(" :;,-")
    return val


def _normalize_table_noise(text: str) -> str:
    compact = re.sub(r"\s+", " ", (text or "").strip())
    # PDF table extraction can interleave column headers into values.
    compact = re.sub(
        r"(?i)\bminute\s+no\.?\s+next\s+review\s+date\b",
        "next review date",
        compact,
    )
    compact = re.sub(
        r"(?i)\bdate\s+[0-9./-]{4,20}\s+responsible\s+officer\b",
        "date responsible officer",
        compact,
    )
    return compact


def _extract_review_frequency_value(text: str) -> Optional[str]:
    compact = _normalize_table_noise(text)
    lower = compact.lower()

    # Handles interleaved table text such as:
    # "Annual or if Minute no. Next review date required by legislation"
    noisy = re.search(
        r"(?i)\bannual(?:ly)?\s+or\s+(if|as)(?:\s+(?:minute|no\.?|next|review|date|[0-9/().:-]+)){0,24}\s+required\s+by\s+legislation\b",
        compact,
    )
    if noisy:
        qualifier = noisy.group(1).lower()
        return f"Annual or {qualifier} required by legislation"

    direct_leg = re.search(
        r"(?i)\bannual(?:ly)?\s+or\s+(if|as)\s+required\s+by\s+legislation\b",
        compact,
    )
    if direct_leg:
        qualifier = direct_leg.group(1).lower()
        return f"Annual or {qualifier} required by legislation"

    direct = re.search(r"(?i)\bannual(?:ly)?\s+or\s+(if|as)\s+required\b", compact)
    if direct:
        qualifier = direct.group(1).lower()
        return f"Annual or {qualifier} required"

    # Conservative fallback for explicit labeled values.
    labeled = re.search(r"(?i)\breview\s+frequency\s*[:\-]?\s*(annual(?:ly)?)\b", compact)
    if labeled:
        val = labeled.group(1).lower()
        return "Annually" if val.startswith("annual") and val.endswith("ly") else "Annual"

    if "next review date" in lower:
        # If next review date exists but a full value phrase is missing, avoid
        # returning a weak single-token match like "Annual".
        return None

    return None


def _extract_responsible_officer_value(text: str) -> Optional[str]:
    compact = _normalize_table_noise(text)
    m = re.search(
        r"(?i)responsible\s+officer\s*[:\-]?\s*([A-Za-z][A-Za-z0-9/().,\- ]{0,80})",
        compact,
    )
    if not m:
        return None
    value = _clean_value(m.group(1))
    # Remove trailing table labels that may bleed into extraction.
    value = re.split(
        r"(?i)\b(next review date|minute no\.?|version history|document retention)\b",
        value,
        maxsplit=1,
    )[0].strip(" :;,-")
    return value or None


def _extract_approved_by_value(text: str) -> Optional[str]:
    compact = _normalize_table_noise(text)
    m = re.search(r"(?i)approved\s+by\s*[:\-]?\s*([A-Za-z0-9&/().,\- ]{1,60})", compact)
    if not m:
        return None
    value = _clean_value(m.group(1))
    value = re.split(
        r"(?i)\b(date|responsible officer|minute no\.?|next review date)\b",
        value,
        maxsplit=1,
    )[0].strip(" :;,-")
    return value or None


def _extract_version_value(text: str) -> Optional[str]:
    compact = _normalize_table_noise(text)
    m = re.search(r"(?i)\bversion\s*[:\-]?\s*([0-9]{2,4}(?:/[0-9]{2,4})?(?:\.[0-9]+)?)", compact)
    if not m:
        return None
    return _clean_value(m.group(1)) or None


def _extract_minute_no_value(text: str) -> Optional[str]:
    compact = _normalize_table_noise(text)
    m = re.search(r"(?i)\bminute\s+no\.?\s*[:\-]?\s*([A-Za-z0-9/().,\-]{2,80})", compact)
    if not m:
        return None
    value = _clean_value(m.group(1))
    value = re.split(
        r"(?i)\b(next review date|version history|document retention)\b",
        value,
        maxsplit=1,
    )[0].strip(" :;,-")
    return value or None


def _extract_document_retention_value(text: str) -> Optional[str]:
    compact = _normalize_table_noise(text)
    m = re.search(
        r"(?is)\bdocument\s+retention\s+period\s*[:\-]?\s*([A-Za-z0-9&/().,\- ]{2,120})",
        compact,
    )
    if not m:
        return None
    value = _clean_value(m.group(1))
    value = re.split(
        r"(?i)\b(page|version history|current document status)\b",
        value,
        maxsplit=1,
    )[0].strip(" :;,-")
    return value or None


def detect_policy_field_question(question: str) -> Optional[Tuple[str, str]]:
    q = (question or "").lower()
    # Prefer frequency guidance extraction when both "review frequency" and
    # "next review date" appear in the same question.
    if re.search(r"\breview frequency\b", q, flags=re.IGNORECASE) or re.search(
        r"\bnext review date guidance\b",
        q,
        flags=re.IGNORECASE,
    ):
        meta = FIELD_DEFS["review_frequency"]
        return "review_frequency", str(meta["name"])

    for key, meta in FIELD_DEFS.items():
        patterns = meta["question_patterns"]  # type: ignore[index]
        if any(re.search(pat, q, flags=re.IGNORECASE) for pat in patterns):
            return key, str(meta["name"])  # type: ignore[index]
    return None


def extract_field_from_text(field_key: str, text: str) -> Optional[str]:
    meta = FIELD_DEFS.get(field_key)
    if not meta:
        return None

    if field_key == "review_frequency":
        normalized = _extract_review_frequency_value(text)
        if normalized:
            return normalized
    elif field_key == "responsible_officer":
        normalized = _extract_responsible_officer_value(text)
        if normalized:
            return normalized
    elif field_key == "approved_by":
        normalized = _extract_approved_by_value(text)
        if normalized:
            return normalized
    elif field_key == "version":
        normalized = _extract_version_value(text)
        if normalized:
            return normalized
    elif field_key == "minute_no":
        normalized = _extract_minute_no_value(text)
        if normalized:
            return normalized
    elif field_key == "document_retention_period":
        normalized = _extract_document_retention_value(text)
        if normalized:
            return normalized

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
