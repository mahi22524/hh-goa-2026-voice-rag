import sys
import time
import argparse
from data_loader import load_dev_sample, extract_passages
from chunker import PassageChunker

def main():
    # Configure UTF-8 for stdout/stderr on Windows terminal
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
            
    parser = argparse.ArgumentParser(description="Compare dataset chunking strategies.")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=100,
        help="Number of records to stream for the development sample (default: 100)."
    )
    parser.add_argument(
        "--split",
        type=str,
        default="train",
        choices=["train", "validation"],
        help="Dataset split to stream from (default: 'train')."
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Target chunk size in characters (default: 500)."
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=100,
        help="Chunk overlap in characters (default: 100)."
    )
    args = parser.parse_args()
    
    print("==================================================", flush=True)
    print("HH Goa 2026 - Phase 3 Chunker Comparison", flush=True)
    print("==================================================\n", flush=True)
    
    # 1. Load dev sample records
    try:
        raw_records = load_dev_sample(sample_size=args.sample_size, split=args.split)
    except Exception as e:
        print(f"Error: Failed to load development sample: {e}", flush=True)
        sys.exit(1)
        
    if not raw_records:
        print("Error: No records were loaded.", flush=True)
        sys.exit(1)
        
    # 2. Extract individual passages
    print("\nExtracting individual source passages...", flush=True)
    passages = extract_passages(raw_records)
    print(f"Extracted {len(passages)} individual source passages (English + Translations).\n", flush=True)
    
    if not passages:
        print("Error: No passages extracted from the sample records.", flush=True)
        sys.exit(1)
        
    # Initialize chunker
    chunker = PassageChunker(chunk_size=args.chunk_size, overlap=args.overlap)
    strategies = ["passage", "overlap", "sentence"]
    results = {}
    
    # 3. Run and measure each strategy
    for strategy in strategies:
        print(f"Running strategy '{strategy}'...", flush=True)
        t0 = time.time()
        
        all_chunks = []
        for p in passages:
            chunks = chunker.chunk(p["text"], p["metadata"], strategy=strategy)
            all_chunks.extend(chunks)
            
        elapsed = time.time() - t0
        
        # Calculate statistics
        num_chunks = len(all_chunks)
        if num_chunks > 0:
            lengths = [len(c.text) for c in all_chunks]
            avg_len = sum(lengths) / len(lengths)
            min_len = min(lengths)
            max_len = max(lengths)
        else:
            avg_len = min_len = max_len = 0
            
        results[strategy] = {
            "count": num_chunks,
            "avg_length": avg_len,
            "min_length": min_len,
            "max_length": max_len,
            "time_seconds": elapsed
        }
        
    # 4. Print Comparison Report
    print("\n" + "=" * 80, flush=True)
    print(f"{'STRATEGY':<18} | {'CHUNKS':<8} | {'AVG LEN':<9} | {'MIN LEN':<8} | {'MAX LEN':<8} | {'TIME (s)':<10}", flush=True)
    print("-" * 80, flush=True)
    for strategy in strategies:
        res = results[strategy]
        print(f"{strategy.upper():<18} | {res['count']:<8} | {res['avg_length']:<9.2f} | {res['min_length']:<8} | {res['max_length']:<8} | {res['time_seconds']:<10.4f}", flush=True)
    print("=" * 80 + "\n", flush=True)
    
    # 5. Show sample chunk trace
    print("Sample Chunk Example (from Overlapping Strategy):", flush=True)
    # Find a passage that was split (total_chunks > 1) if possible
    sample_chunk = None
    for p in passages:
        overlap_chunks = chunker.chunk(p["text"], p["metadata"], strategy="overlap")
        if len(overlap_chunks) > 1:
            sample_chunk = overlap_chunks[1] # Print the second chunk to show overlap / offset
            break
            
    if not sample_chunk and passages:
        # Fallback to first chunk of first passage
        overlap_chunks = chunker.chunk(passages[0]["text"], passages[0]["metadata"], strategy="overlap")
        if overlap_chunks:
            sample_chunk = overlap_chunks[0]
            
    if sample_chunk:
        print(f"  Text: {sample_chunk.text[:120]}...", flush=True)
        print(f"  Metadata keys: {list(sample_chunk.metadata.keys())}", flush=True)
        print(f"  Trace Metadata: query_id={sample_chunk.metadata.get('query_id')}, passage_index={sample_chunk.metadata.get('passage_index')}, language={sample_chunk.metadata.get('language')}, chunk_index={sample_chunk.metadata.get('chunk_index')}", flush=True)
    else:
        print("  No chunks generated to display.", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    main()
