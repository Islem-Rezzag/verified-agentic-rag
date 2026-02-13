from __future__ import annotations

from verified_agentic_rag.agentic import (
    _extract_policy_field_with_doc_scan,
    _heuristic_retrieval_relevant,
    _question_has_policy_context,
)
from verified_agentic_rag.retrieve import RetrievedChunk


def _chunk(
    *,
    chunk_id: str,
    text: str,
    rel_path: str,
    start_line: int = 1,
    end_line: int = 120,
    chunk_type: str = "body",
    similarity: float = 0.6,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        text=text,
        rel_path=rel_path,
        start_line=start_line,
        end_line=end_line,
        chunk_type=chunk_type,  # type: ignore[arg-type]
        distance=1.0 - similarity,
        similarity=similarity,
        dense_rank=1,
        sparse_rank=1,
        fusion_score=0.03,
        rerank_score=0.5,
    )


class _FakeRetriever:
    def __init__(self, by_doc):
        self.by_doc = by_doc

    def get_document_chunks(self, rel_path: str):
        return list(self.by_doc.get(rel_path, []))


def test_question_policy_context_blocks_offtopic_version_queries():
    retrieved = [
        _chunk(
            chunk_id="h1",
            text="Version 2025 Approved by P&F",
            rel_path="docs/txt/Equality_Diversity.txt",
            chunk_type="header",
        )
    ]

    assert _question_has_policy_context(
        "What is the latest version of the OpenAI API?",
        retrieved,
    ) is False

    assert _question_has_policy_context(
        "What is the policy group for the Equality & Diversity Policy?",
        retrieved,
    ) is True


def test_doc_scan_prefers_question_target_document_for_metadata_extraction():
    wrong_doc_header = _chunk(
        chunk_id="dp_h",
        chunk_type="header",
        rel_path="docs/txt/Data_Protection_-_Employees.txt",
        text="RESPONSIBLE COMMITTEE: PERSONNEL",
    )
    target_doc_header = _chunk(
        chunk_id="it_h",
        chunk_type="header",
        rel_path="docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt",
        text="RESPONSIBLE COMMITTEE: P&F",
    )

    retrieved = [wrong_doc_header, target_doc_header]
    retriever = _FakeRetriever(
        {
            "docs/txt/Provision_of_IT_Acceptable_Use_Policy_Employees_Members.txt": [target_doc_header],
            "docs/txt/Data_Protection_-_Employees.txt": [wrong_doc_header],
        }
    )

    match = _extract_policy_field_with_doc_scan(
        question="Which committee is responsible for Provision of IT Acceptable Use Policy Employees Members?",
        retrieved=retrieved,
        retriever=retriever,  # type: ignore[arg-type]
    )

    assert match is not None
    assert match.value == "P&F"
    assert "Provision_of_IT_Acceptable_Use_Policy_Employees_Members" in match.label


def test_heuristic_relevance_requires_policy_context():
    retrieved = [
        _chunk(
            chunk_id="a1",
            rel_path="docs/txt/Data_Protection_-_Employees.txt",
            text="Policy Group: Employees",
            chunk_type="header",
            similarity=0.62,
        ),
        _chunk(
            chunk_id="a2",
            rel_path="docs/txt/Data_Protection_-_Employees.txt",
            text="Current Document Status ...",
            similarity=0.60,
        ),
        _chunk(
            chunk_id="a3",
            rel_path="docs/txt/Data_Protection_-_Employees.txt",
            text="Document Retention Period ...",
            similarity=0.58,
        ),
    ]

    assert _heuristic_retrieval_relevant(
        "Name two lawful bases from the Data Protection - Employees policy.",
        retrieved,
    ) is True

    assert _heuristic_retrieval_relevant(
        "What is the latest version of the OpenAI API?",
        retrieved,
    ) is False
