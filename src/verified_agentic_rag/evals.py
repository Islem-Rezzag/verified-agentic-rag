from __future__ import annotations

import json
import math
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .agentic import ask_question
from .cite import parse_labels_from_text
from .config import AppConfig
from .ingest import iter_source_files

_CANONICAL_ALIAS_PATTERNS: List[Tuple[re.Pattern[str], str]] = [
    # Saltash policy pack committee naming variants.
    (re.compile(r"\bp\s*[/&]\s*f\b", flags=re.IGNORECASE), "personnel"),
    (re.compile(r"\bpersonnel\s*(?:and|&)?\s*finance\b", flags=re.IGNORECASE), "personnel"),
]


def load_questions(path: Path) -> List[Dict]:
    """
    JSONL format:
    - Legacy v1:
      {
        "question": "...",
        "expected": "answer"|"refuse",
        "expected_doc": "...",                   # optional
        "expected_value": "...",                 # optional
        "expected_value_regex": "..."            # optional
      }
    - Evidence-oriented v2:
      {
        "id": "q1",
        "question": "...",
        "expected_behavior": "answer"|"refuse",
        "question_type": "metadata"|"procedure"|"definition"|"multi_chunk"|"out_of_scope",
        "expected_answer": "..."|["fact1", "fact2"],   # optional
        "expected_answer_regex": "...",                # optional
        "required_phrases": ["...", "..."],           # optional
        "gold_evidence": [{"label":"docs/...:1-120","must_contain":["..."]}],
        "gold_evidence_labels": ["docs/...:1-120"],   # optional alias
        "acceptable_answers": ["..."],
        "normalization": "uppercase"|"strip_punct"|"date_iso"|["..."]
      }
    """
    items: List[Dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def _norm_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def _apply_alias_canonicalization(text: str) -> str:
    out = text or ""
    for pattern, replacement in _CANONICAL_ALIAS_PATTERNS:
        out = pattern.sub(replacement, out)
    return re.sub(r"\s+", " ", out).strip()


def _strip_inline_citations(text: str) -> str:
    return re.sub(r"\[[^\[\]\n]+?:\d+-\d+\]", "", text or "")


def _doc_matches_expected(rel_path: str, expected_doc: str) -> bool:
    if not expected_doc:
        return False

    rel = (rel_path or "").replace("\\", "/").lower()
    expected = expected_doc.replace("\\", "/").lower().strip()

    rel_name = Path(rel).name
    exp_name = Path(expected).name

    if rel_name == exp_name:
        return True
    if rel.endswith(expected):
        return True

    rel_stem = Path(rel_name).stem
    exp_stem = Path(exp_name).stem
    if rel_stem and exp_stem and rel_stem == exp_stem:
        return True

    return (exp_name in rel) or (exp_stem in rel)


def _value_matches(
    text: str,
    expected_value: Optional[str],
    expected_value_regex: Optional[str],
) -> Optional[bool]:
    if not expected_value and not expected_value_regex:
        return None

    exact_match = False
    regex_match = False
    if expected_value:
        exact_match = _norm_text(_apply_alias_canonicalization(expected_value)) in _norm_text(
            _apply_alias_canonicalization(text)
        )
    if expected_value_regex:
        try:
            regex_match = re.search(expected_value_regex, text or "", flags=re.IGNORECASE) is not None
        except re.error:
            regex_match = False
    return exact_match or regex_match


def _path_match(path_a: str, path_b: str) -> bool:
    a = (path_a or "").replace("\\", "/").lower().strip()
    b = (path_b or "").replace("\\", "/").lower().strip()
    if not a or not b:
        return False
    if a == b:
        return True
    if a.endswith(b) or b.endswith(a):
        return True

    name_a = Path(a).name
    name_b = Path(b).name
    stem_a = Path(name_a).stem
    stem_b = Path(name_b).stem
    return name_a == name_b or (stem_a and stem_b and stem_a == stem_b)


def _parse_label(label: str) -> Optional[Tuple[str, Optional[int], Optional[int]]]:
    raw = (label or "").strip().strip("[]")
    if not raw:
        return None

    m = re.match(r"^(.*?):(\d+)-(\d+)$", raw)
    if m:
        rel_path = m.group(1)
        start = int(m.group(2))
        end = int(m.group(3))
        if start > end:
            start, end = end, start
        return rel_path, start, end

    return raw, None, None


def _labels_overlap(label_a: str, label_b: str) -> bool:
    parsed_a = _parse_label(label_a)
    parsed_b = _parse_label(label_b)
    if parsed_a is None or parsed_b is None:
        return False

    path_a, start_a, end_a = parsed_a
    path_b, start_b, end_b = parsed_b

    if not _path_match(path_a, path_b):
        return False

    if start_a is None or end_a is None or start_b is None or end_b is None:
        return True

    return not (end_a < start_b or end_b < start_a)


def _normalize_date_tokens(text: str) -> str:
    out = text

    def _to_iso(match: re.Match[str]) -> str:
        d = int(match.group(1))
        m = int(match.group(2))
        y = int(match.group(3))
        if y < 100:
            y += 2000
        if not (1 <= d <= 31 and 1 <= m <= 12):
            return match.group(0)
        return f"{y:04d}-{m:02d}-{d:02d}"

    out = re.sub(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})\b", _to_iso, out)
    return out


