from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import AppConfig
from .agentic import ask_question
from .cite import parse_labels_from_text


def load_questions(path: Path) -> List[Dict]:
    """
    questions.jsonl format:
    One JSON object per line:
    {
      "question": "...",
      "expected": "answer"|"refuse",
      "expected_doc": "Data_Protection_-_Employees.txt",         # optional
      "expected_value": "PERSONNEL",                              # optional
      "expected_value_regex": "annual\\s+or\\s+if\\s+required"    # optional
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
        exact_match = _norm_text(expected_value) in _norm_text(text)
    if expected_value_regex:
        try:
            regex_match = re.search(expected_value_regex, text or "", flags=re.IGNORECASE) is not None
        except re.error:
            regex_match = False
    return exact_match or regex_match


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


def run_eval(
    eval_path: str = "evalset/questions.jsonl",
    output_path: str = "data/eval_results.json",
    mode: str = "full",
) -> None:
    mode = mode.strip().lower()
    if mode not in {"full", "retrieval"}:
        raise ValueError("mode must be 'full' or 'retrieval'")

    cfg = AppConfig()
    cfg.ensure_dirs()

    questions = load_questions(Path(eval_path))
    results = []

    for item in questions:
        q = item["question"]
        expected = item.get("expected", "answer")
        expected_doc = item.get("expected_doc")
        expected_value = item.get("expected_value")
        expected_value_regex = item.get("expected_value_regex")

        run = ask_question(cfg, question=q, debug=False, no_llm=(mode == "retrieval"))
        ans = run.answer

        labels = parse_labels_from_text(ans.answer)
        has_citations = len(labels) > 0
        retrieved_labels = [f"{c.rel_path}:{c.start_line}-{c.end_line}" for c in run.retrieved]
        retrieved_text = "\n".join(c.text for c in run.retrieved)
        doc_metrics = _retrieval_doc_metrics(run.retrieved, expected_doc)
        retrieved_has_expected_doc = doc_metrics["retrieved_has_expected_doc"]
        retrieval_value_match = _value_matches(
            retrieved_text,
            expected_value=expected_value,
            expected_value_regex=expected_value_regex,
        )
        answer_value_match = _value_matches(
            ans.answer,
            expected_value=expected_value,
            expected_value_regex=expected_value_regex,
        )
        verification_ok = _verification_passed(ans.cannot_answer, run.verification)

        # Baseline checks
        if expected == "refuse":
            refused_ok = ans.cannot_answer
        else:
            refused_ok = not ans.cannot_answer

        citations_ok = True if ans.cannot_answer else has_citations
        pass_expected_doc_rule = True if retrieved_has_expected_doc is None else retrieved_has_expected_doc

        if mode == "retrieval":
            pass_expected_value_rule = True if retrieval_value_match is None else retrieval_value_match
            pass_overall = pass_expected_doc_rule and pass_expected_value_rule
            pass_refusal_rule: Optional[bool] = None
            pass_citation_rule: Optional[bool] = None
            pass_verification_rule: Optional[bool] = None
        else:
            pass_expected_value_rule = True if answer_value_match is None else answer_value_match
            pass_refusal_rule = refused_ok
            pass_citation_rule = citations_ok
            pass_verification_rule = True if expected == "refuse" else verification_ok
            pass_overall = (
                pass_refusal_rule
                and pass_citation_rule
                and pass_expected_doc_rule
                and pass_expected_value_rule
                and pass_verification_rule
            )

        results.append(
            {
                "mode": mode,
                "question": q,
                "expected": expected,
                "expected_doc": expected_doc,
                "expected_value": expected_value,
                "expected_value_regex": expected_value_regex,
                "cannot_answer": ans.cannot_answer,
                "confidence": ans.confidence,
                "model_confidence": ans.model_confidence,
                "computed_confidence": ans.computed_confidence,
                "has_citations": has_citations,
                "retrieved_top_k": len(run.retrieved),
                "retrieved_labels": retrieved_labels,
                "retrieved_has_expected_doc": retrieved_has_expected_doc,
                "context_precision": doc_metrics["context_precision"],
                "context_recall": doc_metrics["context_recall"],
                "retrieval_contains_expected_value": retrieval_value_match,
                "answer_matches_expected_value": answer_value_match,
                "verification_passed": verification_ok,
                "pass_refusal_rule": pass_refusal_rule,
                "pass_citation_rule": pass_citation_rule,
                "pass_expected_doc_rule": pass_expected_doc_rule,
                "pass_expected_value_rule": pass_expected_value_rule,
                "pass_verification_rule": pass_verification_rule,
                "pass_overall": pass_overall,
            }
        )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    passed = sum(1 for r in results if r.get("pass_overall"))
    print(f"Wrote eval results: {out} ({mode} mode, pass_overall={passed}/{len(results)})")


def run_eval_retrieval_only(
    eval_path: str = "evalset/questions.jsonl",
    output_path: str = "data/eval_results_retrieval.json",
) -> None:
    run_eval(eval_path=eval_path, output_path=output_path, mode="retrieval")
