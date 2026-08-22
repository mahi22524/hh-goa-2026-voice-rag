import os
import json
import faiss
import numpy as np
from typing import List, Dict, Any, Tuple

class VectorStore:
    def __init__(self, dimension: int = 384):
        """
        Initializes FAISS IndexFlatIP for exact nearest neighbor cosine similarity.
        Since we use normalized L2 unit vectors, the inner product is mathematically
        equivalent to cosine similarity. Flat index is selected for development as it performs
        exact (non-approximate) calculations and is highly efficient for small-to-medium datasets.
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(self.dimension)
        # Holds position index -> metadata dictionary mapping
        self.metadata_map: Dict[int, Dict[str, Any]] = {}
        # Holds original text mapped to position index (separate to save space, but kept in mapping)
        self.texts_map: Dict[int, str] = {}

    def add_chunks(self, chunk_texts: List[str], chunk_metadatas: List[Dict[str, Any]], embeddings: np.ndarray):
        """
        Adds vectors and corresponding metadata mapping to the store.
        embeddings must be a normalized numpy float32 array of shape (N, dimension).
        """
        if len(chunk_texts) != len(chunk_metadatas) or len(chunk_texts) != len(embeddings):
            raise ValueError("Size mismatch between texts, metadatas, and embeddings.")
            
        if len(chunk_texts) == 0:
            return
            
        current_count = self.index.ntotal
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Populate metadata mapping
        for i in range(len(chunk_texts)):
            pos = current_count + i
            self.metadata_map[pos] = chunk_metadatas[i]
            self.texts_map[pos] = chunk_texts[i]

    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Tuple[int, float, str, Dict[str, Any]]]:
        """
        Searches FAISS index using query_embedding (must be normalized float32 array).
        Returns a list of tuples: (rank, score, text, metadata)
        """
        if self.index.ntotal == 0:
            return []
            
        # Reshape to (1, dimension) if query is 1D
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        # Perform query
        # distances (scores) and indices
        actual_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_embedding, actual_k)
        
        results = []
        for i in range(actual_k):
            pos_index = int(indices[0][i])
            score = float(scores[0][i])
            
            if pos_index == -1:
                # FAISS placeholder if not enough vectors are found
                continue
                
            text = self.texts_map.get(pos_index, "")
            metadata = self.metadata_map.get(pos_index, {})
            results.append((i + 1, score, text, metadata))
            
        return results

    def save(self, index_path: str, metadata_path: str):
        """
        Saves the FAISS index and corresponding metadata mapping to local files.
        """
        # Ensure directories exist
        os.makedirs(os.path.dirname(index_path) or '.', exist_ok=True)
        os.makedirs(os.path.dirname(metadata_path) or '.', exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Combine texts and metadata mapping for serialization
        combined_meta = {
            "metadata_map": {str(k): v for k, v in self.metadata_map.items()},
            "texts_map": {str(k): v for k, v in self.texts_map.items()}
        }
        
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(combined_meta, f, ensure_ascii=False, indent=2)
            
        print(f"Saved FAISS index to '{index_path}' and metadata to '{metadata_path}'.", flush=True)

    def load(self, index_path: str, metadata_path: str):
        """
        Loads the FAISS index and metadata mapping from local files.
        """
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Index or metadata file not found at: {index_path}, {metadata_path}")
            
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        self.dimension = self.index.d
        
        # Load metadata maps
        with open(metadata_path, "r", encoding="utf-8") as f:
            combined_meta = json.load(f)
            
        self.metadata_map = {int(k): v for k, v in combined_meta.get("metadata_map", {}).items()}
        self.texts_map = {int(k): v for k, v in combined_meta.get("texts_map", {}).items()}
        
        print(f"Loaded FAISS index with {self.index.ntotal} vectors from '{index_path}'.", flush=True)