def _apply_normalization(text: str, normalization: Optional[Any]) -> str:
    out = text or ""
    rules: List[str] = []
    if isinstance(normalization, str) and normalization.strip():
        rules = [normalization.strip()]
    elif isinstance(normalization, list):
        rules = [str(x).strip() for x in normalization if str(x).strip()]

    for rule in rules:
        if rule == "uppercase":
            out = out.upper()
        elif rule == "strip_punct":
            out = re.sub(r"[^\w\s/.-]+", " ", out)
        elif rule == "date_iso":
            out = _normalize_date_tokens(out)

    out = _apply_alias_canonicalization(out)
    return re.sub(r"\s+", " ", out).strip()


def _extract_gold_labels(item: Dict[str, Any]) -> List[str]:
    labels: List[str] = []
    for ev in item.get("gold_evidence", []) or []:
        if isinstance(ev, str) and ev.strip():
            labels.append(ev.strip())
            continue
        if isinstance(ev, dict):
            lab = str(ev.get("label", "")).strip()
            if lab:
                labels.append(lab)
    for lab in item.get("gold_evidence_labels", []) or []:
        if isinstance(lab, str) and lab.strip():
            labels.append(lab.strip())

    # Legacy fallback (document-level signal when exact spans are absent).
    expected_doc_raw = item.get("expected_doc")
    expected_doc = expected_doc_raw.strip() if isinstance(expected_doc_raw, str) else ""
    if expected_doc and not labels:
        labels.append(expected_doc)

    return labels


def _evidence_metrics(retrieved_labels: Sequence[str], gold_labels: Sequence[str]) -> Dict[str, Optional[float]]:
    if not gold_labels:
        return {
            "evidence_recall_at_k": None,
            "evidence_mrr": None,
            "context_precision_ranked": None,
            "evidence_ndcg_at_k": None,
            "evidence_coverage": None,
        }

    rel_any = [any(_labels_overlap(lab, gold) for gold in gold_labels) for lab in retrieved_labels]
    hit_positions = [i + 1 for i, is_rel in enumerate(rel_any) if is_rel]

    # For ranking-based metrics, count at most one hit per gold evidence label.
    rel_unique: List[bool] = []
    matched_gold_idx: set[int] = set()
    for lab in retrieved_labels:
        overlaps = [i for i, gold in enumerate(gold_labels) if _labels_overlap(lab, gold)]
        first_unmatched = next((i for i in overlaps if i not in matched_gold_idx), None)
        if first_unmatched is None:
            rel_unique.append(False)
            continue
        matched_gold_idx.add(first_unmatched)
        rel_unique.append(True)

    recall = 1.0 if any(rel_any) else 0.0
    mrr = (1.0 / hit_positions[0]) if hit_positions else 0.0

    if any(rel_unique):
        running_hits = 0
        precisions: List[float] = []
        for idx, is_rel in enumerate(rel_unique, start=1):
            if not is_rel:
                continue
            running_hits += 1
            precisions.append(running_hits / idx)
        ranked_precision = sum(precisions) / len(precisions)
    else:
        ranked_precision = 0.0

    dcg = sum((1.0 / math.log2(idx + 1)) for idx, is_rel in enumerate(rel_unique, start=1) if is_rel)
    ideal_rel_count = min(len(gold_labels), len(retrieved_labels))
    idcg = sum((1.0 / math.log2(idx + 1)) for idx in range(1, ideal_rel_count + 1))
    ndcg = (dcg / idcg) if idcg > 0 else 0.0

    coverage = len(matched_gold_idx) / len(gold_labels) if gold_labels else None

    return {
        "evidence_recall_at_k": recall,
        "evidence_mrr": mrr,
        "context_precision_ranked": ranked_precision,
        "evidence_ndcg_at_k": ndcg,
        "evidence_coverage": coverage,
    }


