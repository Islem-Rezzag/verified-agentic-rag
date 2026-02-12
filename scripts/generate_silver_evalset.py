from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SOURCE_TXT_DIR = Path("data/source_repos/saltash_policy_pack/docs/txt")
OUTPUT_PATH = Path("evalset/silver.jsonl")


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _policy_name_from_path(path: Path) -> str:
    stem = path.stem.replace("_", " ").replace("-", " ").strip()
    return _clean(stem)


def _label(rel_path: str, start_line: int, end_line: int) -> str:
    return f"{rel_path}:{start_line}-{end_line}"


def _read_lines(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [line.strip() for line in text.splitlines()]


def _extract_policy_group(lines: List[str]) -> Optional[Tuple[str, int, int]]:
    for i, line in enumerate(lines, start=1):
        if "policy group" not in line.lower():
            continue
        m = re.search(r"policy group\s*[:\-]?\s*(.*)$", line, flags=re.IGNORECASE)
        if not m:
            continue
        value = _clean(m.group(1))
        if not value:
            for j in range(i + 1, min(i + 4, len(lines)) + 1):
                cand = _clean(lines[j - 1])
                if cand and "page" not in cand.lower():
                    value = cand
                    break
        if value:
            return value, max(1, i - 1), min(len(lines), i + 20)
    return None


def _extract_responsible_committee(lines: List[str]) -> Optional[Tuple[str, int, int]]:
    for i, line in enumerate(lines, start=1):
        m = re.search(
            r"responsi\w*\s+committee\s*[:\-]?\s*(.*)$",
            line,
            flags=re.IGNORECASE,
        )
        if not m:
            continue
        value = _clean(m.group(1))
        if value:
            return value, max(1, i - 1), min(len(lines), i + 20)
    return None


def _extract_review_guidance(lines: List[str]) -> Optional[Tuple[str, int, int]]:
    upper_bound = min(len(lines), 200)
    for i in range(1, upper_bound + 1):
        window = _clean(" ".join(lines[max(1, i - 1) - 1 : min(upper_bound, i + 2)]))
        w = window.lower()
        if "next review date" not in w and "annual or" not in w:
            continue

        if "annual or if" in w and "required by legislation" in w:
            return "Annual or if required by legislation", max(1, i - 1), min(upper_bound, i + 20)
        if "annual or as" in w and "required by legislation" in w:
            return "Annual or as required by legislation", max(1, i - 1), min(upper_bound, i + 20)
        if "annual or as required" in w:
            return "Annual or as required", max(1, i - 1), min(upper_bound, i + 20)
        if "annual or if required" in w:
            return "Annual or if required", max(1, i - 1), min(upper_bound, i + 20)
    return None


def _make_item(
    *,
    item_id: str,
    question: str,
    expected_doc: str,
    expected_answer: str,
    evidence_label: str,
    must_contain: List[str],
    normalization: str,
) -> Dict:
    return {
        "id": item_id,
        "question": question,
        "expected_behavior": "answer",
        "question_type": "metadata",
        "expected_doc": expected_doc,
        "expected_answer": expected_answer,
        "gold_evidence": [{"label": evidence_label, "must_contain": must_contain}],
        "normalization": normalization,
    }


def generate(source_dir: Path, output_path: Path, include_out_of_scope: bool = True) -> int:
    rows: List[Dict] = []
    txt_files = sorted(source_dir.glob("*.txt"))

    for txt in txt_files:
        lines = _read_lines(txt)
        rel_path = f"docs/txt/{txt.name}"
        policy_name = _policy_name_from_path(txt)
        doc_name = txt.name
        stem_key = txt.stem.lower()

        pg = _extract_policy_group(lines)
        if pg:
            value, s, e = pg
            rows.append(
                _make_item(
                    item_id=f"silver_{stem_key}_policy_group",
                    question=f"What is the policy group for the {policy_name}?",
                    expected_doc=doc_name,
                    expected_answer=value,
                    evidence_label=_label(rel_path, s, e),
                    must_contain=["Policy Group", value],
                    normalization="strip_punct",
                )
            )

        rc = _extract_responsible_committee(lines)
        if rc:
            value, s, e = rc
            rows.append(
                _make_item(
                    item_id=f"silver_{stem_key}_responsible_committee",
                    question=f"What is the responsible committee for the {policy_name}?",
                    expected_doc=doc_name,
                    expected_answer=value,
                    evidence_label=_label(rel_path, s, e),
                    must_contain=["COMMITTEE", value],
                    normalization="uppercase",
                )
            )

        rg = _extract_review_guidance(lines)
        if rg:
            value, s, e = rg
            rows.append(
                _make_item(
                    item_id=f"silver_{stem_key}_review_guidance",
                    question=f"What is the next review date guidance for the {policy_name}?",
                    expected_doc=doc_name,
                    expected_answer=value,
                    evidence_label=_label(rel_path, s, e),
                    must_contain=["Next review date", "Annual or"],
                    normalization="strip_punct",
                )
            )

    if include_out_of_scope:
        rows.append(
            {
                "id": "silver_out_of_scope_kubernetes_autoscaler",
                "question": "Does this policy corpus include a built-in Kubernetes autoscaler?",
                "expected_behavior": "refuse",
                "question_type": "out_of_scope",
                "expected_answer": None,
                "gold_evidence": [],
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate silver evalset from policy metadata fields.")
    parser.add_argument("--source-dir", default=str(SOURCE_TXT_DIR), help="Directory with .txt policy files")
    parser.add_argument("--output", default=str(OUTPUT_PATH), help="Output JSONL path")
    parser.add_argument(
        "--no-out-of-scope",
        action="store_true",
        help="Do not append the out-of-scope refusal question",
    )
    args = parser.parse_args()

    count = generate(
        source_dir=Path(args.source_dir),
        output_path=Path(args.output),
        include_out_of_scope=(not args.no_out_of_scope),
    )
    print(f"Wrote {count} silver eval rows to {args.output}")


if __name__ == "__main__":
    main()
