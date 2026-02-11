from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Literal, Optional

from .config import AppConfig
from .index import VectorIndex
from .rerank import CrossEncoderReranker
from .sparse import BM25SparseIndex

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "this",
    "that",
    "policy",
    "document",
    "employees",
    "employee",
    "members",
    "member",
    "council",
    "town",
}


@dataclass(frozen=True)
class RetrievedChunk:
    """
    A chunk returned by the retriever.

    distance: lower is better (for cosine distance in Chroma).
    similarity: higher is better (we compute 1 - distance).
    """
    chunk_id: str
    text: str
    rel_path: str
    start_line: int
    end_line: int
    chunk_type: Literal["header", "body"]
    distance: float
    similarity: float
    dense_rank: Optional[int] = None
    sparse_rank: Optional[int] = None
    fusion_score: Optional[float] = None
    rerank_score: Optional[float] = None


@dataclass
class _CandidateChunk:
    chunk_id: str
    text: str
    rel_path: str
    start_line: int
    end_line: int
    chunk_type: Literal["header", "body"]
    distance: float
    similarity: float
    dense_rank: Optional[int] = None
    sparse_rank: Optional[int] = None
    fusion_score: float = 0.0
    rerank_score: Optional[float] = None


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _question_mentions_doc(question: str, rel_path: str) -> bool:
    q = _norm(question)
    title = _norm(Path(rel_path).stem.replace("_", " ").replace("-", " "))
    if not q or not title:
        return False

    if title in q:
        return True

    q_tokens = set(q.split())
    title_tokens = [t for t in title.split() if len(t) > 2 and t not in STOPWORDS]
    if len(title_tokens) < 2:
        return False

    hits = sum(1 for t in title_tokens if t in q_tokens)
    required = min(3, len(title_tokens))
    return hits >= required


def _apply_doc_cap(question: str, chunks: List[RetrievedChunk], max_per_doc: int) -> List[RetrievedChunk]:
    if max_per_doc <= 0:
        return chunks

    exempt_docs = {c.rel_path for c in chunks if _question_mentions_doc(question, c.rel_path)}
    if not chunks:
        return chunks

    out: List[RetrievedChunk] = []
    counts: Counter[str] = Counter()
    for c in chunks:
        if c.rel_path in exempt_docs:
            out.append(c)
            continue
        if counts[c.rel_path] >= max_per_doc:
            continue
        counts[c.rel_path] += 1
        out.append(c)
    return out


def _rrf_score(rank: int, rrf_k: int) -> float:
    return 1.0 / (rrf_k + rank)


