from __future__ import annotations

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


def _plot_pass_rate_by_dataset_mode(rows: List[Dict[str, str]], out_dir: Path) -> str:
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
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([i - width / 2 for i in x], retrieval_rates, width=width, label="retrieval")
    ax.bar([i + width / 2 for i in x], full_rates, width=width, label="full")
    ax.set_xticks(x, datasets)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Pass rate")
    ax.set_title("Pass Rate by Dataset and Mode")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    return _save(fig, out_dir / "pass_rate_by_dataset_mode.png")


def _plot_behavior_confusion(rows: List[Dict[str, str]], out_dir: Path) -> str:
    expected = ["answer", "refuse"]
    answered_counts: List[int] = []
    refused_counts: List[int] = []
    for e in expected:
        e_rows = [r for r in rows if r.get("expected_behavior") == e]
        answered_counts.append(sum(1 for r in e_rows if _parse_bool(r.get("cannot_answer", "")) is False))
        refused_counts.append(sum(1 for r in e_rows if _parse_bool(r.get("cannot_answer", "")) is True))

    x = list(range(len(expected)))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x, answered_counts, label="actual answer")
    ax.bar(x, refused_counts, bottom=answered_counts, label="actual refuse")
    ax.set_xticks(x, [f"expected {e}" for e in expected])
    ax.set_ylabel("Question count")
    ax.set_title("Behavior Breakdown (Full Mode)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    return _save(fig, out_dir / "behavior_confusion_full_mode.png")


def _plot_rule_pass_bars(rows: List[Dict[str, str]], out_dir: Path) -> str:
    rules = [
        "pass_refusal_rule",
        "pass_citation_rule",
        "pass_verification_rule",
        "pass_expected_value_rule",
    ]

    pass_counts: List[int] = []
    fail_counts: List[int] = []
    for rule in rules:
        values = [_parse_bool(r.get(rule, "")) for r in rows]
        pass_counts.append(sum(1 for v in values if v is True))
        fail_counts.append(sum(1 for v in values if v is False))

    x = list(range(len(rules)))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x, pass_counts, label="pass")
    ax.bar(x, fail_counts, bottom=pass_counts, label="fail")
    ax.set_xticks(x, [r.replace("pass_", "") for r in rules], rotation=18, ha="right")
    ax.set_ylabel("Question count")
    ax.set_title("Rule Pass/Fail Breakdown (Full Mode)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    return _save(fig, out_dir / "rule_pass_breakdown_full_mode.png")


def _plot_context_precision_distribution(rows: List[Dict[str, str]], out_dir: Path) -> str:
    vals = [_parse_float(r.get("context_precision_doc", "")) for r in rows]
    values = [v for v in vals if v is not None]
    fig, ax = plt.subplots(figsize=(7, 4))
    bins = [i / 10 for i in range(0, 11)]
    ax.hist(values, bins=bins, edgecolor="black")
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("context_precision_doc")
    ax.set_ylabel("Question count")
    ax.set_title("Distribution of Document-level Context Precision")
    ax.grid(axis="y", alpha=0.25)
    return _save(fig, out_dir / "context_precision_distribution.png")


def generate_result_figures(csv_path: str, output_dir: str = "reports/figures") -> List[str]:
    csv_file = Path(csv_path)
    if not csv_file.exists():
        candidates = [
            Path("reports/full_system_eval_question_results_20260212.csv"),
            Path("data/reports/full_system_eval_question_results_20260212.csv"),
        ]
        found = next((p for p in candidates if p.exists()), None)
        if found is None:
            raise FileNotFoundError(f"CSV not found: {csv_path}")
        csv_file = found

    rows = _read_rows(csv_file)
    full_rows = [r for r in rows if r.get("pass_overall_full", "").strip()]
    out_dir = Path(output_dir)

    out_paths = [
        _plot_pass_rate_by_dataset_mode(rows, out_dir),
        _plot_behavior_confusion(full_rows, out_dir),
        _plot_rule_pass_bars(full_rows, out_dir),
        _plot_context_precision_distribution(full_rows, out_dir),
    ]
    return out_paths