def _retrieval_doc_metrics(retrieved, expected_doc: Optional[str]) -> Dict[str, Optional[Any]]:
    if not expected_doc:
        return {
            "retrieved_has_expected_doc": None,
            "context_precision": None,
            "context_recall": None,
        }

    hits = [c for c in retrieved if _doc_matches_expected(c.rel_path, expected_doc)]
    has_expected = len(hits) > 0
    precision = (len(hits) / len(retrieved)) if retrieved else 0.0
    recall = 1.0 if has_expected else 0.0
    return {
        "retrieved_has_expected_doc": has_expected,
        "context_precision": precision,
        "context_recall": recall,
    }


def _verification_passed(cannot_answer: bool, verification: Optional[Dict[str, Any]]) -> bool:
    if cannot_answer:
        return True
    if not isinstance(verification, dict):
        return False
    return bool(verification.get("all_supported", False))


def _normalize_item(item: Dict[str, Any], idx: int) -> Dict[str, Any]:
    expected_behavior = str(item.get("expected_behavior") or item.get("expected") or "answer").strip().lower()
    if expected_behavior not in {"answer", "refuse"}:
        expected_behavior = "answer"

    question_type = str(item.get("question_type") or "").strip().lower()
    if not question_type:
        question_type = "out_of_scope" if expected_behavior == "refuse" else "metadata"

    expected_answer = item.get("expected_answer")
    if expected_answer is None:
        expected_answer = item.get("expected_value")

    expected_answer_regex = item.get("expected_answer_regex")
    if expected_answer_regex is None:
        expected_answer_regex = item.get("expected_value_regex")

    return {
        "id": str(item.get("id") or f"q{idx+1}"),
        "question": str(item.get("question", "")).strip(),
        "expected_behavior": expected_behavior,
        "question_type": question_type,
        "expected_doc": item.get("expected_doc"),
        "expected_answer": expected_answer,
        "expected_answer_regex": expected_answer_regex,
        "required_phrases": item.get("required_phrases") or [],
        "acceptable_answers": item.get("acceptable_answers") or [],
        "normalization": item.get("normalization"),
        "gold_evidence": item.get("gold_evidence") or [],
        "gold_evidence_labels": item.get("gold_evidence_labels") or [],
    }


def _phrases_match(
    text: str,
    required_phrases: Sequence[str],
    normalization: Optional[Any],
) -> Optional[bool]:
    phrases = [
        _apply_normalization(str(p), normalization).lower()
        for p in required_phrases
        if str(p).strip()
    ]
    if len(phrases) == 0:
        return None
    haystack = _apply_normalization(text or "", normalization).lower()
    return all(p in haystack for p in phrases)


