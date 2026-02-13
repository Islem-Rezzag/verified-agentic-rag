from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .cite import make_label, parse_labels_from_text
from .policy_fields import detect_policy_field_question, extract_field_from_text
from .retrieve import RetrievedChunk

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "this",
    "that",
    "these",
    "those",
    "policy",
    "document",
    "employees",
    "employee",
    "members",
    "member",
    "council",
    "town",
    "is",
    "are",
    "was",
    "were",
    "be",
    "to",
    "of",
    "in",
    "on",
    "at",
    "or",
    "an",
    "a",
}


@dataclass(frozen=True)
class SentenceVerification:
    sentence: str
    citations: List[str]
    supported: bool
    reason: str


@dataclass(frozen=True)
class VerificationResult:
    all_supported: bool
    checks: List[SentenceVerification]

    @property
    def unsupported_sentences(self) -> List[str]:
        return [c.sentence for c in self.checks if not c.supported]


def _split_sentences(text: str) -> List[str]:
    raw = text or ""
    parts = re.split(r"(?<=[.!?])\s+|\n+", raw)
    out: List[str] = []
    for p in parts:
        s = p.strip()
        if s:
            out.append(s)
    return out


def _strip_citations(text: str) -> str:
    return re.sub(r"\[[^\[\]\n]+?:\d+-\d+\]", "", text).strip()


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]{2,}", (text or "").lower())


def _keyword_tokens(text: str) -> List[str]:
    return [t for t in _tokens(text) if t not in STOPWORDS]


def _keyword_supported(sentence_plain: str, cited_text: str) -> bool:
    claim_tokens = _keyword_tokens(sentence_plain)
    if not claim_tokens:
        return True

    cited_l = (cited_text or "").lower()
    hits = [t for t in claim_tokens if t in cited_l]
    ratio = len(hits) / max(1, len(claim_tokens))

    numeric = re.findall(r"\d[\d./-]*", sentence_plain)
    numeric_ok = all(n in cited_l for n in numeric) if numeric else True

    return numeric_ok and (ratio >= 0.35 or len(hits) >= 3)


def _metadata_supported(
    field_key: str,
    sentence_plain: str,
    cited_chunks: List[RetrievedChunk],
) -> bool:
    sent_l = " ".join(_tokens(sentence_plain))
    for chunk in cited_chunks:
        extracted = extract_field_from_text(field_key, chunk.text)
        if not extracted:
            continue
        value_tokens = _tokens(extracted)
        if not value_tokens:
            continue
        if " ".join(value_tokens) in sent_l:
            return True
        if all(tok in sent_l for tok in value_tokens):
            return True
    return False


def verify_answer_grounding(
    *,
    question: str,
    answer_text: str,
    retrieved: List[RetrievedChunk],
    llm_claim_judge: Optional[Callable[[str, str, str], bool]] = None,
) -> VerificationResult:
    label_to_chunk: Dict[str, RetrievedChunk] = {
        make_label(c.rel_path, c.start_line, c.end_line): c for c in retrieved
    }
    field_match = detect_policy_field_question(question)
    field_key = field_match[0] if field_match else None

    checks: List[SentenceVerification] = []
    for sentence in _split_sentences(answer_text):
        plain = _strip_citations(sentence)
        labels = parse_labels_from_text(sentence)

        if not plain:
            continue

        if plain.lower().startswith("i cannot answer from the repository"):
            checks.append(
                SentenceVerification(
                    sentence=sentence,
                    citations=labels,
                    supported=True,
                    reason="refusal sentence",
                )
            )
            continue

        if not labels:
            checks.append(
                SentenceVerification(
                    sentence=sentence,
                    citations=[],
                    supported=False,
                    reason="missing citation for factual sentence",
                )
            )
            continue

        cited_chunks = [label_to_chunk[lab] for lab in labels if lab in label_to_chunk]
        if not cited_chunks:
            checks.append(
                SentenceVerification(
                    sentence=sentence,
                    citations=labels,
                    supported=False,
                    reason="citations not in retrieved context",
                )
            )
            continue

        cited_text = "\n".join(c.text for c in cited_chunks)

        supported = False
        reason = "low lexical overlap with cited text"
        if field_key and _metadata_supported(field_key, plain, cited_chunks):
            supported = True
            reason = "metadata field explicitly found in cited chunk"
        elif _keyword_supported(plain, cited_text):
            supported = True
            reason = "keyword overlap with cited text"
        elif llm_claim_judge is not None:
            # Optional strict fallback using LLM-as-judge.
            try:
                supported = bool(llm_claim_judge(question, plain, cited_text))
                reason = "llm groundedness judge"
            except Exception:
                supported = False
                reason = "llm judge failed"

        checks.append(
            SentenceVerification(
                sentence=sentence,
                citations=labels,
                supported=supported,
                reason=reason,
            )
        )

    return VerificationResult(all_supported=all(c.supported for c in checks), checks=checks)
