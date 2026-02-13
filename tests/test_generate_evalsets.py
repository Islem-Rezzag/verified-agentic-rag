from pathlib import Path
import json

import scripts.generate_evalsets as ges


def _read_jsonl(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def test_generate_evalsets_outputs_expected_shapes(tmp_path: Path):
    source = tmp_path / "docs" / "txt"
    source.mkdir(parents=True, exist_ok=True)
    policy = source / "Policy_A.txt"
    policy.write_text(
        "\n".join(
            [
                "Policy Group: Employees",
                "RESPONSIBLE COMMITTEE: PERSONNEL",
                "Current Document Status",
                "Version 2025 Approved by P&F",
                "Date 11.03.2025 Responsible Officer AJT",
                "Minute no. 164/24/25a(2) Next review date Annual or if required by legislation",
                "Document Retention Period",
                "Until superseded",
                "",
                "Employees must notify the line manager immediately.",
            ]
        ),
        encoding="utf-8",
    )

    silver_out = tmp_path / "silver.jsonl"
    gold_out = tmp_path / "gold.jsonl"

    silver_count, _docs = ges.generate_silver(
        source_dir=source,
        output_path=silver_out,
        variants_per_field=2,
        out_of_scope_count=2,
    )
    assert silver_count >= 10
    silver_rows = _read_jsonl(silver_out)
    assert any(r["question_type"] == "metadata" for r in silver_rows)
    assert any(r["question_type"] == "out_of_scope" for r in silver_rows)
    sample_meta = next(r for r in silver_rows if r["question_type"] == "metadata")
    assert "gold_evidence_labels" in sample_meta
    assert "gold_evidence" in sample_meta

    gold_count, _docs = ges.generate_gold(
        source_dir=source,
        output_path=gold_out,
        metadata_target=6,
        narrative_target=0,
        out_of_scope_target=1,
    )
    assert gold_count == 7
    gold_rows = _read_jsonl(gold_out)
    assert any(r["question_type"] == "metadata" for r in gold_rows)
    assert any(r["question_type"] == "out_of_scope" for r in gold_rows)
