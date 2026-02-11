from pathlib import Path
from types import SimpleNamespace

from app.retrieve import Retriever
from app.sparse import BM25SparseIndex, SparseChunk


def _cfg(**overrides):
    base = dict(
        hybrid_retrieval=True,
        sparse_retrieval=True,
        dense_candidates_k=30,
        sparse_candidates_k=30,
        fused_candidates_k=30,
        rrf_k=60,
        rerank_enabled=False,
        reranker_model="",
        reranker_batch_size=16,
        reranker_max_chars=1200,
        max_chunks_per_doc=3,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


class FakeIndex:
    def __init__(self, query_result, all_chunks=None, key_name: str = "fake"):
        self._query_result = query_result
        self._all_chunks = all_chunks or {"ids": [], "documents": [], "metadatas": []}
        self.persist_dir = Path(f"data/vector_store/{key_name}")
        self.collection_name = f"{key_name}_collection"

    def query(self, query_text: str, top_k: int):
        return self._query_result

    def get_all_chunks(self):
        return self._all_chunks


class FakeReranker:
    def __init__(self, scores):
        self.scores = scores

    def score(self, query: str, texts):
        return [self.scores[t] for t in texts]


def test_bm25_prefers_exact_field_header_chunk():
    idx = BM25SparseIndex(
        chunks=[
            SparseChunk(
                chunk_id="h1",
                text="Policy Group: Employees/Members Responsible Committee: Personnel",
                rel_path="docs/txt/policy_a.txt",
                start_line=1,
                end_line=20,
                chunk_type="header",
                source="src",
            ),
            SparseChunk(
                chunk_id="b1",
                text="General body paragraph about council guidance and procedures.",
                rel_path="docs/txt/policy_a.txt",
                start_line=21,
                end_line=80,
                chunk_type="body",
                source="src",
            ),
        ]
    )

    hits = idx.search("Responsible Committee", top_k=2)

    assert hits
    assert hits[0].chunk_id == "h1"


def test_hybrid_retrieval_includes_sparse_only_candidate_after_fusion():
    dense_res = {
        "ids": [["a", "b"]],
        "documents": [["semantic policy answer chunk", "another chunk"]],
        "metadatas": [[
            {"rel_path": "docs/txt/doc_a.txt", "start_line": 1, "end_line": 120, "chunk_type": "body"},
            {"rel_path": "docs/txt/doc_b.txt", "start_line": 1, "end_line": 120, "chunk_type": "body"},
        ]],
        "distances": [[0.2, 0.25]],
    }
    all_chunks = {
        "ids": ["a", "b", "c"],
        "documents": [
            "semantic policy answer chunk",
            "another chunk",
            "Responsible Committee: Personnel",
        ],
        "metadatas": [
            {"rel_path": "docs/txt/doc_a.txt", "start_line": 1, "end_line": 120, "chunk_type": "body"},
            {"rel_path": "docs/txt/doc_b.txt", "start_line": 1, "end_line": 120, "chunk_type": "body"},
            {"rel_path": "docs/txt/doc_c.txt", "start_line": 1, "end_line": 40, "chunk_type": "header"},
        ],
    }
    idx = FakeIndex(dense_res, all_chunks=all_chunks, key_name="hybrid_test")
    retriever = Retriever(
        index=idx,
        cfg=_cfg(
            dense_candidates_k=2,
            sparse_candidates_k=3,
            fused_candidates_k=3,
            rerank_enabled=False,
            max_chunks_per_doc=10,
        ),
    )

    out = retriever.retrieve("What is the responsible committee?", top_k=2)
    ids = [c.chunk_id for c in out]

    assert "c" in ids


def test_reranker_can_reorder_fused_candidates():
    dense_res = {
        "ids": [["a", "b"]],
        "documents": [["candidate A text", "candidate B text"]],
        "metadatas": [[
            {"rel_path": "docs/txt/doc_a.txt", "start_line": 1, "end_line": 120, "chunk_type": "body"},
            {"rel_path": "docs/txt/doc_b.txt", "start_line": 1, "end_line": 120, "chunk_type": "body"},
        ]],
        "distances": [[0.1, 0.2]],
    }
    idx = FakeIndex(dense_res, key_name="rerank_test")
    reranker = FakeReranker({"candidate A text": 0.2, "candidate B text": 0.9})
    retriever = Retriever(
        index=idx,
        cfg=_cfg(
            hybrid_retrieval=False,
            sparse_retrieval=False,
            rerank_enabled=True,
            reranker_model="fake",
            max_chunks_per_doc=10,
        ),
        reranker=reranker,
    )

    out = retriever.retrieve("query", top_k=2)

    assert [c.chunk_id for c in out] == ["b", "a"]
    assert out[0].rerank_score == 0.9


def test_doc_cap_limits_redundancy_unless_specific_policy_is_mentioned():
    dense_res = {
        "ids": [["a1", "a2", "a3", "b1"]],
        "documents": [["A1", "A2", "A3", "B1"]],
        "metadatas": [[
            {
                "rel_path": "docs/txt/Data_Protection_-_Employees.txt",
                "start_line": 1,
                "end_line": 100,
                "chunk_type": "header",
            },
            {
                "rel_path": "docs/txt/Data_Protection_-_Employees.txt",
                "start_line": 101,
                "end_line": 220,
                "chunk_type": "body",
            },
            {
                "rel_path": "docs/txt/Data_Protection_-_Employees.txt",
                "start_line": 221,
                "end_line": 340,
                "chunk_type": "body",
            },
            {
                "rel_path": "docs/txt/Recruitment_and_Selection_Policy.txt",
                "start_line": 1,
                "end_line": 120,
                "chunk_type": "header",
            },
        ]],
        "distances": [[0.1, 0.12, 0.13, 0.2]],
    }

    idx = FakeIndex(dense_res, key_name="cap_test")
    retriever = Retriever(
        index=idx,
        cfg=_cfg(
            hybrid_retrieval=False,
            sparse_retrieval=False,
            rerank_enabled=False,
            dense_candidates_k=4,
            max_chunks_per_doc=2,
        ),
    )

    generic = retriever.retrieve("What is the review frequency?", top_k=4)
    assert len([c for c in generic if "Data_Protection_-_Employees" in c.rel_path]) == 2

    specific = retriever.retrieve("For Data Protection - Employees, what is the review frequency?", top_k=4)
    assert len([c for c in specific if "Data_Protection_-_Employees" in c.rel_path]) == 3