def _answer_matches_expected(
    item: Dict[str, Any],
    answer_text: str,
    cited_evidence_text: str = "",
) -> Optional[bool]:
    expected_answer = item.get("expected_answer")
    expected_answer_regex = item.get("expected_answer_regex")
    required_phrases = item.get("required_phrases") or []
    acceptable_answers = item.get("acceptable_answers") or []
    normalization = item.get("normalization")

    if (
        expected_answer is None
        and not expected_answer_regex
        and len(acceptable_answers) == 0
        and len(required_phrases) == 0
    ):
        return None

    plain_answer = _strip_inline_citations(answer_text)
    normalized_answer = _apply_normalization(plain_answer, normalization)

    if isinstance(expected_answer, list):
        needed = [
            _apply_normalization(str(x), normalization).lower()
            for x in expected_answer
            if str(x).strip()
        ]
        if len(needed) == 0:
            return None
        haystack = normalized_answer.lower()
        list_match = all(needle in haystack for needle in needed)
    else:
        list_match = False

    candidate_values: List[str] = []
    if isinstance(expected_answer, str) and expected_answer.strip():
        candidate_values.append(expected_answer.strip())
    candidate_values.extend(str(x).strip() for x in acceptable_answers if str(x).strip())

    normalized_haystack = normalized_answer.lower()
    candidate_match = any(
        _apply_normalization(cand, normalization).lower() in normalized_haystack for cand in candidate_values
    )

    regex_match = False
    if expected_answer_regex:
        try:
            regex_match = re.search(str(expected_answer_regex), plain_answer, flags=re.IGNORECASE) is not None
        except re.error:
            regex_match = False

    phrase_answer_match = _phrases_match(plain_answer, required_phrases, normalization)
    phrase_cited_match = _phrases_match(cited_evidence_text, required_phrases, normalization)

    return (
        list_match
        or candidate_match
        or regex_match
        or bool(phrase_answer_match)
        or bool(phrase_cited_match)
    )


def _get_trace_labels(run: Any, stage_name: str) -> List[str]:
    trace = getattr(run, "retrieval_trace", None)
    if trace is None:
        return []

    stage = None
    if isinstance(trace, dict):
        stage = trace.get(stage_name)
    else:
        stage = getattr(trace, stage_name, None)
    if not stage:
        return []

    labels: List[str] = []
    for chunk in stage:
        if isinstance(chunk, dict):
            rel = str(chunk.get("rel_path", ""))
            start = int(chunk.get("start_line", 0))
            end = int(chunk.get("end_line", 0))
        else:
            rel = str(getattr(chunk, "rel_path", ""))
            start = int(getattr(chunk, "start_line", 0))
            end = int(getattr(chunk, "end_line", 0))
        if rel and start > 0 and end > 0:
            labels.append(f"{rel}:{start}-{end}")
    return labels


def _build_corpus_cache(cfg: AppConfig) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for p in iter_source_files(cfg):
        try:
            rel = str(p.relative_to(cfg.repo_path)).replace("\\", "/")
        except Exception:
            rel = str(p).replace("\\", "/")
        try:
            out[rel] = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            out[rel] = ""
    return out


def _mean(results: List[Dict[str, Any]], key: str) -> Optional[float]:
    vals = [float(r[key]) for r in results if isinstance(r.get(key), (int, float))]
    if not vals:
        return None
    return sum(vals) / len(vals)


def _summarize_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    passed = sum(1 for r in results if bool(r.get("pass_overall")))

    summary: Dict[str, Any] = {
        "count": total,
        "passed": passed,
        "pass_rate": (passed / total) if total else 0.0,
        "avg_context_precision_doc": _mean(results, "context_precision"),
        "avg_context_recall_doc": _mean(results, "context_recall"),
        "avg_evidence_recall_at_k": _mean(results, "evidence_recall_at_k"),
        "avg_evidence_mrr": _mean(results, "evidence_mrr"),
        "avg_context_precision_ranked": _mean(results, "context_precision_ranked"),
        "avg_evidence_ndcg_at_k": _mean(results, "evidence_ndcg_at_k"),
        "avg_evidence_coverage": _mean(results, "evidence_coverage"),
    }

    by_type: Dict[str, Any] = {}
    types = sorted({str(r.get("question_type", "unknown")) for r in results})
    for t in types:
        subset = [r for r in results if str(r.get("question_type", "unknown")) == t]
        sub_passed = sum(1 for r in subset if bool(r.get("pass_overall")))
        by_type[t] = {
            "count": len(subset),
            "passed": sub_passed,
            "pass_rate": (sub_passed / len(subset)) if subset else 0.0,
            "avg_evidence_recall_at_k": _mean(subset, "evidence_recall_at_k"),
            "avg_evidence_mrr": _mean(subset, "evidence_mrr"),
            "avg_context_precision_ranked": _mean(subset, "context_precision_ranked"),
            "avg_evidence_ndcg_at_k": _mean(subset, "evidence_ndcg_at_k"),
        }
    summary["by_question_type"] = by_type
    return summary


