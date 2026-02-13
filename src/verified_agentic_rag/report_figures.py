from __future__ import annotations

from datetime import datetime, timezone
import csv
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt


def _parse_bool(raw: str) -> Optional[bool]:
    val = (raw or "").strip().lower()
    if val in {"true", "1", "yes"}:
        return True
    if val in {"false", "0", "no"}:
        return False
    return None


def _parse_float(raw: str) -> Optional[float]:
    val = (raw or "").strip()
    if not val:
        return None
    try:
        return float(val)
    except ValueError:
        return None


def _read_rows(csv_path: Path) -> List[Dict[str, str]]:
    with open(csv_path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _save(fig: plt.Figure, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return str(path).replace("\\", "/")


def _name(base: str, date_tag: str) -> str:
    return f"{date_tag}_{base}.png"


def _plot_pass_rate_by_dataset_mode(rows: List[Dict[str, str]], out_dir: Path, date_tag: str) -> str:
    datasets = ["gold", "silver"]
    retrieval_rates: List[float] = []
    full_rates: List[float] = []
    for ds in datasets:
        ds_rows = [r for r in rows if r.get("dataset") == ds]
        if not ds_rows:
            retrieval_rates.append(0.0)
            full_rates.append(0.0)
            continue
        ret_pass = sum(1 for r in ds_rows if _parse_bool(r.get("pass_overall_retrieval", "")) is True)
        full_pass = sum(1 for r in ds_rows if _parse_bool(r.get("pass_overall_full", "")) is True)
        retrieval_rates.append(ret_pass / len(ds_rows))
        full_rates.append(full_pass / len(ds_rows))

    x = list(range(len(datasets)))
    width = 0.36
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar([i - width / 2 for i in x], retrieval_rates, width=width, label="retrieval")
    ax.bar([i + width / 2 for i in x], full_rates, width=width, label="full")
    ax.set_xticks(x, datasets)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Pass rate")
    ax.set_title("Pass Rate by Dataset and Mode")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    return _save(fig, out_dir / _name("pass_rate_by_dataset_mode", date_tag))


def _plot_behavior_confusion(rows: List[Dict[str, str]], out_dir: Path, date_tag: str) -> str:
    expected = ["answer", "refuse"]
    answered_counts: List[int] = []
    refused_counts: List[int] = []
    for e in expected:
        e_rows = [r for r in rows if (r.get("expected_behavior") or "").strip().lower() == e]
        answered_counts.append(sum(1 for r in e_rows if _parse_bool(r.get("cannot_answer", "")) is False))
        refused_counts.append(sum(1 for r in e_rows if _parse_bool(r.get("cannot_answer", "")) is True))

    x = list(range(len(expected)))
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar(x, answered_counts, label="actual answer")
    ax.bar(x, refused_counts, bottom=answered_counts, label="actual refuse")
    ax.set_xticks(x, [f"expected {e}" for e in expected])
    ax.set_ylabel("Question count")
    ax.set_title("Behavior Breakdown (Full Mode)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    return _save(fig, out_dir / _name("behavior_confusion_full_mode", date_tag))


def _plot_rule_pass_bars(rows: List[Dict[str, str]], out_dir: Path, date_tag: str) -> str:
    rules = [
        "pass_refusal_rule",
        "pass_citation_rule",
        "pass_citation_overlap_rule",
        "pass_expected_value_rule",
        "pass_verification_rule",
    ]

    pass_counts: List[int] = []
    fail_counts: List[int] = []
    for rule in rules:
        values = [_parse_bool(r.get(rule, "")) for r in rows]
        pass_counts.append(sum(1 for v in values if v is True))
        fail_counts.append(sum(1 for v in values if v is False))

    x = list(range(len(rules)))
    fig, ax = plt.subplots(figsize=(8.8, 4.4))
    ax.bar(x, pass_counts, label="pass")
    ax.bar(x, fail_counts, bottom=pass_counts, label="fail")
    ax.set_xticks(x, [r.replace("pass_", "") for r in rules], rotation=18, ha="right")
    ax.set_ylabel("Question count")
    ax.set_title("Rule Pass/Fail Breakdown (Full Mode)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    return _save(fig, out_dir / _name("rule_pass_breakdown_full_mode", date_tag))


def _plot_retrieval_ranking_distributions(rows: List[Dict[str, str]], out_dir: Path, date_tag: str) -> str:
    mrr = [_parse_float(r.get("evidence_mrr_retrieval", "")) for r in rows]
    ndcg = [_parse_float(r.get("evidence_ndcg_at_k_retrieval", "")) for r in rows]
    recall = [_parse_float(r.get("evidence_recall_at_k_retrieval", "")) for r in rows]
    mrr_vals = [v for v in mrr if v is not None]
    ndcg_vals = [v for v in ndcg if v is not None]
    recall_vals = [v for v in recall if v is not None]

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8))
    bins = [i / 10 for i in range(0, 11)]
    axes[0].hist(mrr_vals, bins=bins, edgecolor="black")
    axes[0].set_title("MRR (retrieval)")
    axes[0].set_xlim(0, 1)

    axes[1].hist(ndcg_vals, bins=bins, edgecolor="black")
    axes[1].set_title("nDCG@k (retrieval)")
    axes[1].set_xlim(0, 1)

    axes[2].hist(recall_vals, bins=bins, edgecolor="black")
    axes[2].set_title("Evidence Recall@k (retrieval)")
    axes[2].set_xlim(0, 1)

    for ax in axes:
        ax.grid(axis="y", alpha=0.25)
        ax.set_ylabel("Question count")
    return _save(fig, out_dir / _name("retrieval_ranking_metrics_distribution", date_tag))


def _plot_context_precision_distribution(rows: List[Dict[str, str]], out_dir: Path, date_tag: str) -> str:
    doc_vals = [_parse_float(r.get("context_precision_doc", "")) for r in rows]
    ranked_vals = [_parse_float(r.get("context_precision_ranked_retrieval", "")) for r in rows]
    doc_values = [v for v in doc_vals if v is not None]
    ranked_values = [v for v in ranked_vals if v is not None]

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4))
    bins = [i / 10 for i in range(0, 11)]

    axes[0].hist(doc_values, bins=bins, edgecolor="black")
    axes[0].set_xlim(0, 1.0)
    axes[0].set_xlabel("context_precision_doc")
    axes[0].set_ylabel("Question count")
    axes[0].set_title("Doc-level Context Precision")
    axes[0].grid(axis="y", alpha=0.25)

    axes[1].hist(ranked_values, bins=bins, edgecolor="black")
    axes[1].set_xlim(0, 1.0)
    axes[1].set_xlabel("context_precision_ranked_retrieval")
    axes[1].set_ylabel("Question count")
    axes[1].set_title("Rank-aware Context Precision")
    axes[1].grid(axis="y", alpha=0.25)

    return _save(fig, out_dir / _name("context_precision_distribution", date_tag))


def generate_result_figures(
    csv_path: str,
    output_dir: str = "reports/figures",
    date_tag: str = "",
) -> List[str]:
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    if not date_tag:
        date_tag = datetime.now(timezone.utc).strftime("%Y%m%d")

    rows = _read_rows(csv_file)
    full_rows = [r for r in rows if str(r.get("pass_overall_full", "")).strip() != ""]
    out_dir = Path(output_dir)

    out_paths = [
        _plot_pass_rate_by_dataset_mode(rows, out_dir, date_tag),
        _plot_behavior_confusion(full_rows, out_dir, date_tag),
        _plot_rule_pass_bars(full_rows, out_dir, date_tag),
        _plot_retrieval_ranking_distributions(rows, out_dir, date_tag),
        _plot_context_precision_distribution(rows, out_dir, date_tag),
    ]
    return out_paths
