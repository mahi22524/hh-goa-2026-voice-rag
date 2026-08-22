import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import tempfile
import json
import numpy as np
import requests

# Force environment provider to mock
os.environ["LLM_PROVIDER"] = "mock"
os.environ["SARVAM_API_KEY"] = "dummy_sarvam_subscription_key_123"

# Global placeholder for local imports
VoiceRAGPipeline = None
validate_audio = None
transcribe_audio = None

class TestSpeechToText(unittest.TestCase):
    def setUp(self):
        # Start SentenceTransformer patcher before loading the RAG classes to prevent actual model loads
        self.transformer_patcher = patch('backend.app.embedder.SentenceTransformer')
        self.mock_transformer = self.transformer_patcher.start()
        
        # Configure mock transformer to return dummy dimension
        self.mock_transformer_inst = MagicMock()
        self.mock_transformer_inst.get_embedding_dimension.return_value = 384
        self.mock_transformer_inst.get_sentence_embedding_dimension.return_value = 384
        self.mock_transformer.return_value = self.mock_transformer_inst

        # Import modules locally inside setup
        global VoiceRAGPipeline, validate_audio, transcribe_audio
        from backend.app.voice_rag import VoiceRAGPipeline
        from backend.app.speech_to_text import validate_audio, transcribe_audio

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
        
        # Patch the retriever retrieve method to return controlled mock documents
        self.mock_retrieve = patch('retriever.Retriever.retrieve').start()

    def tearDown(self):
        patch.stopall()
        self.tmpdir.cleanup()

    @patch('backend.app.speech_to_text.os.path.exists', return_value=True)
    @patch('backend.app.speech_to_text.os.path.getsize', return_value=1024)
    @patch('backend.app.speech_to_text.wave.open')
    @patch('backend.app.speech_to_text.requests.post')
    def test_successful_transcription(self, mock_post, mock_wave_open, mock_getsize, mock_exists):
        """
        Test 1: Successful transcription.
        Verify that a successful HTTP 200 response from Sarvam yields structured text.
        """
        # Configure wave open to return dummy WAV parameters (duration = frames/rate = 100/10 = 10s)
        mock_wave_inst = MagicMock()
        mock_wave_inst.getnframes.return_value = 100
        mock_wave_inst.getframerate.return_value = 10
        mock_wave_open.return_value.__enter__.return_value = mock_wave_inst
        
        # Configure mock requests response
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.json.return_value = {
            "transcript": "hello world",
            "language_code": "en-IN",
            "request_id": "req-999"
        }
        mock_post.return_value = mock_res
        
        # Mock file read
        with patch('builtins.open', mock_open(read_data=b"audiobytes")):
            res = transcribe_audio("sample.wav", "en-IN")
            
        self.assertEqual(res["transcript"], "hello world")
        self.assertEqual(res["language_code"], "en-IN")
        self.assertEqual(res["request_id"], "req-999")

    @patch('backend.app.speech_to_text.os.path.exists', return_value=True)
    @patch('backend.app.speech_to_text.os.path.getsize', return_value=0)
    def test_empty_audio_file(self, mock_getsize, mock_exists):
        """
        Test 2: Empty audio file.
        Verify that a zero-byte file is rejected immediately without calling API.
        """
        is_valid, err = validate_audio("empty.wav")
        self.assertFalse(is_valid)
        self.assertIn("empty", err)

    @patch('backend.app.speech_to_text.os.path.exists', return_value=True)
    @patch('backend.app.speech_to_text.os.path.getsize', return_value=1024)
    def test_invalid_file_type(self, mock_getsize, mock_exists):
        """
        Test 3: Invalid file type.
        Verify that unsupported file extensions are rejected immediately.
        """
        is_valid, err = validate_audio("sample.txt")
        self.assertFalse(is_valid)
        self.assertIn("Unsupported audio type", err)

    @patch('backend.app.speech_to_text.os.path.exists', return_value=True)
    @patch('backend.app.speech_to_text.os.path.getsize', return_value=1024)
    @patch('backend.app.speech_to_text.wave.open')
    @patch('backend.app.speech_to_text.requests.post')
    def test_sarvam_api_failure(self, mock_post, mock_wave_open, mock_getsize, mock_exists):
        """
        Test 4: Sarvam API failure.
        Verify HTTP errors are caught and returned safely.
        """
        # WAV duration is 10s
        mock_wave_inst = MagicMock()
        mock_wave_inst.getnframes.return_value = 100
        mock_wave_inst.getframerate.return_value = 10
        mock_wave_open.return_value.__enter__.return_value = mock_wave_inst
        
        # Configure mock requests response to throw HTTPError
        mock_res = MagicMock()
        mock_res.status_code = 500
        mock_res.raise_for_status.side_effect = requests.exceptions.HTTPError("Internal Server Error")
        mock_post.return_value = mock_res
        
        with patch('builtins.open', mock_open(read_data=b"audiobytes")):
            with self.assertRaises(RuntimeError) as context:
                transcribe_audio("sample.wav")
                
        self.assertIn("transcription failed", str(context.exception))

    @patch('backend.app.speech_to_text.os.path.exists', return_value=True)
    @patch('backend.app.speech_to_text.os.path.getsize', return_value=1024)
    def test_missing_api_key(self, mock_getsize, mock_exists):
        """
        Test 5: Missing API key.
        Verify ValueError is raised if SARVAM_API_KEY is absent.
        """
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                transcribe_audio("sample.wav")
        self.assertIn("SARVAM_API_KEY environment variable is not set", str(context.exception))

    @patch('backend.app.speech_to_text.os.path.exists', return_value=True)
    @patch('backend.app.speech_to_text.os.path.getsize', return_value=1024)
    @patch('backend.app.speech_to_text.wave.open')
    @patch('backend.app.speech_to_text.requests.post')
    def test_transcript_passed_to_rag(self, mock_post, mock_wave_open, mock_getsize, mock_exists):
        """
        Test 6: Transcript successfully passed to RAG.
        Verify that transcription is correctly fed into vector retrieval and LLM stages.
        """
        # WAV duration is 10s
        mock_wave_inst = MagicMock()
        mock_wave_inst.getnframes.return_value = 100
        mock_wave_inst.getframerate.return_value = 10
        mock_wave_open.return_value.__enter__.return_value = mock_wave_inst
        
        # Configure mock requests response
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.json.return_value = {
            "transcript": "what is a corporation?",
            "language_code": "en-IN",
            "request_id": "req-1"
        }
        mock_post.return_value = mock_res
        
        # Mock RAG response
        self.mock_retrieve.return_value = [
            {
                "rank": 1,
                "score": 0.85,
                "text": "A corporation is a company authorized to act as a single entity.",
                "metadata": {"query_id": 99, "is_selected": 1, "language": "en"}
            }
        ]
        
        voice_pipeline = VoiceRAGPipeline(index_path=self.index_path, meta_path=self.meta_path)
        
        with patch('builtins.open', mock_open(read_data=b"audiobytes")):
            res = voice_pipeline.answer_voice_query("sample.wav", "en-IN")
            
        self.assertEqual(res["transcript"], "what is a corporation?")
        self.assertEqual(res["language_code"], "en-IN")
        self.assertIn("authorized to act as a single entity", res["answer"])
        self.assertEqual(len(res["sources"]), 1)
        self.assertGreater(res["stt_latency_ms"], 0)
        self.assertGreater(res["rag_latency_ms"], 0)

    @patch('backend.app.speech_to_text.os.path.exists', return_value=True)
    @patch('backend.app.speech_to_text.os.path.getsize', return_value=1024)
    @patch('backend.app.speech_to_text.wave.open')
    @patch('backend.app.speech_to_text.requests.post')
    def test_rag_failure_after_stt(self, mock_post, mock_wave_open, mock_getsize, mock_exists):
        """
        Test 7: RAG failure after successful transcription.
        Verify RAG exceptions are caught cleanly if STT succeeds but retriever fails.
        """
        # WAV duration is 10s
        mock_wave_inst = MagicMock()
        mock_wave_inst.getnframes.return_value = 100
        mock_wave_inst.getframerate.return_value = 10
        mock_wave_open.return_value.__enter__.return_value = mock_wave_inst
        
        # Mock requests response
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.json.return_value = {
            "transcript": "what is a corporation?",
            "language_code": "en-IN",
            "request_id": "req-1"
        }
        mock_post.return_value = mock_res
        
        # Force retrieval to fail
        self.mock_retrieve.side_effect = RuntimeError("FAISS lookup error")
        
        voice_pipeline = VoiceRAGPipeline(index_path=self.index_path, meta_path=self.meta_path)
        
        with patch('builtins.open', mock_open(read_data=b"audiobytes")):
            res = voice_pipeline.answer_voice_query("sample.wav", "en-IN")
            
        self.assertEqual(res["transcript"], "what is a corporation?")
        self.assertEqual(res["answer"], "Retrieval process failed to execute.")
        self.assertEqual(res["sources"], [])
        self.assertGreater(res["rag_latency_ms"], 0)

    @patch('backend.app.speech_to_text.os.path.exists', return_value=True)
    @patch('backend.app.speech_to_text.os.path.getsize', return_value=1024)
    @patch('backend.app.speech_to_text.wave.open')
    @patch('backend.app.speech_to_text.requests.post')
    def test_api_key_protection(self, mock_post, mock_wave_open, mock_getsize, mock_exists):
        """
        Test 8: API key is never exposed.
        Verify that subscription secrets do not leak in error string payloads.
        """
        mock_wave_inst = MagicMock()
        mock_wave_inst.getnframes.return_value = 100
        mock_wave_inst.getframerate.return_value = 10
        mock_wave_open.return_value.__enter__.return_value = mock_wave_inst
        
        # Inject API key into error signature
        mock_post.side_effect = RuntimeError("Failed key dummy_sarvam_subscription_key_123")
        
        with patch('builtins.open', mock_open(read_data=b"audiobytes")):
            with self.assertRaises(RuntimeError) as context:
                transcribe_audio("sample.wav")
                
        err_msg = str(context.exception)
        self.assertNotIn("dummy_sarvam_subscription_key_123", err_msg)
        self.assertIn("STT API request failed due to authentication/service error.", err_msg)

if __name__ == "__main__":
    unittest.main()
