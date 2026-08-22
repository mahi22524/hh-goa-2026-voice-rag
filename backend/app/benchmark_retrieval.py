import sys
import os
import time
import json
import numpy as np

# Ensure backend/app is in Python path for relative imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

from retriever import Retriever

def main():
    index_path = os.path.join("data", "dev.index")
    meta_path = os.path.join("data", "dev_metadata.json")
    out_path = os.path.join("data", "retrieval_benchmark.json")

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        print("Error: Index files do not exist. Please run build_index.py first.")
        sys.exit(1)

    print("Loading Retriever for benchmarking...", flush=True)
    retriever = Retriever(index_path=index_path, meta_path=meta_path)

    # Extract queries from metadata
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
        
    metadata_map = meta_data.get("metadata_map", {})
    
    queries = []
    for pos_str, meta in metadata_map.items():
        eng_q = meta.get("Eng_Query")
        trans_q = meta.get("query")
        if eng_q and eng_q not in queries:
            queries.append(eng_q)
        if trans_q and trans_q not in queries:
            queries.append(trans_q)

    # Fallback queries if metadata is empty
    if not queries:
        queries = ["What is a corporation?", "How does a computer work?", "Where is HH Goa hosted?"]

    # Run 50 query runs total (repeat queries to make exactly 50 runs check)
    target_runs = 50
    run_queries = []
    while len(run_queries) < target_runs:
        run_queries.extend(queries)
    run_queries = run_queries[:target_runs]

    print(f"Running benchmark with {len(run_queries)} queries...", flush=True)
    latencies_ms = []

    # Warm up step to load lazy resources into CPU cache
    dummy_vector = retriever.embedder.encode(["warmup query"])
    retriever.vector_store.search(dummy_vector, top_k=3)

    for q in run_queries:
        t_start = time.perf_counter()
        q_vector = retriever.embedder.encode([q])
        retriever.vector_store.search(q_vector, top_k=3)
        duration = (time.perf_counter() - t_start) * 1000
        latencies_ms.append(duration)

    p50 = float(np.percentile(latencies_ms, 50))
    p70 = float(np.percentile(latencies_ms, 70))
    p100 = float(np.percentile(latencies_ms, 100))
    avg = float(np.mean(latencies_ms))

    print("\nBenchmark Results (ms):", flush=True)
    print(f"  P50 latency : {p50:.2f} ms", flush=True)
    print(f"  P70 latency : {p70:.2f} ms", flush=True)
    print(f"  P100 latency: {p100:.2f} ms", flush=True)
    print(f"  Avg latency : {avg:.2f} ms", flush=True)

    status = "PASS" if p100 < 200.0 else "FAIL"

    result = {
        "p50_ms": round(p50, 2),
        "p70_ms": round(p70, 2),
        "p100_ms": round(p100, 2),
        "avg_ms": round(avg, 2),
        "target_ms": 200.0,
        "status": status,
        "sample_size": target_runs
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Benchmark results written to '{out_path}'.")

if __name__ == "__main__":
    main()
