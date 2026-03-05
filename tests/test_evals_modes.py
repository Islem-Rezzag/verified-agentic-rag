import json
from types import SimpleNamespace

import verified_agentic_rag.evals as evals
from verified_agentic_rag.retrieve import RetrievedChunk


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


def test_value_matches_canonical_aliases_bidirectionally():
    assert evals._value_matches(  # type: ignore[attr-defined]
        "The responsible committee is PERSONNEL.",
        expected_value="P&F",
        expected_value_regex=None,
    )
    assert evals._value_matches(  # type: ignore[attr-defined]
        "Approved by P&F.",
        expected_value="PERSONNEL",
        expected_value_regex=None,
    )


def test_answer_matches_expected_uses_alias_canonicalization():
    item = {
        "expected_answer": "P&F",
        "expected_answer_regex": None,
        "required_phrases": [],
        "acceptable_answers": [],
        "normalization": ["uppercase"],
    }
    assert evals._answer_matches_expected(  # type: ignore[attr-defined]
        item,
        "The responsible committee is PERSONNEL.",
    )

    reverse = dict(item)
    reverse["expected_answer"] = "PERSONNEL"
    assert evals._answer_matches_expected(  # type: ignore[attr-defined]
        reverse,
        "Approved by P&F.",
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


def test_run_eval_full_mode_computes_evidence_and_citation_overlap(tmp_path, monkeypatch):
    eval_path = tmp_path / "gold.jsonl"
    out_path = tmp_path / "results.json"
    eval_path.write_text(
        json.dumps(
            {
                "id": "q1",
                "question": "What is the responsible committee?",
                "expected_behavior": "answer",
                "question_type": "metadata",
                "expected_doc": "Data_Protection_-_Employees.txt",
                "expected_answer": "PERSONNEL",
                "gold_evidence": [
                    {"label": "docs/txt/Data_Protection_-_Employees.txt:1-120", "must_contain": ["PERSONNEL"]}
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_ask_question(cfg, question: str, debug: bool = False, no_llm: bool = False):
        return SimpleNamespace(
            retrieved=[
                _chunk(
                    chunk_id="c1",
                    text="RESPONSIBLE COMMITTEE: PERSONNEL",
                    rel_path="docs/txt/Data_Protection_-_Employees.txt",
                    start_line=1,
                    end_line=100,
                )
            ],
            answer=SimpleNamespace(
                answer="The responsible committee is PERSONNEL.[docs/txt/Data_Protection_-_Employees.txt:1-100]",
                cannot_answer=False,
                confidence="high",
                model_confidence="high",
                computed_confidence="high",
            ),
            verification={"all_supported": True},
            retrieval_trace=None,
        )

    monkeypatch.setattr(evals, "ask_question", fake_ask_question)
    monkeypatch.setattr(evals, "_build_corpus_cache", lambda cfg: {"docs/txt/a.txt": "PERSONNEL"})
    evals.run_eval(eval_path=str(eval_path), output_path=str(out_path), mode="full")

    row = json.loads(out_path.read_text(encoding="utf-8"))[0]
    assert row["evidence_recall_at_k"] == 1.0
    assert row["evidence_mrr"] == 1.0
    assert row["citation_overlaps_gold_evidence"] is True
    assert row["pass_citation_overlap_rule"] is True


def test_run_eval_retrieval_mode_flags_retrieval_missed_existing_value(tmp_path, monkeypatch):
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

    def fake_ask_question(cfg, question: str, debug: bool = False, no_llm: bool = False):
        return SimpleNamespace(
            retrieved=[
                _chunk(
                    chunk_id="c1",
                    text="This chunk does not include the expected value.",
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
            retrieval_trace=None,
        )

    monkeypatch.setattr(evals, "ask_question", fake_ask_question)
    monkeypatch.setattr(evals, "_build_corpus_cache", lambda cfg: {"docs/txt/full.txt": "PERSONNEL appears in corpus"})
    evals.run_eval(eval_path=str(eval_path), output_path=str(out_path), mode="retrieval")

    row = json.loads(out_path.read_text(encoding="utf-8"))[0]
    assert row["corpus_contains_expected_value"] is True
    assert row["retrieval_contains_expected_value"] is False
    assert row["retrieval_missed_existing_value"] is True


def test_run_eval_gold_silver_writes_combined_report(tmp_path, monkeypatch):
    gold_path = tmp_path / "gold.jsonl"
    silver_path = tmp_path / "silver.jsonl"
    out_path = tmp_path / "suite.json"

    gold_path.write_text(
        json.dumps(
            {
                "id": "gold1",
                "question": "What is the responsible committee?",
                "expected_behavior": "answer",
                "question_type": "metadata",
                "expected_doc": "Data_Protection_-_Employees.txt",
                "expected_answer": "PERSONNEL",
                "gold_evidence": [{"label": "docs/txt/Data_Protection_-_Employees.txt:1-120"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    silver_path.write_text(
        json.dumps(
            {
                "id": "silver1",
                "question": "Does this policy corpus include a Kubernetes autoscaler?",
                "expected_behavior": "refuse",
                "question_type": "out_of_scope",
                "expected_answer": None,
                "gold_evidence": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_ask_question(cfg, question: str, debug: bool = False, no_llm: bool = False):
        if "autoscaler" in question.lower():
            return SimpleNamespace(
                retrieved=[],
                answer=SimpleNamespace(
                    answer="LLM disabled. Showing retrieved sources only.",
                    cannot_answer=True,
                    confidence="low",
                    model_confidence="low",
                    computed_confidence="low",
                ),
                verification=None,
                retrieval_trace=None,
            )
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
            retrieval_trace=None,
        )

    monkeypatch.setattr(evals, "ask_question", fake_ask_question)
    monkeypatch.setattr(evals, "_build_corpus_cache", lambda cfg: {"docs/txt/a.txt": "PERSONNEL"})
    evals.run_eval_gold_silver(
        gold_path=str(gold_path),
        silver_path=str(silver_path),
        output_path=str(out_path),
        mode="retrieval",
    )

    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert "gold" in payload and "silver" in payload
    assert payload["gold"]["summary"]["count"] == 1
    assert payload["silver"]["summary"]["count"] == 1


def test_extract_gold_labels_ignores_none_expected_doc():
    labels = evals._extract_gold_labels(  # type: ignore[attr-defined]
        {"expected_doc": None, "gold_evidence": []}
    )
    assert labels == []


def test_evidence_metrics_ndcg_is_capped_with_duplicate_hits():
    metrics = evals._evidence_metrics(  # type: ignore[attr-defined]
        [
            "docs/txt/Policy.txt:1-50",
            "docs/txt/Policy.txt:51-100",
            "docs/txt/Policy.txt:101-150",
        ],
        ["docs/txt/Policy.txt:1-150"],
    )

    assert metrics["evidence_recall_at_k"] == 1.0
    assert metrics["evidence_mrr"] == 1.0
    assert metrics["evidence_ndcg_at_k"] == 1.0
    assert 0.0 <= (metrics["context_precision_ranked"] or 0.0) <= 1.0


def test_refuse_question_does_not_require_evidence_recall(tmp_path, monkeypatch):
    eval_path = tmp_path / "gold.jsonl"
    out_path = tmp_path / "results.json"
    eval_path.write_text(
        json.dumps(
            {
                "id": "q_refuse",
                "question": "Does this corpus include Kubernetes HPA?",
                "expected_behavior": "refuse",
                "question_type": "out_of_scope",
                "expected_doc": None,
                "gold_evidence": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_ask_question(cfg, question: str, debug: bool = False, no_llm: bool = False):
        return SimpleNamespace(
            retrieved=[],
            answer=SimpleNamespace(
                answer="I cannot answer from the repository based on the retrieved sources.",
                cannot_answer=True,
                confidence="low",
                model_confidence="low",
                computed_confidence="low",
            ),
            verification=None,
            retrieval_trace=None,
        )

    monkeypatch.setattr(evals, "ask_question", fake_ask_question)
    monkeypatch.setattr(evals, "_build_corpus_cache", lambda cfg: {"docs/txt/a.txt": "policy"})
    evals.run_eval(eval_path=str(eval_path), output_path=str(out_path), mode="full")

    row = json.loads(out_path.read_text(encoding="utf-8"))[0]
    assert row["evidence_recall_at_k"] is None
    assert row["pass_evidence_recall_rule"] is True
    assert row["pass_overall"] is True


def test_required_phrases_can_match_cited_evidence(tmp_path, monkeypatch):
    eval_path = tmp_path / "gold.jsonl"
    out_path = tmp_path / "results.json"
    eval_path.write_text(
        json.dumps(
            {
                "id": "q_required_phrases",
                "question": "What must staff do?",
                "expected_behavior": "answer",
                "question_type": "procedure",
                "expected_doc": "Policy.txt",
                "expected_answer": None,
                "required_phrases": ["must notify", "line manager"],
                "gold_evidence": [{"label": "docs/txt/Policy.txt:101-120"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_ask_question(cfg, question: str, debug: bool = False, no_llm: bool = False):
        return SimpleNamespace(
            retrieved=[
                _chunk(
                    chunk_id="c1",
                    text="Employees must notify the line manager immediately.",
                    rel_path="docs/txt/Policy.txt",
                    start_line=101,
                    end_line=120,
                )
            ],
            answer=SimpleNamespace(
                answer="Employees should inform their supervisor promptly.[docs/txt/Policy.txt:101-120]",
                cannot_answer=False,
                confidence="high",
                model_confidence="high",
                computed_confidence="high",
            ),
            verification={"all_supported": True},
            retrieval_trace=None,
        )

    monkeypatch.setattr(evals, "ask_question", fake_ask_question)
    monkeypatch.setattr(evals, "_build_corpus_cache", lambda cfg: {"docs/txt/Policy.txt": "Employees must notify line manager."})
    evals.run_eval(eval_path=str(eval_path), output_path=str(out_path), mode="full")

    row = json.loads(out_path.read_text(encoding="utf-8"))[0]
    assert row["answer_matches_expected_value"] is True
    assert row["pass_expected_value_rule"] is True
    assert row["pass_overall"] is True


def test_gold_evidence_labels_alias_is_supported():
    labels = evals._extract_gold_labels(  # type: ignore[attr-defined]
        {
            "gold_evidence_labels": ["docs/txt/Policy.txt:1-120"],
            "gold_evidence": [],
        }
    )
    assert labels == ["docs/txt/Policy.txt:1-120"]

