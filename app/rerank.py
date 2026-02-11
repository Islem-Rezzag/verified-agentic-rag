from __future__ import annotations

from typing import Dict, List


class CrossEncoderReranker:
    """
    Thin wrapper around sentence-transformers CrossEncoder for query-chunk reranking.
    """

    _GLOBAL_MODELS: Dict[str, object] = {}

    def __init__(self, model_name: str, batch_size: int = 16) -> None:
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None

    def _load(self):
        if self._model is None:
            if self.model_name in self._GLOBAL_MODELS:
                self._model = self._GLOBAL_MODELS[self.model_name]
                return self._model
            try:
                from sentence_transformers import CrossEncoder
            except ImportError as e:
                raise RuntimeError(
                    "sentence-transformers is not installed. Run: pip install -r requirements.txt"
                ) from e
            self._model = CrossEncoder(self.model_name)
            self._GLOBAL_MODELS[self.model_name] = self._model
        return self._model

    def score(self, query: str, texts: List[str]) -> List[float]:
        if not texts:
            return []
        model = self._load()
        pairs = [[query, text] for text in texts]
        scores = model.predict(pairs, batch_size=self.batch_size, show_progress_bar=False)
        return [float(x) for x in scores]
