import sys
import os

# Ensure backend/app is in Python path for relative imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

from rag_pipeline import RAGPipeline

def main():
    # Configure UTF-8 for stdout/stderr on Windows terminal
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
            
    index_path = os.path.join("data", "dev.index")
    meta_path = os.path.join("data", "dev_metadata.json")
    
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        print(f"Error: Vector index files do not exist at '{index_path}' or '{meta_path}'. Please run build_index.py first.", flush=True)
        sys.exit(1)
        
    print("==================================================", flush=True)
    print("HH Goa 2026 - Interactive Grounded RAG System", flush=True)
    print("==================================================", flush=True)
    
    # Initialize pipeline
    pipeline = RAGPipeline(index_path=index_path, meta_path=meta_path)
    
    print("Enter your questions below. Type 'exit' or 'quit' to end the session.\n", flush=True)
    
    while True:
        try:
            # Prompt user
            sys.stdout.write("Ask RAG: ")
            sys.stdout.flush()
            query = sys.stdin.readline()
            
            # End of stream or quit
            if not query:
                break
                
            query = query.strip()
            if query.lower() in ["exit", "quit"]:
                break
                
            if not query:
                continue
                
            print("\nProcessing...", flush=True)
            res = pipeline.answer_question(query, top_k=3)
            
            print("\n" + "=" * 60, flush=True)
            print(f"QUESTION: {res['question']}", flush=True)
            print("=" * 60, flush=True)
            
            print("RETRIEVED SOURCES:", flush=True)
            if res["retrieved_sources"]:
                for r in res["retrieved_sources"]:
                    truncated_text = r["text"][:120] + "... [TRUNCATED]" if len(r["text"]) > 120 else r["text"]
                    print(f"  [{r['rank']}] Cosine Score: {r['score']:.4f} (lang: {r['metadata'].get('language')})", flush=True)
                    print(f"      Text: {truncated_text}", flush=True)
            else:
                print("  No sources retrieved.", flush=True)
            print("-" * 60, flush=True)
            
            print("ANSWER:", flush=True)
            print(res["answer"], flush=True)
            print("=" * 60, flush=True)
            
            print("LATENCY METRICS:", flush=True)
            print(f"  - Retrieval latency : {res['retrieval_latency']*1000:.2f} ms", flush=True)
            print(f"  - LLM latency       : {res['llm_latency']*1000:.2f} ms", flush=True)
            print(f"  - Total RAG latency : {res['total_latency']*1000:.2f} ms", flush=True)
            print("=" * 60 + "\n", flush=True)
            
        except KeyboardInterrupt:
            print("\nExiting interactive session.", flush=True)
            break
        except Exception as e:
            print(f"\nError processing query: {e}\n", flush=True)

if __name__ == "__main__":
    main()
