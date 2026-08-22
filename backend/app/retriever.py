import os
import sys

# Ensure backend/app is in Python path for relative imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

from embedder import EmbeddingService
from vector_store import VectorStore

class Retriever:
    def __init__(self, index_path: str = os.path.join("data", "dev.index"), meta_path: str = os.path.join("data", "dev_metadata.json")):
        """
        Initializes the retriever by loading the local index and metadata mapping,
        and initializing the embedding service.
        """
        self.index_path = index_path
        self.meta_path = meta_path
        
        # Load embedding service (singleton)
        self.embedder = EmbeddingService()
        
        # Load vector store
        print(f"Loading retriever index from '{self.index_path}'...", flush=True)
        self.vector_store = VectorStore(dimension=self.embedder.dimension)
        self.vector_store.load(self.index_path, self.meta_path)

    def retrieve(self, query: str, top_k: int = 3, language_code: str = None):
        """
        Main retrieval pipeline:
        1. Embed runtime query
        2. Normalize query vector (for cosine similarity)
        3. Search FAISS flat Inner Product index
        4. Match chunk language to query language if mapping exists
        5. Return top_k matching chunks with rank, score, text, and metadata
        """
        if not query or not query.strip():
            return []
            
        # 1. Embed query (normalize_embeddings=True inside embedder generates normalized unit vector)
        query_vector = self.embedder.encode([query])
        
        # 2. Search FAISS index
        raw_results = self.vector_store.search(query_vector, top_k=top_k)
        
        # 3. Map detected language to target dataset language code
        target_lang = "en"
        if language_code:
            code = language_code.lower().split("-")[0]
            mapping = {
                "ta": "tam_Taml",
                "hi": "hin_Deva",
                "gu": "guj_Gujr",
                "te": "tel_Telu",
                "ur": "urd_Arab",
                "bn": "ben_Beng",
                "mr": "mar_Deva",
                "pa": "pan_Guru",
                "ml": "mal_Mlym",
                "kn": "kan_Knda",
                "or": "ory_Orya",
                "en": "en"
            }
            target_lang = mapping.get(code, "en")
        
        # 4. Format output and resolve matching language translation
        results = []
        for rank, score, text, metadata in raw_results:
            q_id = metadata.get("query_id")
            p_idx = metadata.get("passage_index")
            current_lang = metadata.get("language")
            
            if language_code and q_id is not None and p_idx is not None and current_lang != target_lang:
                found_match = False
                for pos_idx, meta in self.vector_store.metadata_map.items():
                    if (meta.get("query_id") == q_id and 
                        meta.get("passage_index") == p_idx and 
                        meta.get("language") == target_lang):
                        text = self.vector_store.texts_map.get(pos_idx, text)
                        metadata = meta
                        found_match = True
                        break
                
                if not found_match and target_lang != "en" and current_lang != "en":
                    for pos_idx, meta in self.vector_store.metadata_map.items():
                        if (meta.get("query_id") == q_id and 
                            meta.get("passage_index") == p_idx and 
                            meta.get("language") == "en"):
                            text = self.vector_store.texts_map.get(pos_idx, text)
                            metadata = meta
                            break
                            
            results.append({
                "rank": rank,
                "score": score,
                "text": text,
                "metadata": metadata
            })
            
        return results
