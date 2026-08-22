import os
import requests
from typing import List, Dict, Any

class LLMProvider:
    def generate_answer(self, prompt: str, system_instruction: str) -> str:
        """
        Base interface for modular LLM answer generation.
        """
        raise NotImplementedError("Subclasses must implement generate_answer.")


class MockLLMProvider(LLMProvider):
    def generate_answer(self, prompt: str, system_instruction: str) -> str:
        """
        Mock LLM provider for resource-safe offline testing.
        Searches context inside prompt for relevant sentences or returns default fallbacks.
        """
        # Parse the prompt to locate the Question and Context
        lower_prompt = prompt.lower()
        lower_system = system_instruction.lower()
        
        lang = "english"
        if "hindi" in lower_system:
            lang = "hindi"
        elif "telugu" in lower_system:
            lang = "telugu"
        elif "urdu" in lower_system:
            lang = "urdu"
            
        fallback_msg = "I don't have enough information in the provided context to answer that."
        if lang == "hindi":
            fallback_msg = "मेरे पास इसका उत्तर देने के लिए दिए गए संदर्भ में पर्याप्त जानकारी नहीं है।"
        elif lang == "telugu":
            fallback_msg = "అందించిన సందర్భంలో దీనికి సమాధానం ఇవ్వడానికి నా దగ్గర సరిపడా సమాచారం లేదు।"
        elif lang == "urdu":
            fallback_msg = "میرے پاس فراہم کردہ سیاق و سباق میں اس کا جواب دینے کے لیے کافی معلومات نہیں ہیں۔"
        
        # Simple rule-based mock logic
        if "corporation" in lower_prompt:
            if "authorized to act as a single entity" in lower_prompt or "کارپوریشن ایک کمپنی" in lower_prompt:
                if lang == "hindi":
                    return "कारपोरेशन एक कंपनी या लोगों का समूह है जिसे एक इकाई के रूप में कार्य करने के लिए अधिकृत किया गया है और कानून में इस तरह से मान्यता प्राप्त है।"
                elif lang == "telugu":
                    return "కార్పొరేషన్ అనేది చట్టంలో ఒకే సంస్థగా వ్యవహరించడానికి అధికారం కలిగి ఉన్న మరియు గుర్తించబడిన ఒక కంపెనీ లేదా వ్యక్తుల సమూహం।"
                elif lang == "urdu":
                    return "کارپوریشن ایک کمپنی یا لوگوں کا ایسا گروپ ہے جو قانون میں ایک واحد ادارے کے طور پر کام کرنے اور اس طرح تسلیم کیے جانے کے لیے مجاز ہے۔"
                return "A corporation is a company or group of people authorized to act as a single entity and recognized as such in law."
                
        if "cargo ship" in lower_prompt or "مال بردار جہاز" in lower_prompt:
            if "belly of a massive cargo ship" in lower_prompt or "shipned" in lower_prompt:
                return "The bottom front of a cargo ship is part of its hull/belly, and ships like flat bottom tankers are often traded internationally."
                
        if "honesty" in lower_prompt or "integrity" in lower_prompt or "دیانت داری" in lower_prompt:
            if "consistency of actions" in lower_prompt or "ایماندار ہونے की हालत" in lower_prompt:
                return "Integrity is a concept of consistency of actions, values, and principles. Honesty is the quality of being honest."
                
        # If no specific matches, check if prompt contains generic content
        # We look for context sentences that might answer typical queries
        # (This is just a fallback for dynamic testing)
        if "context passages:" in lower_prompt:
            passages_block = lower_prompt.split("context passages:")[1]
            # Simple keyword overlap matching between query and context sentences
            query_line = ""
            if "question:" in lower_prompt:
                query_line = lower_prompt.split("question:")[1].split("\n")[0].strip()
                
            query_words = [w for w in query_line.split() if len(w) > 3]
            
            # Search context lines
            for line in passages_block.split("\n"):
                line = line.strip()
                if not line:
                    continue
                # If a line shares multiple keywords with the query, return it
                matches = sum(1 for w in query_words if w in line)
                if matches >= 2:
                    # Clean up prefix punctuation
                    clean_line = line.lstrip("-*1234567890. ")
                    return f"Based on the context: {clean_line}"

        return fallback_msg


class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = "gemini-1.5-flash"
        
    def generate_answer(self, prompt: str, system_instruction: str) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "generationConfig": {
                "temperature": 0.0,  # Zero temperature for factual grounded output
                "maxOutputTokens": 1024
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            res_json = response.json()
            
            # Parse text response
            candidates = res_json.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return text.strip()
                
            raise ValueError(f"Unexpected response structure from Gemini API: {res_json}")
        except Exception as e:
            print(f"Gemini API request failed: {e}", flush=True)
            raise e


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = "gpt-4o-mini"
        
    def generate_answer(self, prompt: str, system_instruction: str) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
            
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            res_json = response.json()
            
            choices = res_json.get("choices", [])
            if choices:
                text = choices[0].get("message", {}).get("content", "")
                return text.strip()
                
            raise ValueError(f"Unexpected response structure from OpenAI API: {res_json}")
        except Exception as e:
            print(f"OpenAI API request failed: {e}", flush=True)
            raise e
