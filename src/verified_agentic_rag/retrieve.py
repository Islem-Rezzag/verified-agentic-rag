from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

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

METADATA_HINT_PATTERNS = [
    r"\bresponsible committee\b",
    r"\bwhich committee\b",
    r"\bpolicy group\b",
    r"\bwhich group\b",
    r"\bresponsible officer\b",
    r"\bapproved by\b",
    r"\bwho approved\b",
    r"\bapproving body\b",
    r"\bversion\b",
    r"\bminute no\b",
    r"\bminute number\b",
    r"\blast updated\b",
    r"\bdate updated\b",
    r"\bdate\b.*\bupdated\b",
    r"\bnext review date\b",
    r"\breview date\b",
    r"\breview frequency\b",
    r"\bdocument retention\b",
    r"\bretention period\b",
]


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


@dataclass(frozen=True)
class RetrievalTrace:
    dense_candidates: List[RetrievedChunk] = field(default_factory=list)
    sparse_candidates: List[RetrievedChunk] = field(default_factory=list)
    fused_candidates: List[RetrievedChunk] = field(default_factory=list)
    reranked_candidates: List[RetrievedChunk] = field(default_factory=list)
    final_top_k: List[RetrievedChunk] = field(default_factory=list)


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


def question_mentions_doc(question: str, rel_path: str) -> bool:
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


def _is_metadata_question(question: str) -> bool:
    q = question or ""
    return any(re.search(p, q, flags=re.IGNORECASE) for p in METADATA_HINT_PATTERNS)


