import sys
import os

# Ensure backend/app is in Python path for relative imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

import argparse
from voice_rag import VoiceRAGPipeline

def main():
    # Configure UTF-8 for stdout/stderr on Windows terminal
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Test Voice-Enabled RAG System with an audio file.")
    parser.add_argument(
        "audio_path",
        type=str,
        help="Path to the audio file (e.g., path/to/sample.wav)."
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Optional language selection code (e.g., 'en-IN', 'te-IN', 'hi-IN')."
    )
    args = parser.parse_args()

    index_path = os.path.join("data", "dev.index")
    meta_path = os.path.join("data", "dev_metadata.json")

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        print(f"Error: Vector index files do not exist at '{index_path}' or '{meta_path}'. Please run build_index.py first.", flush=True)
        sys.exit(1)

    print("Initializing Voice RAG Pipeline (this may take a moment to load models)...", flush=True)
    try:
        pipeline = VoiceRAGPipeline(index_path=index_path, meta_path=meta_path)
    except Exception as e:
        print(f"Error: Failed to initialize pipeline: {e}", flush=True)
        sys.exit(1)

    print(f"Processing audio file: '{args.audio_path}'...\n", flush=True)
    res = pipeline.answer_voice_query(args.audio_path, args.language)

    print("========================================", flush=True)
    print("HH GOA 2026 VOICE RAG", flush=True)
    print("========================================\n", flush=True)

    print("TRANSCRIPT:", flush=True)
    print(res["transcript"] if res["transcript"] else "[No transcript generated]", flush=True)
    print("\nLANGUAGE:", flush=True)
    print(res["language_code"] if res["language_code"] else "[Unknown]", flush=True)
    print("\nRETRIEVED SOURCES:", flush=True)
    
    if res["sources"]:
        for s in res["sources"]:
            truncated_text = s["text"][:120] + "... [TRUNCATED]" if len(s["text"]) > 120 else s["text"]
            print(f"  {s['rank']}. Cosine Score: {s['score']:.4f} (lang: {s['metadata'].get('language')})", flush=True)
            print(f"      Text: {truncated_text}", flush=True)
            print(f"      query_id: {s['metadata'].get('query_id')}, passage_index: {s['metadata'].get('passage_index')}", flush=True)
            print("-" * 30, flush=True)
    else:
        print("  No sources retrieved.", flush=True)

    print("\nANSWER:", flush=True)
    print(res["answer"], flush=True)
    
    print("\nLATENCY:", flush=True)
    print(f"STT   : {res['stt_latency_ms']:.2f} ms", flush=True)
    print(f"RAG   : {res['rag_latency_ms']:.2f} ms (Retrieval: {res['retrieval_latency_ms']:.2f} ms)", flush=True)
    print(f"TOTAL : {res['total_latency_ms']:.2f} ms", flush=True)
    print("========================================", flush=True)

if __name__ == "__main__":
    main()