def _evaluate_questions(
    *,
    cfg: AppConfig,
    questions: List[Dict[str, Any]],
    mode: str,
    dataset_name: str,
    corpus_cache: Dict[str, str],
) -> List[Dict[str, Any]]:
    corpus_text = "\n".join(corpus_cache.values())
    results: List[Dict[str, Any]] = []

    for idx, raw in enumerate(questions):
        item = _normalize_item(raw, idx)
        q = item["question"]
        expected_behavior = item["expected_behavior"]
        expected_doc = item.get("expected_doc")
        expected_answer = item.get("expected_answer")
        expected_answer_regex = item.get("expected_answer_regex")
        required_phrases = item.get("required_phrases") or []
        gold_labels = _extract_gold_labels(item)

        run = ask_question(cfg, question=q, debug=False, no_llm=(mode == "retrieval"))
        ans = run.answer

        answer_citation_labels = parse_labels_from_text(ans.answer)
        has_citations = len(answer_citation_labels) > 0
        retrieved_labels = [f"{c.rel_path}:{c.start_line}-{c.end_line}" for c in run.retrieved]
        retrieved_text = "\n".join(c.text for c in run.retrieved)
        retrieved_by_label = {f"{c.rel_path}:{c.start_line}-{c.end_line}": c.text for c in run.retrieved}
        cited_evidence_text = "\n".join(retrieved_by_label.get(lab, "") for lab in answer_citation_labels)
        retrieved_set = set(retrieved_labels)

        doc_metrics = _retrieval_doc_metrics(run.retrieved, expected_doc)
        retrieved_has_expected_doc = doc_metrics["retrieved_has_expected_doc"]

        expected_answer_str = expected_answer if isinstance(expected_answer, str) else None
        retrieval_value_match = _value_matches(
            retrieved_text,
            expected_value=expected_answer_str,
            expected_value_regex=expected_answer_regex,
        )
        retrieval_required_phrase_match = _phrases_match(retrieved_text, required_phrases, item.get("normalization"))
        answer_value_match = _answer_matches_expected(
            item,
            ans.answer,
            cited_evidence_text=cited_evidence_text,
        )
        corpus_value_match = _value_matches(
            corpus_text,
            expected_value=expected_answer_str,
            expected_value_regex=expected_answer_regex,
        )
        corpus_required_phrase_match = _phrases_match(corpus_text, required_phrases, item.get("normalization"))
        retrieval_signal: Optional[bool] = retrieval_value_match
        corpus_signal: Optional[bool] = corpus_value_match
        if retrieval_signal is None:
            retrieval_signal = retrieval_required_phrase_match
        if corpus_signal is None:
            corpus_signal = corpus_required_phrase_match
        retrieval_missed_existing_value = (
            bool(corpus_signal) and (retrieval_signal is False)
        ) if corpus_signal is not None else None

        verification_ok = _verification_passed(ans.cannot_answer, run.verification)

        evidence = _evidence_metrics(retrieved_labels, gold_labels)
        citation_validity = all(lab in retrieved_set for lab in answer_citation_labels) if has_citations else False
        citation_overlaps_gold = (
            any(_labels_overlap(cit, gold) for cit in answer_citation_labels for gold in gold_labels)
            if gold_labels and has_citations
            else None
        )

        fused_labels = _get_trace_labels(run, "fused_candidates")
        reranked_labels = _get_trace_labels(run, "reranked_candidates")
        evidence_before_rerank = _evidence_metrics(fused_labels, gold_labels).get("evidence_recall_at_k")
        evidence_after_rerank = _evidence_metrics(reranked_labels, gold_labels).get("evidence_recall_at_k")
        reranker_dropped_evidence = (
            bool(evidence_before_rerank) and (evidence_after_rerank == 0.0)
            if (evidence_before_rerank is not None and evidence_after_rerank is not None)
            else None
        )

        if expected_behavior == "refuse":
            refused_ok = ans.cannot_answer
        else:
            refused_ok = not ans.cannot_answer

        citations_ok = True if ans.cannot_answer else (has_citations and citation_validity)
        pass_expected_doc_rule = True if retrieved_has_expected_doc is None else bool(retrieved_has_expected_doc)
        if expected_behavior == "refuse":
            pass_evidence_recall_rule = True
        else:
            pass_evidence_recall_rule = (
                True if evidence["evidence_recall_at_k"] is None else bool(evidence["evidence_recall_at_k"])
            )

        if mode == "retrieval":
            if retrieval_signal is None:
                pass_expected_value_rule = True
            else:
                pass_expected_value_rule = bool(retrieval_signal)
            pass_refusal_rule: Optional[bool] = None
            pass_citation_rule: Optional[bool] = None
            pass_verification_rule: Optional[bool] = None
            pass_citation_overlap_rule: Optional[bool] = None
            pass_overall = pass_expected_doc_rule and pass_evidence_recall_rule and pass_expected_value_rule
        else:
            pass_expected_value_rule = True if answer_value_match is None else bool(answer_value_match)
            pass_refusal_rule = refused_ok
            pass_citation_rule = citations_ok
            pass_verification_rule = True if expected_behavior == "refuse" else verification_ok
            if expected_behavior == "refuse" or not gold_labels:
                pass_citation_overlap_rule = True
            else:
                pass_citation_overlap_rule = bool(citation_overlaps_gold) if not ans.cannot_answer else False

            pass_overall = (
                pass_refusal_rule
                and pass_citation_rule
                and pass_expected_doc_rule
                and pass_evidence_recall_rule
                and pass_expected_value_rule
                and pass_citation_overlap_rule
                and pass_verification_rule
            )

        results.append(
            {
                "mode": mode,
                "dataset": dataset_name,
                "id": item["id"],
                "question_type": item["question_type"],
                "question": q,
                "expected": expected_behavior,  # legacy key
                "expected_behavior": expected_behavior,
                "expected_doc": expected_doc,
                "expected_value": expected_answer,  # legacy key
                "expected_answer": expected_answer,
                "expected_value_regex": expected_answer_regex,  # legacy key
                "expected_answer_regex": expected_answer_regex,
                "required_phrases": required_phrases,
                "gold_evidence_labels": gold_labels,
                "acceptable_answers": item.get("acceptable_answers", []),
                "normalization": item.get("normalization"),
                "cannot_answer": ans.cannot_answer,
                "answer_text": ans.answer,
                "answer_citations": answer_citation_labels,
                "confidence": ans.confidence,
                "model_confidence": ans.model_confidence,
                "computed_confidence": ans.computed_confidence,
                "has_citations": has_citations,
                "citation_validity": citation_validity if has_citations else None,
                "citation_overlaps_gold_evidence": citation_overlaps_gold,
                "retrieved_top_k": len(run.retrieved),
                "retrieved_labels": retrieved_labels,
                "retrieved_has_expected_doc": retrieved_has_expected_doc,
                "context_precision": doc_metrics["context_precision"],
                "context_recall": doc_metrics["context_recall"],
                "evidence_recall_at_k": evidence["evidence_recall_at_k"],
                "evidence_mrr": evidence["evidence_mrr"],
                "context_precision_ranked": evidence["context_precision_ranked"],
                "evidence_ndcg_at_k": evidence["evidence_ndcg_at_k"],
                "evidence_coverage": evidence["evidence_coverage"],
                "evidence_recall_before_rerank": evidence_before_rerank,
                "evidence_recall_after_rerank": evidence_after_rerank,
                "reranker_dropped_evidence": reranker_dropped_evidence,
                "retrieval_contains_expected_value": retrieval_value_match,
                "retrieval_contains_required_phrases": retrieval_required_phrase_match,
                "answer_matches_expected_value": answer_value_match,
                "corpus_contains_expected_value": corpus_value_match,
                "corpus_contains_required_phrases": corpus_required_phrase_match,
                "retrieval_missed_existing_value": retrieval_missed_existing_value,
                "verification_passed": verification_ok,
                "pass_refusal_rule": pass_refusal_rule,
                "pass_citation_rule": pass_citation_rule,
                "pass_expected_doc_rule": pass_expected_doc_rule,
                "pass_evidence_recall_rule": pass_evidence_recall_rule,
                "pass_expected_value_rule": pass_expected_value_rule,
                "pass_citation_overlap_rule": pass_citation_overlap_rule,
                "pass_verification_rule": pass_verification_rule,
                "pass_overall": pass_overall,
            }
        )

    return results


