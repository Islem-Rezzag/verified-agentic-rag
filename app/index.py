from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .chunking import Chunk


@dataclass
class IndexedChunk:
    """
    A chunk ready for storage.

    Beginner note:
    - embeddings are the numeric vectors stored in the vector database.
    """
    chunk: Chunk
    embedding: List[float]


class Embedder:
    """
    Text -> vector embeddings using sentence-transformers.

    Beginner note:
    - embedding models convert text to numbers so similar texts are close in vector space.
    """

    # Cache the loaded SentenceTransformer across instances in the same process.
    # This avoids repeated HF Hub calls during eval loops.
    _GLOBAL_MODELS: Dict[str, object] = {}

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            if self.model_name in self._GLOBAL_MODELS:
                self._model = self._GLOBAL_MODELS[self.model_name]
                return self._model
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as e:
                raise RuntimeError(
                    "sentence-transformers is not installed. Run: pip install -r requirements.txt"
                ) from e
            self._model = SentenceTransformer(self.model_name)
            self._GLOBAL_MODELS[self.model_name] = self._model
        return self._model

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        model = self._load()
        vectors = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,  # cosine similarity behaves better when normalized
        )
        # Convert to plain Python lists (Chroma can store lists)
        return [v.tolist() for v in vectors]


class VectorIndex:
    """
    Chroma persistent vector store wrapper.

    Stores:
    - documents (chunk text)
    - embeddings
    - metadata (path + line range + chunk_type)

    Beginner note:
    - Chroma is like a database for embeddings.
    - "Persistent" means it saves on disk so you can reuse the index later.
    """

    def __init__(
        self,
        persist_dir: Path,
        collection_name: str,
        embedding_model: str,
    ) -> None:
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.embedder = Embedder(embedding_model)

        self._client = None
        self._collection = None

    def _get_client(self):
        if self._client is None:
            try:
                import chromadb
            except ImportError as e:
                raise RuntimeError(
                    "chromadb is not installed. Run: pip install -r requirements.txt"
                ) from e
            self._client = chromadb.PersistentClient(path=str(self.persist_dir))
        return self._client

    def _get_collection(self):
        if self._collection is None:
            client = self._get_client()
            try:
                self._collection = client.get_collection(self.collection_name)
            except Exception:
                # Create collection if not exists.
                # cosine space works well for normalized embeddings.
                self._collection = client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
        return self._collection

    def reset_collection(self) -> None:
        client = self._get_client()
        try:
            client.delete_collection(self.collection_name)
        except Exception:
            pass
        self._collection = None

    def upsert_chunks(self, chunks: Iterable[Chunk], batch_size: int = 64) -> int:
        """
        Embed and store chunks in Chroma.

        Returns number of chunks stored.
        """
        collection = self._get_collection()

        buffer: List[Chunk] = []
        total = 0

        def flush(buf: List[Chunk]) -> int:
            if not buf:
                return 0
            texts = [c.text for c in buf]
            embeddings = self.embedder.embed_texts(texts)

            ids = [c.chunk_id for c in buf]
            metadatas = [
                {
                    "source": c.source,
                    "rel_path": c.rel_path,
                    "start_line": c.start_line,
                    "end_line": c.end_line,
                    "chunk_type": c.chunk_type,
                }
                for c in buf
            ]

            # Some Chroma versions support upsert; fallback to add.
            if hasattr(collection, "upsert"):
                collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
            else:
                # If add errors because ids exist, you should reset collection first.
                collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

            return len(buf)

        for ch in chunks:
            buffer.append(ch)
            if len(buffer) >= batch_size:
                total += flush(buffer)
                buffer = []

        total += flush(buffer)
        return total

    def query(self, query_text: str, top_k: int):
        """
        Retrieve top_k chunks for query_text.

        Returns Chroma raw query result (documents, metadatas, distances).
        """
        collection = self._get_collection()
        q_embedding = self.embedder.embed_texts([query_text])[0]
        return collection.query(
            query_embeddings=[q_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

    def get_all_chunks(self):
        """
        Return all stored chunks from the collection.

        Used by sparse retrievers that need corpus-wide lexical indexing.
        """
        collection = self._get_collection()
        return collection.get(include=["documents", "metadatas"])
