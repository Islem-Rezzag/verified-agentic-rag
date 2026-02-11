import json
from types import SimpleNamespace

import app.evals as evals
from app.retrieve import RetrievedChunk


def _chunk(
    *,
    chunk_id: str,
    text: str,
    rel_path: str,
    start_line: int = 1,
    end_line: int = 120,
):
    return RetrievedChunk(
        chunk_id=chunk_id,
        text=text,
        rel_path=rel_path,
        start_line=start_line,
        end_line=end_line,
        chunk_type="header",
        distance=0.1,
        similarity=0.9,
        dense_rank=1,
        sparse_rank=1,
        fusion_score=0.03,
        rerank_score=0.7,
    )


def test_doc_and_value_matching_helpers():
    assert evals._doc_matches_expected(  # type: ignore[attr-defined]
        "docs/txt/Data_Protection_-_Employees.txt",
        "Data_Protection_-_Employees.txt",
    )
    assert evals._value_matches(  # type: ignore[attr-defined]
        "The responsible committee is PERSONNEL.",
        expected_value="personnel",
        expected_value_regex=None,
    )
    assert evals._value_matches(  # type: ignore[attr-defined]
        "Annual or if required by legislation",
        expected_value=None,
        expected_value_regex=r"annual\s+or\s+if\s+required\s+by\s+legislation",
    )


def test_run_eval_retrieval_mode(tmp_path, monkeypatch):
    eval_path = tmp_path / "questions.jsonl"
    out_path = tmp_path / "results.json"
    eval_path.write_text(
        json.dumps(
            {
                "question": "What is the responsible committee?",
                "expected": "answer",
                "expected_doc": "Data_Protection_-_Employees.txt",
                "expected_value": "PERSONNEL",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    calls = []

    def fake_ask_question(cfg, question: str, debug: bool = False, no_llm: bool = False):
        calls.append(no_llm)
        return SimpleNamespace(
            retrieved=[
                _chunk(
                    chunk_id="c1",
                    text="RESPONSIBLE COMMITTEE: PERSONNEL",
                    rel_path="docs/txt/Data_Protection_-_Employees.txt",
                )
            ],
            answer=SimpleNamespace(
                answer="LLM disabled. Showing retrieved sources only.",
                cannot_answer=True,
                confidence="low",
                model_confidence="low",
                computed_confidence="low",
            ),
            verification=None,
        )

    monkeypatch.setattr(evals, "ask_question", fake_ask_question)
    evals.run_eval(eval_path=str(eval_path), output_path=str(out_path), mode="retrieval")

    rows = json.loads(out_path.read_text(encoding="utf-8"))
    row = rows[0]

    assert calls == [True]
    assert row["mode"] == "retrieval"
    assert row["pass_refusal_rule"] is None
    assert row["pass_citation_rule"] is None
    assert row["pass_expected_doc_rule"] is True
    assert row["pass_expected_value_rule"] is True
    assert row["pass_overall"] is True


def test_run_eval_full_mode_checks_verification(tmp_path, monkeypatch):
    eval_path = tmp_path / "questions.jsonl"
    out_path = tmp_path / "results.json"
    eval_path.write_text(
        json.dumps(
            {
                "question": "What is the responsible committee?",
                "expected": "answer",
                "expected_doc": "Data_Protection_-_Employees.txt",
                "expected_value": "PERSONNEL",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    calls = []

    def fake_ask_question(cfg, question: str, debug: bool = False, no_llm: bool = False):
        calls.append(no_llm)
        return SimpleNamespace(
            retrieved=[
                _chunk(
                    chunk_id="c1",
                    text="RESPONSIBLE COMMITTEE: PERSONNEL",
                    rel_path="docs/txt/Data_Protection_-_Employees.txt",
                )
            ],
            answer=SimpleNamespace(
                answer="The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-120]",
                cannot_answer=False,
                confidence="high",
                model_confidence="high",
                computed_confidence="high",
            ),
            verification={"all_supported": True},
        )

    monkeypatch.setattr(evals, "ask_question", fake_ask_question)
    evals.run_eval(eval_path=str(eval_path), output_path=str(out_path), mode="full")

    rows = json.loads(out_path.read_text(encoding="utf-8"))
    row = rows[0]

    assert calls == [False]
    assert row["mode"] == "full"
    assert row["pass_refusal_rule"] is True
    assert row["pass_citation_rule"] is True
    assert row["pass_expected_doc_rule"] is True
    assert row["pass_expected_value_rule"] is True
    assert row["pass_verification_rule"] is True
    assert row["pass_overall"] is True
