import os
import sys
import wave
import requests
from typing import Dict, Any, Tuple

# Ensure backend/app is in Python path for relative imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

# Max audio file size is 10 MB
MAX_AUDIO_SIZE = 10 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"}

def validate_audio(filepath: str) -> Tuple[bool, str]:
    """
    Validates the input audio file:
      - Checks file existence and size.
      - Checks supported extension formats.
      - If WAV format, checks duration is <= 30 seconds.
    """
    if not isinstance(filepath, str) or not filepath.strip():
        return False, "Audio filepath must be a valid non-empty string."
        
    if not os.path.exists(filepath):
        return False, f"Audio file not found at: {filepath}"
        
    file_size = os.path.getsize(filepath)
    if file_size == 0:
        return False, "Audio file is empty."
        
    if file_size > MAX_AUDIO_SIZE:
        return False, f"Audio file exceeds maximum size limit of {MAX_AUDIO_SIZE / (1024*1024):.1f} MB."
        
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False, f"Unsupported audio type '{ext}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        
    # Standard library duration check for WAV files
    if ext == ".wav":
        try:
            with wave.open(filepath, "rb") as w:
                frames = w.getnframes()
                rate = w.getframerate()
                if rate > 0:
                    duration = frames / float(rate)
                    if duration > 30.0:
                        return False, f"Audio duration ({duration:.2f}s) exceeds maximum allowed limit of 30 seconds."
                else:
                    return False, "Invalid WAV samplerate (0)."
        except wave.Error as e:
            return False, f"Malformed WAV file header: {e}"
        except Exception as e:
            # Fallback if other standard OS errors happen
            return False, f"Failed to parse WAV header: {e}"
            
    return True, ""


def transcribe_audio(filepath: str, language_code: str = None) -> Dict[str, Any]:
    """
    Sends the audio file to Sarvam AI Saaras v3 REST endpoint to transcribe.
    Headers: api-subscription-key
    Body parameters (form-data): file, model="saaras:v3", mode="transcribe", language_code
    """
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY environment variable is not set.")
        
    # 1. Run local validation
    is_valid, err_msg = validate_audio(filepath)
    if not is_valid:
        raise ValueError(err_msg)
        
    url = "https://api.sarvam.ai/speech-to-text"
    headers = {
        "api-subscription-key": api_key
    }
    
    data = {
        "model": "saaras:v3",
        "mode": "transcribe"
    }
    
    if language_code:
        data["language_code"] = language_code
        
    try:
        filename = os.path.basename(filepath)
        # Determine content type based on extension
        ext = os.path.splitext(filepath)[1].lower()
        content_type = "audio/wav" if ext == ".wav" else f"audio/{ext.lstrip('.')}"
        
        with open(filepath, "rb") as audio_file:
            files = {
                "file": (filename, audio_file, content_type)
            }
            
            response = requests.post(url, headers=headers, data=data, files=files, timeout=35)
            response.raise_for_status()
            res_json = response.json()
            
            # Format output
            transcript = res_json.get("transcript", "").strip()
            lang = res_json.get("language_code", language_code or "auto")
            req_id = res_json.get("request_id", "none")
            
            return {
                "transcript": transcript,
                "language_code": lang,
                "request_id": req_id
            }
    except Exception as e:
        # Secure error masking: remove key signature
        masked_error = str(e)
        if api_key in masked_error:
            masked_error = masked_error.replace(api_key, "[MASKED_KEY]")
        if "key" in masked_error.lower():
            masked_error = "STT API request failed due to authentication/service error."
        print(f"ERROR [Local log only - STT API Failure]: {masked_error}", flush=True)
        raise RuntimeError(f"Speech-to-Text transcription failed: {masked_error}")
