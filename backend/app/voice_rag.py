import os
import sys
import time
from typing import Dict, Any

# Ensure backend/app is in Python path for relative imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

from speech_to_text import transcribe_audio, validate_audio
from rag_pipeline import RAGPipeline

class VoiceRAGPipeline:
    def __init__(self, index_path: str = os.path.join("data", "dev.index"), meta_path: str = os.path.join("data", "dev_metadata.json")):
        """
        Orchestration pipeline integrating Sarvam STT and the Grounded RAG core.
        """
        # Load the RAG core
        self.rag = RAGPipeline(index_path=index_path, meta_path=meta_path)

    def answer_voice_query(self, audio_path: str, language_code: str = None) -> Dict[str, Any]:
        """
        Processes voice query:
        Validate Audio -> Transcribe Audio -> Vector Retrieval -> LLM -> Response
        """
        t_start = time.perf_counter()
        
        # 1. Audio Validation Guardrail
        is_valid_audio, audio_err = validate_audio(audio_path)
        if not is_valid_audio:
            return {
                "transcript": "",
                "language_code": "",
                "answer": f"Audio validation failed: {audio_err}",
                "sources": [],
                "retrieval_latency_ms": 0.0,
                "stt_latency_ms": 0.0,
                "rag_latency_ms": 0.0,
                "total_latency_ms": (time.perf_counter() - t_start) * 1000
            }
            
        # 2. Speech-to-Text Stage
        t_stt_start = time.perf_counter()
        try:
            stt_res = transcribe_audio(audio_path, language_code)
            transcript = stt_res["transcript"]
            lang = stt_res["language_code"]
        except Exception as e:
            # Handle STT failures cleanly without calling RAG
            t_stt = time.perf_counter() - t_stt_start
            return {
                "transcript": "",
                "language_code": "",
                "answer": "Speech-to-Text transcription failed.",
                "sources": [],
                "retrieval_latency_ms": 0.0,
                "stt_latency_ms": t_stt * 1000,
                "rag_latency_ms": 0.0,
                "total_latency_ms": (time.perf_counter() - t_start) * 1000,
                "status": "stt_failure",
                "error": str(e)
            }
            
        t_stt = time.perf_counter() - t_stt_start
        
        # 3. Grounded RAG Stage
        t_rag_start = time.perf_counter()
        try:
            rag_res = self.rag.answer_question(transcript, language_code=lang)
            answer = rag_res["answer"]
            sources = rag_res["retrieved_sources"]
            retrieval_latency = rag_res["retrieval_latency"]
        except Exception as e:
            # Handle post-transcription RAG failures cleanly
            t_rag = time.perf_counter() - t_rag_start
            return {
                "transcript": transcript,
                "language_code": lang,
                "answer": "RAG pipeline failed to execute.",
                "sources": [],
                "retrieval_latency_ms": 0.0,
                "stt_latency_ms": t_stt * 1000,
                "rag_latency_ms": t_rag * 1000,
                "total_latency_ms": (time.perf_counter() - t_start) * 1000,
                "status": "rag_failure",
                "error": str(e)
            }
            
        t_rag = time.perf_counter() - t_rag_start
        t_total = time.perf_counter() - t_start
        
        return {
            "transcript": transcript,
            "language_code": lang,
            "answer": answer,
            "sources": sources,
            "retrieval_latency_ms": retrieval_latency * 1000,
            "stt_latency_ms": t_stt * 1000,
            "rag_latency_ms": t_rag * 1000,
            "total_latency_ms": t_total * 1000
        }
