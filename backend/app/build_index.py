import sys
import os

# Ensure backend/app is in Python path for relative imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

import argparse
import time
from data_loader import load_dev_sample, extract_passages
from chunker import PassageChunker
from embedder import EmbeddingService
from vector_store import VectorStore

def main():
    # Configure UTF-8 for stdout/stderr on Windows terminal
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Build RAG development vector index.")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=15,
        help="Number of records to stream for building the index (default: 15)."
    )
    parser.add_argument(
        "--split",
        type=str,
        default="train",
        choices=["train", "validation"],
        help="Dataset split to stream from (default: 'train')."
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="sentence",
        choices=["passage", "overlap", "sentence"],
        help="Chunking strategy to apply (default: 'sentence')."
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Chunk size in characters (default: 500)."
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=100,
        help="Chunk overlap in characters (default: 100)."
    )
    parser.add_argument(
        "--index-path",
        type=str,
        default=os.path.join("data", "dev.index"),
        help="Path where FAISS index will be saved (default: data/dev.index)."
    )
    parser.add_argument(
        "--meta-path",
        type=str,
        default=os.path.join("data", "dev_metadata.json"),
        help="Path where metadata mapping JSON will be saved (default: data/dev_metadata.json)."
    )
    args = parser.parse_args()

    print("==================================================", flush=True)
    print("HH Goa 2026 - Building Development Index", flush=True)
    print("==================================================\n", flush=True)

    t_start = time.perf_counter()

    # 1. Load data sample
    raw_records = load_dev_sample(sample_size=args.sample_size, split=args.split)
    if not raw_records:
        print("Error: No records loaded from dataset.", flush=True)
        sys.exit(1)

    # 2. Extract passages
    print("\nExtracting passages...", flush=True)
    passages = extract_passages(raw_records)
    print(f"Extracted {len(passages)} individual passages (English + Translations).", flush=True)
    if not passages:
        print("Error: No passages extracted.", flush=True)
        sys.exit(1)

    # 3. Chunk passages
    print(f"\nChunking passages using strategy '{args.strategy}' (size={args.chunk_size}, overlap={args.overlap})...", flush=True)
    chunker = PassageChunker(chunk_size=args.chunk_size, overlap=args.overlap)
    
    all_chunks = []
    for idx, p in enumerate(passages):
        chunks = chunker.chunk(p["text"], p["metadata"], strategy=args.strategy)
        all_chunks.extend(chunks)
        
    print(f"Generated {len(all_chunks)} chunks from {len(passages)} passages.", flush=True)
    if not all_chunks:
        print("Error: No chunks generated.", flush=True)
        sys.exit(1)

    # 4. Generate Embeddings
    print("\nInitializing embedding service...", flush=True)
    t_embed_start = time.perf_counter()
    embedder = EmbeddingService()
    t_embed_init = time.perf_counter() - t_embed_start
    print(f"Model initialization took {t_embed_init:.4f} seconds.", flush=True)

    print("Encoding chunks into vectors (this may take a moment)...", flush=True)
    chunk_texts = [c.text for c in all_chunks]
    chunk_metadatas = [c.metadata for c in all_chunks]
    
    t_encode_start = time.perf_counter()
    embeddings = embedder.encode(chunk_texts)
    t_encode = time.perf_counter() - t_encode_start
    print(f"Encoded {len(embeddings)} vectors in {t_encode:.4f} seconds (Avg: {t_encode/len(embeddings)*1000:.2f} ms/vector).", flush=True)

    # 5. Populate Vector Store & Save
    print("\nIndexing vectors into FAISS...", flush=True)
    t_index_start = time.perf_counter()
    vector_store = VectorStore(dimension=embedder.dimension)
    vector_store.add_chunks(chunk_texts, chunk_metadatas, embeddings)
    t_index = time.perf_counter() - t_index_start
    print(f"FAISS indexing took {t_index:.4f} seconds.", flush=True)

    # 6. Save files
    print("\nSaving files to disk...", flush=True)
    vector_store.save(args.index_path, args.meta_path)
    
    t_total = time.perf_counter() - t_start
    print(f"\nIndex build process finished successfully in {t_total:.4f} seconds.", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    main()
