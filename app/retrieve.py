from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .index import VectorIndex


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
    distance: float
    similarity: float


class Retriever:
    def __init__(self, index: VectorIndex) -> None:
        self.index = index

    def retrieve(self, query: str, top_k: int) -> List[RetrievedChunk]:
        res = self.index.query(query_text=query, top_k=top_k)

        docs = res["documents"][0]
        metas = res["metadatas"][0]
        dists = res["distances"][0]
        ids = res.get("ids", [["" for _ in docs]])[0]

        out: List[RetrievedChunk] = []
        for chunk_id, doc, meta, dist in zip(ids, docs, metas, dists):
            sim = 1.0 - float(dist)  # works as approx when using cosine distance
            out.append(
                RetrievedChunk(
                    chunk_id=str(chunk_id),
                    text=str(doc),
                    rel_path=str(meta.get("rel_path", "")),
                    start_line=int(meta.get("start_line", 0)),
                    end_line=int(meta.get("end_line", 0)),
                    distance=float(dist),
                    similarity=float(sim),
                )
            )
        return out