def run_eval(
    eval_path: str = "evalset/gold.jsonl",
    output_path: str = "data/eval_results_single.json",
    mode: str = "full",
) -> None:
    """
    Evaluate a single dataset file and write a flat list of per-question rows.

    This evaluates one dataset file (for quick experiments).
    """
    mode = mode.strip().lower()
    if mode not in {"full", "retrieval"}:
        raise ValueError("mode must be 'full' or 'retrieval'")

    cfg = AppConfig()
    cfg.ensure_dirs()

    eval_file = Path(eval_path)
    questions = load_questions(eval_file)
    corpus_cache = _build_corpus_cache(cfg)
    results = _evaluate_questions(
        cfg=cfg,
        questions=questions,
        mode=mode,
        dataset_name=eval_file.stem,
        corpus_cache=corpus_cache,
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    passed = sum(1 for r in results if r.get("pass_overall"))
    print(f"Wrote eval results: {out} ({mode} mode, pass_overall={passed}/{len(results)})")


def run_eval_gold_silver(
    *,
    gold_path: str = "evalset/gold.jsonl",
    silver_path: str = "evalset/silver.jsonl",
    output_path: str = "data/eval_results_suite.json",
    mode: str = "full",
) -> None:
    """
    Evaluate gold and silver datasets separately and write one combined report.
    """
    mode = mode.strip().lower()
    if mode not in {"full", "retrieval"}:
        raise ValueError("mode must be 'full' or 'retrieval'")

    cfg = AppConfig()
    cfg.ensure_dirs()

    gold_file = Path(gold_path)
    silver_file = Path(silver_path)
    if not gold_file.exists():
        raise FileNotFoundError(f"Gold evalset not found: {gold_file}")
    if not silver_file.exists():
        raise FileNotFoundError(f"Silver evalset not found: {silver_file}")

    corpus_cache = _build_corpus_cache(cfg)
    gold_rows = _evaluate_questions(
        cfg=cfg,
        questions=load_questions(gold_file),
        mode=mode,
        dataset_name="gold",
        corpus_cache=corpus_cache,
    )
    silver_rows = _evaluate_questions(
        cfg=cfg,
        questions=load_questions(silver_file),
        mode=mode,
        dataset_name="silver",
        corpus_cache=corpus_cache,
    )

    payload = {
        "mode": mode,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "gold": {
            "path": str(gold_file).replace("\\", "/"),
            "summary": _summarize_results(gold_rows),
            "results": gold_rows,
        },
        "silver": {
            "path": str(silver_file).replace("\\", "/"),
            "summary": _summarize_results(silver_rows),
            "results": silver_rows,
        },
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    gold_summary = payload["gold"]["summary"]
    silver_summary = payload["silver"]["summary"]
    print(
        "Wrote eval suite:",
        out,
        f"(mode={mode}, gold={gold_summary['passed']}/{gold_summary['count']},",
        f"silver={silver_summary['passed']}/{silver_summary['count']})",
    )


def run_eval_retrieval_only(
    eval_path: str = "evalset/gold.jsonl",
    output_path: str = "data/eval_results_retrieval.json",
) -> None:
    run_eval(eval_path=eval_path, output_path=output_path, mode="retrieval")
