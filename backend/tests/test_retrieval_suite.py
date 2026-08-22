import unittest
import numpy as np
import os
import tempfile
import json
from backend.app.embedder import EmbeddingService
from backend.app.vector_store import VectorStore
from backend.app.retriever import Retriever

class TestRetrievalSuite(unittest.TestCase):
    def setUp(self):
        # We initialize the singleton EmbeddingService. It will load the model (on CPU)
        self.embedder = EmbeddingService()
        self.dummy_texts = [
            "What is a corporation? A corporation is a company authorized to act as a single entity.",
            "How does a computer work? It processes data using binary switches called transistors.",
            "HH Goa 2026 is the world's largest AI and crypto hacker house hosting hackers from all over."
        ]
        self.dummy_metadatas = [
            {"query_id": 1, "passage_index": 0, "language": "en", "chunk_strategy": "passage"},
            {"query_id": 2, "passage_index": 0, "language": "en", "chunk_strategy": "passage"},
            {"query_id": 3, "passage_index": 0, "language": "en", "chunk_strategy": "passage"}
        ]

    def test_embedder(self):
        """
        Embedding Test:
        - Verify model loads.
        - Embeddings are produced with correct dimensions.
        - Verify returned dtype is float32.
        """
        embeddings = self.embedder.encode(self.dummy_texts)
        self.assertEqual(embeddings.shape[0], len(self.dummy_texts))
        self.assertEqual(embeddings.shape[1], 384) # MiniLM-L6-v2 dimension is 384
        self.assertEqual(embeddings.dtype, np.float32)
        
        # Verify L2 normalization (cosine similarity check)
        norms = np.linalg.norm(embeddings, axis=1)
        for norm in norms:
            self.assertAlmostEqual(norm, 1.0, places=5)

    def test_faiss_index_and_metadata(self):
        """
        FAISS Index and Metadata Test:
        - Verify FAISS index builds and holds the expected number of vectors.
        - Verify search returns Top-K results.
        - Verify result positions map back correctly to chunk metadata.
        """
        vector_store = VectorStore(dimension=self.embedder.dimension)
        embeddings = self.embedder.encode(self.dummy_texts)
        
        # Add chunks
        vector_store.add_chunks(self.dummy_texts, self.dummy_metadatas, embeddings)
        self.assertEqual(vector_store.index.ntotal, len(self.dummy_texts))
        
        # Query search (exact match on query 3)
        query_text = "Who is hosting the HH Goa 2026 crypto hacker house?"
        query_vector = self.embedder.encode([query_text])
        
        results = vector_store.search(query_vector, top_k=2)
        
        # Check Top-K constraint
        self.assertEqual(len(results), 2)
        
        # Check mapping logic
        for rank, score, text, metadata in results:
            self.assertIn(text, self.dummy_texts)
            idx = self.dummy_texts.index(text)
            self.assertEqual(metadata["query_id"], self.dummy_metadatas[idx]["query_id"])
            self.assertEqual(metadata["passage_index"], self.dummy_metadatas[idx]["passage_index"])
            
        # The first result should be the HH Goa text (highest similarity)
        first_result_text = results[0][2]
        self.assertEqual(first_result_text, self.dummy_texts[2])

    def test_retriever_flow(self):
        """
        Retriever Flow Test:
        - Test save/load logic.
        - Verify a known query returns formatting containing rank, score, text, and metadata.
        """
        # Create temp files for index serialization
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, "test.index")
            meta_path = os.path.join(tmpdir, "test_metadata.json")
            
            # 1. Build and save dummy store
            vector_store = VectorStore(dimension=self.embedder.dimension)
            embeddings = self.embedder.encode(self.dummy_texts)
            vector_store.add_chunks(self.dummy_texts, self.dummy_metadatas, embeddings)
            vector_store.save(index_path, meta_path)
            
            # 2. Load retriever
            retriever = Retriever(index_path=index_path, meta_path=meta_path)
            
            # 3. Retrieve
            query_str = "What is a corporation?"
            results = retriever.retrieve(query_str, top_k=1)
            
            self.assertEqual(len(results), 1)
            res = results[0]
            self.assertEqual(res["rank"], 1)
            self.assertGreater(res["score"], 0.5) # High similarity expected for exact query
            self.assertEqual(res["text"], self.dummy_texts[0])
            self.assertEqual(res["metadata"]["query_id"], 1)
            self.assertEqual(res["metadata"]["language"], "en")

if __name__ == "__main__":
    unittest.main()
