from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def _load_json(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _flatten_suite(suite: Dict, mode_name: str) -> Dict[Tuple[str, str], Dict]:
    out: Dict[Tuple[str, str], Dict] = {}
    for dataset in ["gold", "silver"]:
        bucket = suite.get(dataset, {})
        for row in bucket.get("results", []):
            key = (dataset, str(row.get("id", "")))
            out[key] = dict(row)
    return out


def _safe(v):
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False)
    if v is None:
        return ""
    return v


def build_question_rows(retrieval_suite: Dict, full_suite: Dict) -> List[Dict]:
    ret_rows = _flatten_suite(retrieval_suite, "retrieval")
    full_rows = _flatten_suite(full_suite, "full")
    keys = sorted(set(ret_rows.keys()) | set(full_rows.keys()))

    out: List[Dict] = []
    for dataset, qid in keys:
        r = ret_rows.get((dataset, qid), {})
        f = full_rows.get((dataset, qid), {})
        base = f or r
        row = {
            "dataset": dataset,
            "id": qid,
            "question": base.get("question"),
            "question_type": base.get("question_type"),
            "expected_behavior": base.get("expected_behavior") or base.get("expected"),
            "expected_answer": base.get("expected_answer"),
            "expected_answer_regex": base.get("expected_answer_regex"),
            "required_phrases": _safe(base.get("required_phrases")),
            "gold_evidence_labels": _safe(base.get("gold_evidence_labels")),
            "cannot_answer": f.get("cannot_answer", ""),
            "answer_text": f.get("answer_text", ""),
            "answer_citations": _safe(f.get("answer_citations", [])),
            "has_citations": f.get("has_citations", ""),
            "citation_validity": f.get("citation_validity", ""),
            "citation_overlaps_gold_evidence": f.get("citation_overlaps_gold_evidence", ""),
            "verification_passed": f.get("verification_passed", ""),
            "pass_overall_full": f.get("pass_overall", ""),
            "pass_overall_retrieval": r.get("pass_overall", ""),
            "pass_refusal_rule": f.get("pass_refusal_rule", ""),
            "pass_citation_rule": f.get("pass_citation_rule", ""),
            "pass_expected_doc_rule": f.get("pass_expected_doc_rule", r.get("pass_expected_doc_rule", "")),
            "pass_evidence_recall_rule": f.get("pass_evidence_recall_rule", r.get("pass_evidence_recall_rule", "")),
            "pass_expected_value_rule": f.get("pass_expected_value_rule", r.get("pass_expected_value_rule", "")),
            "pass_citation_overlap_rule": f.get("pass_citation_overlap_rule", ""),
            "pass_verification_rule": f.get("pass_verification_rule", ""),
            "context_precision_doc": f.get("context_precision", r.get("context_precision", "")),
            "context_recall_doc": f.get("context_recall", r.get("context_recall", "")),
            "context_precision_ranked_full": f.get("context_precision_ranked", ""),
            "context_precision_ranked_retrieval": r.get("context_precision_ranked", ""),
            "evidence_recall_at_k_full": f.get("evidence_recall_at_k", ""),
            "evidence_recall_at_k_retrieval": r.get("evidence_recall_at_k", ""),
            "evidence_mrr_full": f.get("evidence_mrr", ""),
            "evidence_mrr_retrieval": r.get("evidence_mrr", ""),
            "evidence_ndcg_at_k_full": f.get("evidence_ndcg_at_k", ""),
            "evidence_ndcg_at_k_retrieval": r.get("evidence_ndcg_at_k", ""),
            "evidence_coverage_full": f.get("evidence_coverage", ""),
            "evidence_coverage_retrieval": r.get("evidence_coverage", ""),
            "evidence_recall_before_rerank": f.get("evidence_recall_before_rerank", r.get("evidence_recall_before_rerank", "")),
            "evidence_recall_after_rerank": f.get("evidence_recall_after_rerank", r.get("evidence_recall_after_rerank", "")),
            "reranker_dropped_evidence": f.get("reranker_dropped_evidence", r.get("reranker_dropped_evidence", "")),
            "retrieval_contains_expected_value": r.get("retrieval_contains_expected_value", ""),
            "retrieval_contains_required_phrases": r.get("retrieval_contains_required_phrases", ""),
            "answer_matches_expected_value": f.get("answer_matches_expected_value", ""),
            "corpus_contains_expected_value": r.get("corpus_contains_expected_value", ""),
            "corpus_contains_required_phrases": r.get("corpus_contains_required_phrases", ""),
            "retrieval_missed_existing_value": r.get("retrieval_missed_existing_value", ""),
        }
        out.append(row)
    return out


