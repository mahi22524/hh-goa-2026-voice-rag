import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
import json
import numpy as np

# Force environment provider to mock
os.environ["LLM_PROVIDER"] = "mock"

# Global placeholder for local imports
RAGPipeline = None
LLMProvider = None

class TestRAGPipeline(unittest.TestCase):
    def setUp(self):
        # 1. Start SentenceTransformer patcher before loading the RAGPipeline
        self.transformer_patcher = patch('backend.app.embedder.SentenceTransformer')
        self.mock_transformer = self.transformer_patcher.start()
        
        # Configure mock transformer to return dummy dimension
        self.mock_transformer_inst = MagicMock()
        self.mock_transformer_inst.get_embedding_dimension.return_value = 384
        self.mock_transformer_inst.get_sentence_embedding_dimension.return_value = 384
        # Return all-zero normalized vector
        self.mock_transformer_inst.encode.return_value = np.zeros((1, 384), dtype=np.float32)
        self.mock_transformer.return_value = self.mock_transformer_inst

        # Import modules locally inside setup so they resolve against the mocked SentenceTransformer
        global RAGPipeline, LLMProvider
        from backend.app.rag_pipeline import RAGPipeline
        from backend.app.llm_providers import LLMProvider

        # Create temp files for setup mock loading
        self.tmpdir = tempfile.TemporaryDirectory()
        self.index_path = os.path.join(self.tmpdir.name, "test.index")
        self.meta_path = os.path.join(self.tmpdir.name, "test_metadata.json")
        
        # Write dummy files to satisfy path checks
        with open(self.index_path, "wb") as f:
            f.write(b"dummy index data")
        
        dummy_meta = {
            "metadata_map": {},
            "texts_map": {}
        }
        with open(self.meta_path, "w") as f:
            json.dump(dummy_meta, f)

        # Mock VectorStore.load
        self.load_patcher = patch('vector_store.VectorStore.load', return_value=None)
        self.load_patcher.start()
        
        # Patch retriever retrieve method
        self.mock_retrieve = patch('retriever.Retriever.retrieve').start()
        
        self.pipeline = RAGPipeline(index_path=self.index_path, meta_path=self.meta_path)
        self.fallback_msg = "I don't have enough information in the provided context to answer that."

    def tearDown(self):
        patch.stopall()
        self.tmpdir.cleanup()

    def test_grounded_answer(self):
        """
        Test 1: Successful grounded answer.
        Verify successful RAG output when relevant context containing the answer is retrieved.
        """
        self.mock_retrieve.return_value = [
            {
                "rank": 1,
                "score": 0.85,
                "text": "A corporation is a company authorized to act as a single entity.",
                "metadata": {"query_id": 99, "is_selected": 1, "language": "en"}
            }
        ]
        
        res = self.pipeline.answer_question("what is a corporation?", top_k=1)
        self.assertEqual(res["status"], "success")
        self.assertIn("authorized to act as a single entity", res["answer"])
        self.assertGreater(len(res["retrieved_sources"]), 0)
        self.assertGreater(res["retrieval_latency"], 0)
        self.assertGreater(res["llm_latency"], 0)

    def test_insufficient_context(self):
        """
        Test 2: Insufficient context.
        Verify that the pipeline returns the exact fallback string when retrieved context is irrelevant.
        """
        # Case A: Retrieval returns empty list
        self.mock_retrieve.return_value = []
        res = self.pipeline.answer_question("who won the 2026 world cup?", top_k=1)
        self.assertEqual(res["status"], "insufficient_context")
        self.assertEqual(res["answer"], self.fallback_msg)
        
        # Case B: Retrieval returns irrelevant context
        self.mock_retrieve.return_value = [
            {
                "rank": 1,
                "score": 0.32,
                "text": "In 2018, south lincoln weather website was active.",
                "metadata": {"query_id": 100, "is_selected": 0, "language": "en"}
            }
        ]
        res = self.pipeline.answer_question("what is a corporation?", top_k=1)
        self.assertEqual(res["status"], "insufficient_context")
        self.assertEqual(res["answer"], self.fallback_msg)

    def test_empty_question(self):
        """
        Test 3: Empty question.
        Verify that empty or whitespace queries are handled safely.
        """
        # Empty string
        res = self.pipeline.answer_question("")
        self.assertEqual(res["status"], "input_rejected")
        self.assertIn("cannot be empty", res["answer"])
        
        # Whitespaces
        res = self.pipeline.answer_question("   ")
        self.assertEqual(res["status"], "input_rejected")
        self.assertIn("cannot be empty", res["answer"])
        
        # None type
        res = self.pipeline.answer_question(None)
        self.assertEqual(res["status"], "input_rejected")
        self.assertIn("Invalid input type", res["answer"])

    def test_retrieval_failure(self):
        """
        Test 4: Retrieval failure.
        Verify that exceptions raised during FAISS indexing/lookup are handled gracefully.
        """
        self.mock_retrieve.side_effect = RuntimeError("FAISS database corrupted")
        
        res = self.pipeline.answer_question("what is a corporation?")
        self.assertEqual(res["status"], "retrieval_failure")
        self.assertIn("failed to execute", res["answer"])
        self.assertEqual(res["retrieved_sources"], [])
        self.assertEqual(res["error"], "Database lookup failed.")

    def test_llm_failure(self):
        """
        Test 5: LLM failure.
        Verify that errors raised by the LLM (timeouts, API failures) are caught and handled.
        """
        self.mock_retrieve.return_value = [
            {
                "rank": 1,
                "score": 0.90,
                "text": "Dummy valid context",
                "metadata": {"query_id": 55, "is_selected": 1, "language": "en"}
            }
        ]
        
        # Mock LLM provider to throw ConnectionError
        failing_provider = MagicMock(spec=LLMProvider)
        failing_provider.generate_answer.side_effect = ConnectionError("Google API timeout")
        self.pipeline.llm = failing_provider
        
        res = self.pipeline.answer_question("what is a corporation?")
        self.assertEqual(res["status"], "llm_failure")
        self.assertIn("failed to execute", res["answer"])
        self.assertEqual(res["error"], "Google API timeout")
        self.assertEqual(len(res["retrieved_sources"]), 1)

if __name__ == "__main__":
    unittest.main()
