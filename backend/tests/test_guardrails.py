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

class TestGuardrails(unittest.TestCase):
    def setUp(self):
        # 1. Start SentenceTransformer patcher before loading the RAGPipeline
        self.transformer_patcher = patch('backend.app.embedder.SentenceTransformer')
        self.mock_transformer = self.transformer_patcher.start()
        
        # Configure mock transformer to return dummy dimension
        self.mock_transformer_inst = MagicMock()
        self.mock_transformer_inst.get_embedding_dimension.return_value = 384
        self.mock_transformer_inst.get_sentence_embedding_dimension.return_value = 384
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

    def test_empty_question(self):
        """
        Test 1: Empty question.
        Verify that a null or empty query is rejected safely by input guardrails.
        """
        res = self.pipeline.answer_question("")
        self.assertEqual(res["status"], "input_rejected")
        self.assertIn("cannot be empty", res["answer"])
        self.assertEqual(res["retrieved_sources"], [])
        
        # Non-string input rejection
        res = self.pipeline.answer_question(None)
        self.assertEqual(res["status"], "input_rejected")
        self.assertIn("Invalid input type", res["answer"])

    def test_whitespace_question(self):
        """
        Test 2: Whitespace question.
        Verify that whitespace-only queries are rejected safely.
        """
        res = self.pipeline.answer_question("    ")
        self.assertEqual(res["status"], "input_rejected")
        self.assertIn("cannot be empty", res["answer"])

    def test_relevant_context(self):
        """
        Test 3: Relevant context.
        Verify that the LLM successfully answers using relevant context that exceeds the score threshold.
        """
        self.mock_retrieve.return_value = [
            {
                "rank": 1,
                "score": 0.85,
                "text": "A corporation is a company authorized to act as a single entity.",
                "metadata": {"query_id": 99, "is_selected": 1, "language": "en"}
            }
        ]
        res = self.pipeline.answer_question("what is a corporation?")
        self.assertEqual(res["status"], "success")
        self.assertIn("authorized to act as a single entity", res["answer"])
        self.assertNotEqual(res["answer"], self.fallback_msg)

    def test_irrelevant_context(self):
        """
        Test 4: Irrelevant context.
        Verify that context that does not contain the answer results in the fallback reply.
        """
        # Retrieval returns document but it is irrelevant
        self.mock_retrieve.return_value = [
            {
                "rank": 1,
                "score": 0.65,
                "text": "McDonald's is a fast food chain.",
                "metadata": {"query_id": 101, "is_selected": 0, "language": "en"}
            }
        ]
        res = self.pipeline.answer_question("what is a corporation?")
        self.assertEqual(res["status"], "insufficient_context")
        self.assertEqual(res["answer"], self.fallback_msg)

    def test_low_retrieval_scores(self):
        """
        Test 5: Low retrieval scores.
        Verify that the LLM is bypassed (not called, LLM latency is 0) if scores are below the threshold.
        """
        # Cosine score is 0.25 (below MIN_RETRIEVAL_SCORE of 0.40)
        self.mock_retrieve.return_value = [
            {
                "rank": 1,
                "score": 0.25,
                "text": "A corporation is a company authorized to act as a single entity.",
                "metadata": {"query_id": 99, "is_selected": 1, "language": "en"}
            }
        ]
        
        res = self.pipeline.answer_question("what is a corporation?")
        self.assertEqual(res["status"], "insufficient_context")
        self.assertEqual(res["answer"], self.fallback_msg)
        self.assertEqual(res["llm_latency"], 0.0)

    def test_llm_failure(self):
        """
        Test 6: LLM failure.
        Verify that errors raised by the LLM (timeouts, API failures) are caught and handled safely.
        """
        self.mock_retrieve.return_value = [
            {
                "rank": 1,
                "score": 0.90,
                "text": "A corporation is a company authorized to act as a single entity.",
                "metadata": {"query_id": 99, "is_selected": 1, "language": "en"}
            }
        ]
        
        failing_provider = MagicMock(spec=LLMProvider)
        failing_provider.generate_answer.side_effect = ConnectionError("Google API timeout")
        self.pipeline.llm = failing_provider
        
        res = self.pipeline.answer_question("what is a corporation?")
        self.assertEqual(res["status"], "llm_failure")
        self.assertEqual(res["answer"], "LLM generation failed to execute.")
        self.assertEqual(res["error"], "Google API timeout")

    def test_retrieval_failure(self):
        """
        Test 7: Retrieval failure.
        Verify that exceptions raised during FAISS search are handled gracefully.
        """
        self.mock_retrieve.side_effect = RuntimeError("FAISS lookup failed")
        
        res = self.pipeline.answer_question("what is a corporation?")
        self.assertEqual(res["status"], "retrieval_failure")
        self.assertEqual(res["answer"], "Retrieval process failed to execute.")
        self.assertEqual(res["error"], "Database lookup failed.")

    def test_source_traceability(self):
        """
        Test 8: Source traceability.
        Verify that metadata from retrieved sources remains attached to the response.
        """
        self.mock_retrieve.return_value = [
            {
                "rank": 1,
                "score": 0.85,
                "text": "A corporation is a company authorized to act as a single entity.",
                "metadata": {"query_id": 99, "passage_index": 4, "language": "en", "is_selected": 1}
            }
        ]
        res = self.pipeline.answer_question("what is a corporation?")
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["retrieved_sources"]), 1)
        source = res["retrieved_sources"][0]
        self.assertEqual(source["rank"], 1)
        self.assertEqual(source["score"], 0.85)
        self.assertEqual(source["metadata"]["query_id"], 99)
        self.assertEqual(source["metadata"]["passage_index"], 4)
        self.assertEqual(source["metadata"]["language"], "en")

    def test_secret_protection(self):
        """
        Test 9: Secret protection.
        Verify no API key or .env details are exposed in user-facing error messages.
        """
        self.mock_retrieve.return_value = [
            {
                "rank": 1,
                "score": 0.90,
                "text": "A corporation is a company authorized to act as a single entity.",
                "metadata": {"query_id": 99, "is_selected": 1, "language": "en"}
            }
        ]
        
        failing_provider = MagicMock(spec=LLMProvider)
        # Throw an error that contains an API key signature
        failing_provider.generate_answer.side_effect = RuntimeError("Failed with key: AIzaSyDdummyKey123")
        self.pipeline.llm = failing_provider
        
        res = self.pipeline.answer_question("what is a corporation?")
        self.assertEqual(res["status"], "llm_failure")
        # Ensure key is masked and not returned in user-facing error message
        self.assertNotIn("AIzaSyDdummyKey123", res["error"])
        self.assertEqual(res["error"], "API request failed due to authentication/service error.")

if __name__ == "__main__":
    unittest.main()
