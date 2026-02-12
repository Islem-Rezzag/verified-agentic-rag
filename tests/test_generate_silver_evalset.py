from pathlib import Path

import scripts.generate_silver_evalset as gse


def test_extract_policy_group_handles_split_value_line():
    lines = [
        "Policy Group:",
        "Employees/Members",
    ]
    out = gse._extract_policy_group(lines)
    assert out is not None
    assert out[0] == "Employees/Members"


def test_extract_review_guidance_handles_interleaved_table_text():
    lines = [
        "Current Document Status",
        "164/24/25a(2) Annual or if",
        "Minute no. Next review date required by",
        "legislation",
    ]
    out = gse._extract_review_guidance(lines)
    assert out is not None
    assert out[0] == "Annual or if required by legislation"


def test_generate_creates_rows_for_single_policy(tmp_path: Path):
    source = tmp_path / "docs" / "txt"
    source.mkdir(parents=True, exist_ok=True)
    policy = source / "Policy_A.txt"
    policy.write_text(
        "\n".join(
            [
                "Policy Group: Employees",
                "RESPONSIBLE COMMITTEE: PERSONNEL",
                "Next review date Annual or as required",
            ]
        ),
        encoding="utf-8",
    )

    out = tmp_path / "silver.jsonl"
    count = gse.generate(source_dir=source, output_path=out, include_out_of_scope=False)

    assert count == 3
    text = out.read_text(encoding="utf-8")
    assert "policy_group" in text
    assert "responsible_committee" in text
    assert "review_guidance" in text
