from types import SimpleNamespace

from verified_agentic_rag.generate import LLMClient
from verified_agentic_rag.policy_fields import detect_policy_field_question, extract_policy_field
from verified_agentic_rag.retrieve import RetrievedChunk
from verified_agentic_rag.verify import verify_answer_grounding


def _chunk(
    *,
    chunk_id: str,
    text: str,
    rel_path: str = "docs/txt/policy.txt",
    start_line: int = 1,
    end_line: int = 120,
    chunk_type: str = "body",
):
    return RetrievedChunk(
        chunk_id=chunk_id,
        text=text,
        rel_path=rel_path,
        start_line=start_line,
        end_line=end_line,
        chunk_type=chunk_type,  # type: ignore[arg-type]
        distance=0.2,
        similarity=0.8,
        dense_rank=1,
        sparse_rank=1,
        fusion_score=0.03,
        rerank_score=0.7,
    )


def test_policy_field_extraction_prefers_header_chunk():
    chunks = [
        _chunk(
            chunk_id="b1",
            chunk_type="body",
            text="This section discusses process and governance in detail.",
            start_line=101,
            end_line=220,
        ),
        _chunk(
            chunk_id="h1",
            chunk_type="header",
            text="Policy Group: Employees/Members\nRESPONSIBLE COMMITTEE: PERSONNEL",
            start_line=1,
            end_line=100,
        ),
    ]

    match = extract_policy_field(
        question="What is the responsible committee for this policy?",
        chunks=chunks,
    )

    assert match is not None
    assert match.field_key == "responsible_committee"
    assert match.value.lower() == "personnel"
    assert match.chunk.chunk_type == "header"


def test_verify_answer_grounding_marks_supported_metadata_claim():
    chunk = _chunk(
        chunk_id="h1",
        chunk_type="header",
        text="RESPONSIBLE COMMITTEE: PERSONNEL",
        rel_path="docs/txt/Data_Protection_-_Employees.txt",
        start_line=1,
        end_line=100,
    )
    answer = (
        "The responsible committee is PERSONNEL."
        "[docs/txt/Data_Protection_-_Employees.txt:1-100]"
    )

    result = verify_answer_grounding(
        question="What is the responsible committee?",
        answer_text=answer,
        retrieved=[chunk],
    )

    assert result.all_supported is True
    assert len(result.checks) == 1
    assert result.checks[0].supported is True


def test_verify_answer_grounding_flags_unsupported_sentence():
    chunk = _chunk(
        chunk_id="h1",
        chunk_type="header",
        text="Policy Group: Employees/Members",
        rel_path="docs/txt/Policy.txt",
        start_line=1,
        end_line=100,
    )
    answer = (
        "The policy includes a built-in Kubernetes autoscaler."
        "[docs/txt/Policy.txt:1-100]"
    )

    result = verify_answer_grounding(
        question="Does this policy include Kubernetes autoscaler?",
        answer_text=answer,
        retrieved=[chunk],
    )

    assert result.all_supported is False
    assert result.unsupported_sentences


def test_grade_retrieval_filters_nonexistent_supporting_labels():
    class FakeLLM:
        def complete(self, system: str, user: str) -> str:
            return (
                '{"relevant": true, "reason": "explicit field present", '
                '"supporting_labels": ["docs/txt/Policy.txt:1-120", "bad:1-2"], '
                '"suggested_rewrite": ""}'
            )

    client = object.__new__(LLMClient)
    client.cfg = SimpleNamespace()
    client.llm = FakeLLM()

    chunks = [
        _chunk(
            chunk_id="x1",
            text="Policy Group: Employees/Members",
            rel_path="docs/txt/Policy.txt",
            start_line=1,
            end_line=120,
        )
    ]

    grade = client.grade_retrieval("What is the policy group?", chunks)

    assert grade.relevant is True
    assert grade.supporting_labels == ["docs/txt/Policy.txt:1-120"]


def test_detect_policy_field_question():
    field = detect_policy_field_question("What is the review frequency for this policy?")
    assert field is not None
    assert field[0] == "review_frequency"


def test_extract_policy_field_handles_interleaved_status_table_text():
    chunk = _chunk(
        chunk_id="h2",
        chunk_type="header",
        rel_path="docs/txt/Data_Protection_-_Employees.txt",
        start_line=1,
        end_line=120,
        text=(
            "Current Document Status\n"
            "164/24/25a(2) Annual or if\n"
            "Minute no. Next review date required by\n"
            "legislation"
        ),
    )

    match = extract_policy_field(
        question="What is the review frequency (or next review date guidance)?",
        chunks=[chunk],
    )

    assert match is not None
    assert match.field_key == "review_frequency"
    assert match.value == "Annual or if required by legislation"


def test_extract_policy_field_handles_as_required_variants():
    chunk = _chunk(
        chunk_id="h3",
        chunk_type="header",
        rel_path="docs/txt/Employee_Handbook.txt",
        start_line=1,
        end_line=120,
        text="Next review date Annual or as required by legislation",
    )

    match = extract_policy_field(
        question="What is the next review date guidance for the Employee Handbook?",
        chunks=[chunk],
    )

    assert match is not None
    assert match.field_key == "review_frequency"
    assert match.value == "Annual or as required by legislation"


def test_extract_policy_field_handles_interleaved_as_required_table_text():
    chunk = _chunk(
        chunk_id="h4",
        chunk_type="header",
        rel_path="docs/txt/Recruitment_and_Selection_Policy.txt",
        start_line=1,
        end_line=120,
        text=(
            "Current Document Status\n"
            "Annual or as\n"
            "Minute no. 146/25/26 Next review date required by\n"
            "legislation"
        ),
    )

    match = extract_policy_field(
        question="What is the next review date guidance for the Recruitment and Selection Policy?",
        chunks=[chunk],
    )

    assert match is not None
    assert match.field_key == "review_frequency"
    assert match.value == "Annual or as required by legislation"

