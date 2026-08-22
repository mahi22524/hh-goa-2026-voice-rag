import os
import sys
import time

# Ensure backend/app is in Python path for relative imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

from dotenv import load_dotenv
from retriever import Retriever
from llm_providers import MockLLMProvider, GeminiLLMProvider, OpenAILLMProvider
from guardrails import (
    validate_input,
    validate_retrieval,
    filter_context,
    validate_output,
    MIN_RETRIEVAL_SCORE,
    MAX_INPUT_LENGTH
)

# Load environment variables from .env
load_dotenv()

class RAGPipeline:
    def __init__(self, index_path: str = os.path.join("data", "dev.index"), meta_path: str = os.path.join("data", "dev_metadata.json")):
        """
        Initializes the Grounded RAG Pipeline, including the vector retriever
        and the configured LLM provider.
        """
        self.retriever = Retriever(index_path=index_path, meta_path=meta_path)
        self.provider_name = os.environ.get("LLM_PROVIDER", "mock").lower()
        
        if self.provider_name == "gemini":
            self.llm = GeminiLLMProvider()
        elif self.provider_name == "openai":
            self.llm = OpenAILLMProvider()
        else:
            if self.provider_name != "mock":
                print(f"Warning: Unknown LLM provider '{self.provider_name}'. Defaulting to 'mock'.", flush=True)
            self.llm = MockLLMProvider()
            
        print(f"RAG Pipeline initialized with LLM Provider: '{self.provider_name.upper()}'\n", flush=True)

    def answer_question(self, query: str, top_k: int = 3, language_code: str = None) -> dict:
        """
        Processes query through the Guarded RAG flow:
        Input Validation -> FAISS Retrieval -> Retrieval score filter -> Context filtering -> LLM -> Output validation.
        """
        fallback_msg = "I don't have enough information in the provided context to answer that."
        t_start = time.perf_counter()
        
        # 1. Input Guardrail
        is_valid_in, in_err = validate_input(query, MAX_INPUT_LENGTH)
        if not is_valid_in:
            return {
                "question": query if isinstance(query, str) else str(query),
                "answer": in_err,
                "retrieved_sources": [],
                "retrieval_latency": 0.0,
                "llm_latency": 0.0,
                "total_latency": time.perf_counter() - t_start,
                "status": "input_rejected"
            }
            
        # 2. Retrieval Stage
        t_retrieval_start = time.perf_counter()
        try:
            raw_sources = self.retriever.retrieve(query, top_k=top_k, language_code=language_code)
        except Exception as e:
            # Handle retrieval failure gracefully (do not leak internal trace details/directories)
            print(f"ERROR [Local log only - DB Failure]: {e}", flush=True)
            return {
                "question": query,
                "answer": "Retrieval process failed to execute.",
                "retrieved_sources": [],
                "retrieval_latency": time.perf_counter() - t_retrieval_start,
                "llm_latency": 0.0,
                "total_latency": time.perf_counter() - t_start,
                "status": "retrieval_failure",
                "error": "Database lookup failed."
            }
            
        t_retrieval = time.perf_counter() - t_retrieval_start
        
        # 3. Retrieval Score Guardrail (LLM Bypass)
        is_valid_retrieval = validate_retrieval(raw_sources, MIN_RETRIEVAL_SCORE)
        if not is_valid_retrieval:
            return {
                "question": query,
                "answer": fallback_msg,
                "retrieved_sources": raw_sources,
                "retrieval_latency": t_retrieval,
                "llm_latency": 0.0,  # LLM bypassed!
                "total_latency": time.perf_counter() - t_start,
                "status": "insufficient_context"
            }
            
        # 4. Context Selection Guardrail (Clean and deduplicate)
        cleaned_sources = filter_context(raw_sources, max_chunks=top_k)
        
        lang_name = "English"
        if language_code:
            code = language_code.lower().split("-")[0]
            mapping = {
                "ta": "Tamil",
                "hi": "Hindi",
                "gu": "Gujarati",
                "te": "Telugu",
                "ur": "Urdu",
                "bn": "Bengali",
                "mr": "Marathi",
                "pa": "Punjabi",
                "ml": "Malayalam",
                "kn": "Kannada",
                "or": "Odia"
            }
            lang_name = mapping.get(code, "English")

        # 5. Generation Stage
        # Construct strict system prompt
        system_instruction = (
            "You are a grounded question-answering system.\n"
            "Answer the user's question using ONLY the supplied retrieved context.\n"
            "Do not use outside knowledge.\n"
            "Do not invent facts, names, dates, numbers, or explanations that are not supported by the context.\n"
            f"The final answer must be generated in the language identified by the user's query/language_code ({lang_name}). Do not change the language of the user's question.\n"
            "If the context does not contain enough information to answer the question, say:\n"
            "\"I don't have enough information in the provided context to answer that.\"\n"
            "Do not pretend that unsupported information is present in the context."
        )
        
        # Format the passages context block
        passages_text = "\n".join([
            f"- [Source {r['rank']} (query_id={r['metadata'].get('query_id')}, index={r['metadata'].get('passage_index')})]: {r['text']}" 
            for r in cleaned_sources
        ])
        
        prompt = (
            f"Question: {query}\n\n"
            f"Retrieved Context Passages:\n{passages_text}\n"
        )
        
        t_llm_start = time.perf_counter()
        try:
            answer = self.llm.generate_answer(prompt, system_instruction)
        except Exception as e:
            # Handle LLM execution failure gracefully (mask keys/secrets in logs)
            masked_error = str(e)
            # Mask API keys if they accidentally appear in the exception message
            if "key" in masked_error.lower():
                masked_error = "API request failed due to authentication/service error."
            print(f"ERROR [Local log only - API Failure]: {masked_error}", flush=True)
            
            return {
                "question": query,
                "answer": "LLM generation failed to execute.",
                "retrieved_sources": cleaned_sources,
                "retrieval_latency": t_retrieval,
                "llm_latency": time.perf_counter() - t_llm_start,
                "total_latency": time.perf_counter() - t_start,
                "status": "llm_failure",
                "error": masked_error
            }
            
        t_llm = time.perf_counter() - t_llm_start
        t_total = time.perf_counter() - t_start
        
        # Grounding check check
        if fallback_msg.lower() in answer.lower():
            answer = fallback_msg
            
        # 6. Output Guardrail
        is_valid_out, out_err = validate_output(answer, passages_text)
        if not is_valid_out:
            return {
                "question": query,
                "answer": fallback_msg,  # Default to fallback response if output check fails
                "retrieved_sources": cleaned_sources,
                "retrieval_latency": t_retrieval,
                "llm_latency": t_llm,
                "total_latency": t_total,
                "status": "output_blocked",
                "error": out_err
            }
            
        return {
            "question": query,
            "answer": answer,
            "retrieved_sources": cleaned_sources,
            "retrieval_latency": t_retrieval,
            "llm_latency": t_llm,
            "total_latency": t_total,
            "status": "success" if answer != fallback_msg else "insufficient_context"
        }