def _write_csv(rows: List[Dict], path: Path) -> None:
    if not rows:
        raise ValueError("Cannot write empty question-level CSV")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _safe(v) for k, v in row.items()})


def _summary_row(suite: Dict, dataset: str) -> Dict[str, object]:
    data = suite.get(dataset, {})
    summary = data.get("summary", {})
    return {
        "count": int(summary.get("count", 0)),
        "passed": int(summary.get("passed", 0)),
        "pass_rate": float(summary.get("pass_rate", 0.0)),
        "avg_evidence_recall_at_k": summary.get("avg_evidence_recall_at_k"),
        "avg_evidence_mrr": summary.get("avg_evidence_mrr"),
        "avg_context_precision_ranked": summary.get("avg_context_precision_ranked"),
        "avg_evidence_ndcg_at_k": summary.get("avg_evidence_ndcg_at_k"),
    }


def _bool(v) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        return v.strip().lower() in {"true", "1", "yes"}
    return False


def _failure_breakdown(full_suite: Dict) -> Dict[str, Counter]:
    out: Dict[str, Counter] = {}
    for dataset in ["gold", "silver"]:
        ctr: Counter = Counter()
        rows = full_suite.get(dataset, {}).get("results", [])
        for row in rows:
            if _bool(row.get("pass_overall")):
                continue
            for rule in [
                "pass_refusal_rule",
                "pass_citation_rule",
                "pass_expected_doc_rule",
                "pass_evidence_recall_rule",
                "pass_expected_value_rule",
                "pass_citation_overlap_rule",
                "pass_verification_rule",
            ]:
                if row.get(rule) is False:
                    ctr[rule] += 1
        out[dataset] = ctr
    return out


def _question_type_breakdown(rows: Iterable[Dict]) -> Dict[str, Counter]:
    by_dataset: Dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        by_dataset[str(row.get("dataset", "unknown"))][str(row.get("question_type", "unknown"))] += 1
    return by_dataset


def _to_markdown_table(headers: List[str], data_rows: List[List[object]]) -> str:
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in data_rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(out)