def _candidate_to_retrieved(c: _CandidateChunk) -> RetrievedChunk:
    return RetrievedChunk(
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


def _apply_doc_cap(question: str, chunks: List[RetrievedChunk], max_per_doc: int) -> List[RetrievedChunk]:
    if max_per_doc <= 0:
        return chunks

    exempt_docs = {c.rel_path for c in chunks if question_mentions_doc(question, c.rel_path)}
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
        self._all_chunks_by_doc: Optional[Dict[str, List[RetrievedChunk]]] = None

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

    def _dense_candidates(self, query: str, dense_k: int) -> Tuple[Dict[str, _CandidateChunk], List[_CandidateChunk]]:
        res = self.index.query(query_text=query, top_k=dense_k)

        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        ids = (res.get("ids") or [["" for _ in docs]])[0]

        out: Dict[str, _CandidateChunk] = {}
        ranked: List[_CandidateChunk] = []
        for rank, (chunk_id, doc, meta, dist) in enumerate(zip(ids, docs, metas, dists), start=1):
            meta = meta or {}
            chunk_type = str(meta.get("chunk_type", "body")).lower()
            if chunk_type not in {"header", "body"}:
                chunk_type = "body"
            cand = _CandidateChunk(
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
            out[str(chunk_id)] = cand
            ranked.append(cand)
        return out, ranked

    def _add_sparse_candidates(
        self,
        query: str,
        candidates: Dict[str, _CandidateChunk],
    ) -> List[_CandidateChunk]:
        sparse_idx = self._ensure_sparse_index()
        if sparse_idx is None:
            return []

        sparse_hits = sparse_idx.search(query, top_k=self.cfg.sparse_candidates_k)
        ordered: List[_CandidateChunk] = []
        for hit in sparse_hits:
            existing = candidates.get(hit.chunk_id)
            if existing is not None:
                if existing.sparse_rank is None:
                    existing.sparse_rank = hit.rank
                ordered.append(existing)
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
            ordered.append(candidates[hit.chunk_id])
        return ordered

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

    @staticmethod
    def _norm_rel_path(rel_path: str) -> str:
        return (rel_path or "").replace("\\", "/").strip().lower()

    def _load_all_chunks_by_doc(self) -> Dict[str, List[RetrievedChunk]]:
        if self._all_chunks_by_doc is not None:
            return self._all_chunks_by_doc

        raw = self.index.get_all_chunks()
        ids = raw.get("ids") or []
        docs = raw.get("documents") or []
        metas = raw.get("metadatas") or []

        by_doc: Dict[str, List[RetrievedChunk]] = {}
        for chunk_id, doc, meta in zip(ids, docs, metas):
            meta = meta or {}
            chunk_type = str(meta.get("chunk_type", "body")).lower()
            if chunk_type not in {"header", "body"}:
                chunk_type = "body"

            rel = str(meta.get("rel_path", ""))
            key = self._norm_rel_path(rel)
            if not key:
                continue

            item = RetrievedChunk(
                chunk_id=str(chunk_id),
                text=str(doc or ""),
                rel_path=rel,
                start_line=int(meta.get("start_line", 0)),
                end_line=int(meta.get("end_line", 0)),
                chunk_type=chunk_type,  # type: ignore[arg-type]
                distance=1.0,
                similarity=0.0,
                dense_rank=None,
                sparse_rank=None,
                fusion_score=None,
                rerank_score=None,
            )
            by_doc.setdefault(key, []).append(item)

        for chunks in by_doc.values():
            chunks.sort(key=lambda c: (c.start_line, 0 if c.chunk_type == "header" else 1, c.end_line))

        self._all_chunks_by_doc = by_doc
        return by_doc

    def get_document_chunks(self, rel_path: str) -> List[RetrievedChunk]:
        wanted = self._norm_rel_path(rel_path)
        if not wanted:
            return []

        by_doc = self._load_all_chunks_by_doc()
        exact = by_doc.get(wanted)
        if exact is not None:
            return list(exact)

        for key, chunks in by_doc.items():
            if key.endswith(wanted) or wanted.endswith(key):
                return list(chunks)
        return []

    def _ensure_metadata_header_chunk(
        self,
        *,
        query: str,
        selected: List[RetrievedChunk],
        reranked_all: List[RetrievedChunk],
        top_k: int,
    ) -> List[RetrievedChunk]:
        if top_k <= 0 or not _is_metadata_question(query):
            return selected
        if any(c.chunk_type == "header" for c in selected[:top_k]):
            return selected

        header = next((c for c in reranked_all if c.chunk_type == "header"), None)
        if header is None:
            return selected

        boosted = [header]
        boosted.extend(c for c in selected if c.chunk_id != header.chunk_id)
        return boosted

    def retrieve_with_trace(self, query: str, top_k: int) -> Tuple[List[RetrievedChunk], RetrievalTrace]:
        dense_k = max(top_k, self.cfg.dense_candidates_k)
        candidates, dense_ranked = self._dense_candidates(query=query, dense_k=dense_k)
        sparse_ranked = self._add_sparse_candidates(query=query, candidates=candidates)

        fused = self._fuse_candidates(candidates)
        reranked = self._rerank(query=query, candidates=fused)
        reranked_retrieved = [_candidate_to_retrieved(c) for c in reranked]

        capped = _apply_doc_cap(query, reranked_retrieved, max_per_doc=self.cfg.max_chunks_per_doc)
        adjusted = self._ensure_metadata_header_chunk(
            query=query,
            selected=capped,
            reranked_all=reranked_retrieved,
            top_k=top_k,
        )
        final = adjusted[:top_k]

        trace = RetrievalTrace(
            dense_candidates=[_candidate_to_retrieved(c) for c in dense_ranked[:dense_k]],
            sparse_candidates=[_candidate_to_retrieved(c) for c in sparse_ranked[: self.cfg.sparse_candidates_k]],
            fused_candidates=[_candidate_to_retrieved(c) for c in fused],
            reranked_candidates=reranked_retrieved,
            final_top_k=final,
        )
        return final, trace

    def retrieve(self, query: str, top_k: int) -> List[RetrievedChunk]:
        retrieved, _trace = self.retrieve_with_trace(query=query, top_k=top_k)
        return retrieved
