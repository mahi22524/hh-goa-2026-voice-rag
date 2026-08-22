import sys
import os

# Ensure backend/app is in Python path for relative imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

import json
import time
from retriever import Retriever

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
        print(f"Error: Index files do not exist at '{index_path}' or '{meta_path}'. Please run build_index.py first.", flush=True)
        sys.exit(1)

    print("==================================================", flush=True)
    print("HH Goa 2026 - RAG Retrieval Evaluation & Benchmark", flush=True)
    print("==================================================\n", flush=True)

    # 1. Benchmark: Model loading and Index loading
    print("Loading Retriever (Model + FAISS Index)...", flush=True)
    t_load_start = time.perf_counter()
    retriever = Retriever(index_path=index_path, meta_path=meta_path)
    t_load = time.perf_counter() - t_load_start
    print(f"Retriever loaded in {t_load:.4f} seconds.\n", flush=True)

    # 2. Extract real test queries from the loaded index metadata map
    print("Extracting queries from index metadata...", flush=True)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
        
    metadata_map = meta_data.get("metadata_map", {})
    
    # Collect unique test queries present in the development dataset
    # We map query_id to its text representation (English and Target translated language)
    queries_dict = {}
    for pos_str, meta in metadata_map.items():
        q_id = meta.get("query_id")
        if q_id is not None and q_id not in queries_dict:
            # Prefer English query or target language query
            eng_q = meta.get("Eng_Query")
            trans_q = meta.get("query")
            
            queries_dict[q_id] = {
                "Eng_Query": eng_q,
                "query": trans_q,
                "target_lang": meta.get("target_lang")
            }
            
    test_queries = []
    # Take up to 5 unique queries to run tests
    for q_id, q_info in list(queries_dict.items())[:5]:
        # Test both the English version and the Indic translated version!
        if q_info["Eng_Query"]:
            test_queries.append((q_id, q_info["Eng_Query"], "en"))
        if q_info["query"] and q_info["query"] != q_info["Eng_Query"]:
            test_queries.append((q_id, q_info["query"], q_info["target_lang"]))
            
    print(f"Extracted {len(test_queries)} test queries.\n", flush=True)
    if not test_queries:
        print("Error: No test queries could be extracted from metadata.", flush=True)
        sys.exit(1)

    # 3. Execute Retrieval and Quality Checks
    eval_results = []
    query_latencies = []
    embed_latencies = []
    search_latencies = []

    for q_id, q_text, lang in test_queries:
        print("=" * 50, flush=True)
        print("QUERY", flush=True)
        print("=" * 50, flush=True)
        print(f"Query text  : {q_text}", flush=True)
        print(f"Query ID    : {q_id}", flush=True)
        print(f"Language    : {lang}", flush=True)
        print("\nTOP RESULTS\n", flush=True)
        
        # Benchmark individual pipeline steps
        t_pipeline_start = time.perf_counter()
        
        # Step A: Query embedding
        t_embed_start = time.perf_counter()
        query_vector = retriever.embedder.encode([q_text])
        t_embed = time.perf_counter() - t_embed_start
        
        # Step B: FAISS search
        t_search_start = time.perf_counter()
        raw_results = retriever.vector_store.search(query_vector, top_k=3)
        t_search = time.perf_counter() - t_search_start
        
        t_pipeline = time.perf_counter() - t_pipeline_start
        
        query_latencies.append(t_pipeline)
        embed_latencies.append(t_embed)
        search_latencies.append(t_search)
        
        # Process and print retrieved results
        success = False
        for idx, (rank, score, text, metadata) in enumerate(raw_results):
            truncated_text = text[:150] + "... [TRUNCATED]" if len(text) > 150 else text
            
            # Ground-truth verification:
            # If the retrieved chunk is from the same query_id and has is_selected == 1
            # in the source record, it means it's a correct passage retrieval!
            is_relevant = (metadata.get("query_id") == q_id and metadata.get("is_selected") == 1)
            if is_relevant:
                success = True
                
            print(f"{rank}.", flush=True)
            print(f"Score         : {score:.4f}", flush=True)
            print(f"Text          : {truncated_text}", flush=True)
            print(f"query_id      : {metadata.get('query_id')}", flush=True)
            print(f"passage_index : {metadata.get('passage_index')}", flush=True)
            print(f"language      : {metadata.get('language')}", flush=True)
            print(f"is_selected   : {metadata.get('is_selected')} (Relevance: {'RELEVANT' if is_relevant else 'OTHER'})", flush=True)
            print("-" * 30, flush=True)
            
        eval_results.append({
            "query_id": q_id,
            "success": success
        })
        print(f"Pipeline latency: {t_pipeline*1000:.2f} ms (Embedding: {t_embed*1000:.2f} ms, Search: {t_search*1000:.2f} ms)\n", flush=True)

    # 4. Retrieval Quality Metrics
    print("=" * 50, flush=True)
    print("RETRIEVAL QUALITY CHECK", flush=True)
    print("=" * 50, flush=True)
    
    total_queries = len(eval_results)
    successful_retrievals = sum(1 for r in eval_results if r["success"])
    
    # Calculate accuracy
    if total_queries > 0:
        accuracy = (successful_retrievals / total_queries) * 100
        print(f"Ground-Truth Evaluation (Top-K=3):", flush=True)
        print(f"  - Total queries evaluated: {total_queries}", flush=True)
        print(f"  - Queries where a selected/relevant passage was retrieved: {successful_retrievals}", flush=True)
        print(f"  - Retrieval Accuracy (Top-K Recall): {accuracy:.2f}%", flush=True)
    else:
        print("Reliable retrieval accuracy cannot be calculated from this test setup.", flush=True)
    print("\n", flush=True)

    # 5. Latency Benchmarks
    print("==================================================", flush=True)
    print("LOCAL DEVELOPMENT BENCHMARK", flush=True)
    print("==================================================", flush=True)
    print(f"Embedding model loading time : {t_load:.4f} seconds", flush=True)
    
    avg_query_time = sum(query_latencies) / len(query_latencies) if query_latencies else 0
    avg_embed_time = sum(embed_latencies) / len(embed_latencies) if embed_latencies else 0
    avg_search_time = sum(search_latencies) / len(search_latencies) if search_latencies else 0
    
    print(f"Average query embedding time : {avg_embed_time*1000:.2f} ms", flush=True)
    print(f"Average FAISS retrieval time : {avg_search_time*1000:.2f} ms", flush=True)
    print(f"Average total retrieval time : {avg_query_time*1000:.2f} ms", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    main()