def _build_report_markdown(
    *,
    retrieval_suite_path: Path,
    full_suite_path: Path,
    csv_path: Path,
    retrieval_suite: Dict,
    full_suite: Dict,
    rows: List[Dict],
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    ret_gold = _summary_row(retrieval_suite, "gold")
    ret_silver = _summary_row(retrieval_suite, "silver")
    full_gold = _summary_row(full_suite, "gold")
    full_silver = _summary_row(full_suite, "silver")
    failures = _failure_breakdown(full_suite)
    qtype = _question_type_breakdown(rows)

    lines: List[str] = []
    lines.append("# Full Agent System Evaluation Report")
    lines.append("")
    lines.append(f"- Generated on: {now}")
    lines.append(f"- Retrieval suite file: `{retrieval_suite_path.as_posix()}`")
    lines.append(f"- Full suite file: `{full_suite_path.as_posix()}`")
    lines.append(f"- Question-level CSV: `{csv_path.as_posix()}`")
    lines.append("")
    lines.append("## Dataset Composition")
    lines.append("")
    comp_rows = []
    for dataset in ["gold", "silver"]:
        ctr = qtype.get(dataset, Counter())
        total = sum(ctr.values())
        comp_rows.append(
            [
                dataset,
                total,
                ctr.get("metadata", 0),
                ctr.get("procedure", 0),
                ctr.get("definition", 0),
                ctr.get("multi_chunk", 0),
                ctr.get("out_of_scope", 0),
            ]
        )
    lines.append(
        _to_markdown_table(
            ["Dataset", "Total", "Metadata", "Procedure", "Definition", "Multi-chunk", "Out-of-scope"],
            comp_rows,
        )
    )
    lines.append("")
    lines.append("## Aggregate Results")
    lines.append("")
    lines.append("### Retrieval mode")
    lines.append(
        _to_markdown_table(
            ["Dataset", "Count", "Passed", "Pass rate", "Avg evidence_recall@k", "Avg MRR", "Avg ranked precision", "Avg nDCG@k"],
            [
                [
                    "gold",
                    ret_gold["count"],
                    ret_gold["passed"],
                    f"{ret_gold['pass_rate']:.4f}",
                    f"{float(ret_gold['avg_evidence_recall_at_k'] or 0.0):.4f}",
                    f"{float(ret_gold['avg_evidence_mrr'] or 0.0):.4f}",
                    f"{float(ret_gold['avg_context_precision_ranked'] or 0.0):.4f}",
                    f"{float(ret_gold['avg_evidence_ndcg_at_k'] or 0.0):.4f}",
                ],
                [
                    "silver",
                    ret_silver["count"],
                    ret_silver["passed"],
                    f"{ret_silver['pass_rate']:.4f}",
                    f"{float(ret_silver['avg_evidence_recall_at_k'] or 0.0):.4f}",
                    f"{float(ret_silver['avg_evidence_mrr'] or 0.0):.4f}",
                    f"{float(ret_silver['avg_context_precision_ranked'] or 0.0):.4f}",
                    f"{float(ret_silver['avg_evidence_ndcg_at_k'] or 0.0):.4f}",
                ],
            ],
        )
    )
    lines.append("")
    lines.append("### Full mode")
    lines.append(
        _to_markdown_table(
            ["Dataset", "Count", "Passed", "Pass rate", "Avg evidence_recall@k", "Avg MRR", "Avg ranked precision", "Avg nDCG@k"],
            [
                [
                    "gold",
                    full_gold["count"],
                    full_gold["passed"],
                    f"{full_gold['pass_rate']:.4f}",
                    f"{float(full_gold['avg_evidence_recall_at_k'] or 0.0):.4f}",
                    f"{float(full_gold['avg_evidence_mrr'] or 0.0):.4f}",
                    f"{float(full_gold['avg_context_precision_ranked'] or 0.0):.4f}",
                    f"{float(full_gold['avg_evidence_ndcg_at_k'] or 0.0):.4f}",
                ],
                [
                    "silver",
                    full_silver["count"],
                    full_silver["passed"],
                    f"{full_silver['pass_rate']:.4f}",
                    f"{float(full_silver['avg_evidence_recall_at_k'] or 0.0):.4f}",
                    f"{float(full_silver['avg_evidence_mrr'] or 0.0):.4f}",
                    f"{float(full_silver['avg_context_precision_ranked'] or 0.0):.4f}",
                    f"{float(full_silver['avg_evidence_ndcg_at_k'] or 0.0):.4f}",
                ],
            ],
        )
    )
    lines.append("")
    lines.append("## Failure Breakdown (Full mode)")
    lines.append("")
    for dataset in ["gold", "silver"]:
        ctr = failures[dataset]
        if not ctr:
            lines.append(f"- {dataset}: no failures (all questions passed strict rules).")
            continue
        lines.append(f"- {dataset}:")
        for rule, count in ctr.most_common():
            lines.append(f"  - {rule}: {count}")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `required_phrases` checks are enabled in evaluation and can be satisfied by answer text or cited evidence text.")
    lines.append("- Core groundedness requirements remain strict: citation validity, citation overlap with gold evidence, and verification pass.")
    lines.append("")
    return "\n".join(lines)


def _write_pdf_from_markdown(md_text: str, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    lines = md_text.splitlines()
    chunk_size = 45
    with PdfPages(pdf_path) as pdf:
        for i in range(0, len(lines), chunk_size):
            chunk = lines[i : i + chunk_size]
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis("off")
            ax.text(
                0.02,
                0.98,
                "\n".join(chunk),
                va="top",
                ha="left",
                fontsize=8.5,
                family="monospace",
                wrap=True,
            )
            pdf.savefig(fig)
            plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate merged question-level CSV and markdown/pdf reports.")
    parser.add_argument("--retrieval-suite", required=True, help="Path to retrieval suite JSON")
    parser.add_argument("--full-suite", required=True, help="Path to full suite JSON")
    parser.add_argument("--csv-out", required=True, help="Output question-level CSV path")
    parser.add_argument("--md-out", required=True, help="Output markdown report path")
    parser.add_argument("--pdf-out", default="", help="Optional PDF report output path")
    args = parser.parse_args()

    retrieval_suite_path = Path(args.retrieval_suite)
    full_suite_path = Path(args.full_suite)
    csv_path = Path(args.csv_out)
    md_path = Path(args.md_out)
    pdf_path = Path(args.pdf_out) if args.pdf_out else None

    retrieval_suite = _load_json(retrieval_suite_path)
    full_suite = _load_json(full_suite_path)
    rows = build_question_rows(retrieval_suite, full_suite)
    _write_csv(rows, csv_path)
    report_md = _build_report_markdown(
        retrieval_suite_path=retrieval_suite_path,
        full_suite_path=full_suite_path,
        csv_path=csv_path,
        retrieval_suite=retrieval_suite,
        full_suite=full_suite,
        rows=rows,
    )

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(report_md, encoding="utf-8")

    if pdf_path is not None:
        _write_pdf_from_markdown(report_md, pdf_path)
        print(f"Wrote PDF report: {pdf_path}")

    print(f"Wrote question-level CSV: {csv_path}")
    print(f"Wrote markdown report: {md_path}")


if __name__ == "__main__":
    main()
