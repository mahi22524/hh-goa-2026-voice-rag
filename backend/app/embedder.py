import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Singleton pattern to ensure the model is loaded only once across the application lifecycle.
        """
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", batch_size: int = 32):
        if self._initialized:
            return
            
        self.model_name = model_name
        self.batch_size = batch_size
        
        # Load the sentence transformer model on CPU explicitly to conserve resources
        print(f"Initializing EmbeddingService on CPU with model '{self.model_name}'...", flush=True)
        self.model = SentenceTransformer(self.model_name, device="cpu")
        self.dimension = self.model.get_embedding_dimension() if hasattr(self.model, "get_embedding_dimension") else self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Dimension: {self.dimension}", flush=True)
        
        self._initialized = True

    def encode(self, texts: List[str], batch_size: int = None) -> np.ndarray:
        """
        Generates L2-normalized float32 embeddings for a list of texts in batches.
        Normalized vectors allow Cosine Similarity to be computed using a flat Inner Product index (IndexFlatIP).
        """
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
            
        bs = batch_size if batch_size is not None else self.batch_size
        
        # We set normalize_embeddings=True to generate unit vectors (L2 normalized)
        # This matches cosine similarity when searched using Inner Product.
        embeddings = self.model.encode(
            texts,
            batch_size=bs,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        
        # Ensure it is float32
        return np.array(embeddings, dtype=np.float32)