class Retriever:
    def __init__(
        self,
        index: VectorIndex,
        cfg: Optional[AppConfig] = None,
        sparse_index: Optional[BM25SparseIndex] = None,
        reranker: Optional[CrossEncoderReranker] = None,
    ) -> None:
        self.index = index
        self.cfg = cfg or AppConfig()
        self._sparse_index = sparse_index
        self._reranker = reranker

        if self._reranker is None and self.cfg.rerank_enabled and self.cfg.reranker_model:
            self._reranker = CrossEncoderReranker(
                model_name=self.cfg.reranker_model,
                batch_size=self.cfg.reranker_batch_size,
            )

    def _ensure_sparse_index(self) -> Optional[BM25SparseIndex]:
        if (not self.cfg.hybrid_retrieval) or (not self.cfg.sparse_retrieval):
            return None
        if self._sparse_index is None:
            self._sparse_index = BM25SparseIndex.from_vector_index(self.index)
        return self._sparse_index

    def _dense_candidates(self, query: str, dense_k: int) -> Dict[str, _CandidateChunk]:
        res = self.index.query(query_text=query, top_k=dense_k)

        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        ids = (res.get("ids") or [["" for _ in docs]])[0]

        out: Dict[str, _CandidateChunk] = {}
        for rank, (chunk_id, doc, meta, dist) in enumerate(zip(ids, docs, metas, dists), start=1):
            meta = meta or {}
            chunk_type = str(meta.get("chunk_type", "body")).lower()
            if chunk_type not in {"header", "body"}:
                chunk_type = "body"
            out[str(chunk_id)] = _CandidateChunk(
                chunk_id=str(chunk_id),
                text=str(doc),
                rel_path=str(meta.get("rel_path", "")),
                start_line=int(meta.get("start_line", 0)),
                end_line=int(meta.get("end_line", 0)),
                chunk_type=chunk_type,  # type: ignore[arg-type]
                distance=float(dist),
                similarity=float(1.0 - float(dist)),
                dense_rank=rank,
            )
        return out

    def _add_sparse_candidates(
        self,
        query: str,
        candidates: Dict[str, _CandidateChunk],
    ) -> None:
        sparse_idx = self._ensure_sparse_index()
        if sparse_idx is None:
            return

        sparse_hits = sparse_idx.search(query, top_k=self.cfg.sparse_candidates_k)
        for hit in sparse_hits:
            existing = candidates.get(hit.chunk_id)
            if existing is not None:
                if existing.sparse_rank is None:
                    existing.sparse_rank = hit.rank
                continue

            sparse_chunk = sparse_idx.get_chunk(hit.chunk_id)
            if sparse_chunk is None:
                continue
            chunk_type = str(sparse_chunk.chunk_type).lower()
            if chunk_type not in {"header", "body"}:
                chunk_type = "body"
            candidates[hit.chunk_id] = _CandidateChunk(
                chunk_id=hit.chunk_id,
                text=sparse_chunk.text,
                rel_path=sparse_chunk.rel_path,
                start_line=sparse_chunk.start_line,
                end_line=sparse_chunk.end_line,
                chunk_type=chunk_type,  # type: ignore[arg-type]
                distance=1.0,
                similarity=0.0,
                sparse_rank=hit.rank,
            )

    def _fuse_candidates(self, candidates: Dict[str, _CandidateChunk]) -> List[_CandidateChunk]:
        for c in candidates.values():
            score = 0.0
            if c.dense_rank is not None:
                score += _rrf_score(c.dense_rank, self.cfg.rrf_k)
            if c.sparse_rank is not None:
                score += _rrf_score(c.sparse_rank, self.cfg.rrf_k)
            c.fusion_score = score

        fused = sorted(
            candidates.values(),
            key=lambda x: (
                x.fusion_score,
                x.similarity,
                1 if x.chunk_type == "header" else 0,
            ),
            reverse=True,
        )
        return fused[: self.cfg.fused_candidates_k]

    def _rerank(self, query: str, candidates: List[_CandidateChunk]) -> List[_CandidateChunk]:
        if (not self.cfg.rerank_enabled) or self._reranker is None or not candidates:
            return sorted(candidates, key=lambda x: x.fusion_score, reverse=True)

        texts = [c.text[: self.cfg.reranker_max_chars] for c in candidates]
        try:
            scores = self._reranker.score(query=query, texts=texts)
        except Exception:
            # If reranker fails at runtime (model missing/offline/etc), gracefully fallback.
            self._reranker = None
            return sorted(candidates, key=lambda x: x.fusion_score, reverse=True)

        for c, s in zip(candidates, scores):
            c.rerank_score = float(s)

        return sorted(
            candidates,
            key=lambda x: (
                x.rerank_score if x.rerank_score is not None else float("-inf"),
                x.fusion_score,
            ),
            reverse=True,
        )

    def retrieve(self, query: str, top_k: int) -> List[RetrievedChunk]:
        dense_k = max(top_k, self.cfg.dense_candidates_k)
        candidates = self._dense_candidates(query=query, dense_k=dense_k)
        self._add_sparse_candidates(query=query, candidates=candidates)

        fused = self._fuse_candidates(candidates)
        reranked = self._rerank(query=query, candidates=fused)

        retrieved = [
            RetrievedChunk(
                chunk_id=c.chunk_id,
                text=c.text,
                rel_path=c.rel_path,
                start_line=c.start_line,
                end_line=c.end_line,
                chunk_type=c.chunk_type,
                distance=c.distance,
                similarity=c.similarity,
                dense_rank=c.dense_rank,
                sparse_rank=c.sparse_rank,
                fusion_score=c.fusion_score,
                rerank_score=c.rerank_score,
            )
            for c in reranked
        ]

        capped = _apply_doc_cap(query, retrieved, max_per_doc=self.cfg.max_chunks_per_doc)
        return capped[:top_k]
