from pathlib import Path

from verified_agentic_rag.chunking import Chunk, chunk_lines
from verified_agentic_rag.index import VectorIndex


def _lines(n: int):
    return [f"line {i}\n" for i in range(1, n + 1)]


def test_chunk_lines_emits_header_then_body_windows():
    chunks = list(
        chunk_lines(
            lines=_lines(250),
            rel_path="docs/txt/policy.txt",
            source="saltash_policy_pack",
            chunk_size_lines=120,
            overlap_lines=20,
            header_chunk_lines=100,
        )
    )

    assert chunks[0].chunk_type == "header"
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 100
    assert ":header:" in chunks[0].chunk_id

    body_chunks = [c for c in chunks if c.chunk_type == "body"]
    assert len(body_chunks) == 3
    assert [(c.start_line, c.end_line) for c in body_chunks] == [(1, 120), (101, 220), (201, 250)]
    assert all(":body:" in c.chunk_id for c in body_chunks)


def test_chunk_lines_without_header_only_emits_body():
    chunks = list(
        chunk_lines(
            lines=_lines(40),
            rel_path="docs/txt/policy.txt",
            source="saltash_policy_pack",
            chunk_size_lines=20,
            overlap_lines=5,
            header_chunk_lines=0,
        )
    )
    assert chunks
    assert all(c.chunk_type == "body" for c in chunks)


def test_upsert_chunks_stores_chunk_type_metadata(monkeypatch, tmp_path: Path):
    class FakeCollection:
        def __init__(self):
            self.calls = []

        def upsert(self, **kwargs):
            self.calls.append(kwargs)

    class FakeEmbedder:
        def embed_texts(self, texts, batch_size=32):
            return [[0.1, 0.2] for _ in texts]

    idx = VectorIndex(
        persist_dir=tmp_path / "vector_store",
        collection_name="test_collection",
        embedding_model="dummy-model",
    )
    fake_collection = FakeCollection()

    monkeypatch.setattr(idx, "_get_collection", lambda: fake_collection)
    idx.embedder = FakeEmbedder()

    chunks = [
        Chunk(
            chunk_id="src:docs/txt/policy.txt:header:1-100:0",
            text="header text",
            rel_path="docs/txt/policy.txt",
            start_line=1,
            end_line=100,
            source="src",
            chunk_type="header",
        ),
        Chunk(
            chunk_id="src:docs/txt/policy.txt:body:1-120:0",
            text="body text",
            rel_path="docs/txt/policy.txt",
            start_line=1,
            end_line=120,
            source="src",
            chunk_type="body",
        ),
    ]

    total = idx.upsert_chunks(chunks, batch_size=64)

    assert total == 2
    assert len(fake_collection.calls) == 1
    metadatas = fake_collection.calls[0]["metadatas"]
    assert metadatas[0]["chunk_type"] == "header"
    assert metadatas[1]["chunk_type"] == "body"

