from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterable, List, Optional, Tuple

from .index import VectorIndex

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


@dataclass(frozen=True)
class SparseChunk:
    chunk_id: str
    text: str
    rel_path: str
    start_line: int
    end_line: int
    chunk_type: str
    source: str


@dataclass(frozen=True)
class SparseHit:
    chunk_id: str
    score: float
    rank: int


class BM25SparseIndex:
    """
    Lightweight in-memory BM25 index over chunk texts.
    """

    _GLOBAL_CACHE: Dict[str, "BM25SparseIndex"] = {}

    def __init__(self, chunks: List[SparseChunk], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.chunks = chunks
        self.by_id: Dict[str, SparseChunk] = {c.chunk_id: c for c in chunks}
        self._idf: Dict[str, float] = {}
        self._postings: DefaultDict[str, List[Tuple[int, int]]] = defaultdict(list)
        self._doc_lens: List[int] = []
        self._avg_doc_len: float = 1.0
        self._build()

    @classmethod
    def from_vector_index(cls, index: VectorIndex) -> "BM25SparseIndex":
        key = f"{index.persist_dir}|{index.collection_name}"
        cached = cls._GLOBAL_CACHE.get(key)
        if cached is not None:
            return cached

        raw = index.get_all_chunks()
        ids = raw.get("ids") or []
        docs = raw.get("documents") or []
        metas = raw.get("metadatas") or []

        chunks: List[SparseChunk] = []
        for chunk_id, doc, meta in zip(ids, docs, metas):
            meta = meta or {}
            chunks.append(
                SparseChunk(
                    chunk_id=str(chunk_id),
                    text=str(doc or ""),
                    rel_path=str(meta.get("rel_path", "")),
                    start_line=int(meta.get("start_line", 0)),
                    end_line=int(meta.get("end_line", 0)),
                    chunk_type=str(meta.get("chunk_type", "body")),
                    source=str(meta.get("source", "")),
                )
            )

        built = cls(chunks=chunks)
        cls._GLOBAL_CACHE[key] = built
        return built

    def _build(self) -> None:
        n_docs = len(self.chunks)
        if n_docs == 0:
            return

        doc_freq: Counter[str] = Counter()

        for i, chunk in enumerate(self.chunks):
            tokens = tokenize(chunk.text)
            tf = Counter(tokens)
            self._doc_lens.append(len(tokens))
            for term, freq in tf.items():
                self._postings[term].append((i, freq))
            doc_freq.update(tf.keys())

        self._avg_doc_len = max(1.0, sum(self._doc_lens) / n_docs)
        for term, df in doc_freq.items():
            # Okapi BM25 idf
            self._idf[term] = math.log(1.0 + ((n_docs - df + 0.5) / (df + 0.5)))

    def search(self, query: str, top_k: int) -> List[SparseHit]:
        if top_k <= 0 or not self.chunks:
            return []

        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        scores: Dict[int, float] = defaultdict(float)
        for term in q_tokens:
            idf = self._idf.get(term)
            if idf is None:
                continue
            for doc_idx, tf in self._postings.get(term, []):
                doc_len = self._doc_lens[doc_idx]
                norm = 1.0 - self.b + self.b * (doc_len / self._avg_doc_len)
                numer = tf * (self.k1 + 1.0)
                denom = tf + self.k1 * norm
                scores[doc_idx] += idf * (numer / denom)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        hits: List[SparseHit] = []
        for rank, (doc_idx, score) in enumerate(ranked, start=1):
            if score <= 0:
                continue
            hits.append(SparseHit(chunk_id=self.chunks[doc_idx].chunk_id, score=float(score), rank=rank))
        return hits

    def get_chunk(self, chunk_id: str) -> Optional[SparseChunk]:
        return self.by_id.get(chunk_id)
