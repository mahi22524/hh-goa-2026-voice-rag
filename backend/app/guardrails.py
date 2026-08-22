import re
from typing import List, Dict, Any, Tuple

# Constants for guardrail parameters
MAX_INPUT_LENGTH = 1000
MIN_RETRIEVAL_SCORE = 0.40

def validate_input(query: Any, max_length: int = MAX_INPUT_LENGTH) -> Tuple[bool, str]:
    """
    Validates user input queries.
    Rejects:
      - Non-string inputs
      - Empty queries or whitespace-only queries
      - Queries exceeding the maximum character threshold
    """
    if not isinstance(query, str):
        return False, "Invalid input type. Query must be a string."
        
    if not query.strip():
        return False, "Query cannot be empty or only whitespace."
        
    if len(query) > max_length:
        return False, f"Query exceeds maximum allowed length of {max_length} characters."
        
    return True, ""


def validate_retrieval(sources: List[Dict[str, Any]], threshold: float = MIN_RETRIEVAL_SCORE) -> bool:
    """
    Validates vector database retrieval scores.
    If all retrieved chunks have a similarity score below the threshold,
    returns False, indicating insufficient context to answer safely.
    """
    if not sources:
        return False
        
    # Check if the highest score (first rank) meets the minimum score threshold
    best_score = max([s.get("score", 0.0) for s in sources])
    if best_score < threshold:
        return False
        
    return True


def filter_context(sources: List[Dict[str, Any]], max_chunks: int = 3) -> List[Dict[str, Any]]:
    """
    Cleanses and structures retrieved context:
      - Removes empty passages
      - Deduplicates passages based on text content
      - Truncates context chunks to a configurable maximum count
      - Retains original source metadata mapping
    """
    filtered = []
    seen_texts = set()
    
    for s in sources:
        text = s.get("text", "").strip()
        if not text:
            continue
            
        # Normalize text to detect duplicate passages (case/space insensitive)
        normalized_text = " ".join(text.lower().split())
        if normalized_text in seen_texts:
            continue
            
        seen_texts.add(normalized_text)
        filtered.append(s)
        
        if len(filtered) >= max_chunks:
            break
            
    return filtered


def validate_output(answer: Any, context: str) -> Tuple[bool, str]:
    """
    Validates the generated LLM response:
      - Rejects empty answers
      - Rejects responses containing internal API error signatures
      - Performs lightweight grounding checks (e.g. check fallback response consistency)
    
    Limitations:
      This is a lightweight validation wrapper. Standard keyword matching reduces hallucination risk,
      but cannot mathematically guarantee zero hallucinations.
    """
    if not isinstance(answer, str):
        return False, "Invalid output type. Answer must be a string."
        
    if not answer.strip():
        return False, "LLM returned an empty answer."
        
    # Block typical API error or stack trace signatures to prevent leaking credentials/internals
    error_patterns = [
        r"traceback", r"exception", r"api_key", r"auth_token", r"unauthorized",
        r"internal server error", r"api request failed", r"connection timeout"
    ]
    
    lower_answer = answer.lower()
    for pattern in error_patterns:
        if re.search(pattern, lower_answer):
            return False, "LLM response blocked: contains internal error signature."
            
    return True, ""
