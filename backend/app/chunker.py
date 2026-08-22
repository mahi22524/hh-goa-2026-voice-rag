import re
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Chunk:
    text: str
    metadata: Dict[str, Any]

class PassageChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        """
        Initializes the chunker with target chunk size and overlap (in characters).
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        # Ensure stride is at least 1 to prevent infinite loops
        self.stride = max(1, self.chunk_size - self.overlap)

    def chunk(self, text: str, metadata: Dict[str, Any], strategy: str = "passage") -> List[Chunk]:
        """
        Main entry point for chunking a single passage.
        """
        if not text or not text.strip():
            return []
            
        text = text.strip()
        
        if strategy == "passage":
            return self._chunk_passage_baseline(text, metadata)
        elif strategy == "overlap":
            return self._chunk_overlap(text, metadata)
        elif strategy == "sentence":
            return self._chunk_sentence_aware(text, metadata)
        else:
            return self._chunk_passage_baseline(text, metadata)

    def _chunk_passage_baseline(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Strategy A: Baseline strategy where each passage becomes one chunk.
        """
        meta = metadata.copy()
        meta["chunk_strategy"] = "passage"
        meta["chunk_index"] = 0
        meta["total_chunks"] = 1
        return [Chunk(text=text, metadata=meta)]

    def _chunk_overlap(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Strategy B: Overlapping character chunker.
        """
        if len(text) <= self.chunk_size:
            meta = metadata.copy()
            meta["chunk_strategy"] = "overlap"
            meta["chunk_index"] = 0
            meta["total_chunks"] = 1
            return [Chunk(text=text, metadata=meta)]
            
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append(chunk_text)
                
            if end >= len(text):
                break
                
            start += self.stride
            
        result = []
        for idx, chunk_text in enumerate(chunks):
            meta = metadata.copy()
            meta["chunk_strategy"] = "overlap"
            meta["chunk_index"] = idx
            meta["total_chunks"] = len(chunks)
            meta["chunk_start_char"] = idx * self.stride
            meta["chunk_end_char"] = idx * self.stride + len(chunk_text)
            result.append(Chunk(text=chunk_text, metadata=meta))
            
        return result

    def _chunk_sentence_aware(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Strategy C: Sentence-aware chunker. Splits text by sentence boundaries
        and groups sentences into chunks that do not exceed chunk_size.
        """
        sentence_ends = r'(?<=[.!?|؟])\s+'
        sentences = re.split(sentence_ends, text)
        
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            # If no sentences could be parsed, fallback to overlap chunking with strategy labeled as 'sentence'
            overlap_chunks = self._chunk_overlap(text, metadata)
            for c in overlap_chunks:
                c.metadata["chunk_strategy"] = "sentence"
            return overlap_chunks
            
        if len(sentences) == 1 and len(sentences[0]) > self.chunk_size:
            # Fallback for single long sentence
            overlap_chunks = self._chunk_overlap(text, metadata)
            for c in overlap_chunks:
                c.metadata["chunk_strategy"] = "sentence"
            return overlap_chunks
            
        chunks = []
        current_chunk_sentences = []
        current_chunk_len = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            if sentence_len > self.chunk_size:
                if current_chunk_sentences:
                    chunks.append(" ".join(current_chunk_sentences))
                    current_chunk_sentences = []
                    current_chunk_len = 0
                
                # Split this long sentence using overlap chunking
                sentence_sub_chunks = self._chunk_overlap(sentence, metadata)
                for sc in sentence_sub_chunks:
                    chunks.append(sc.text)
                continue
                
            if current_chunk_len + len(sentence) + (1 if current_chunk_sentences else 0) > self.chunk_size:
                if current_chunk_sentences:
                    chunks.append(" ".join(current_chunk_sentences))
                current_chunk_sentences = [sentence]
                current_chunk_len = sentence_len
            else:
                if current_chunk_sentences:
                    current_chunk_len += 1
                current_chunk_sentences.append(sentence)
                current_chunk_len += sentence_len
                
        if current_chunk_sentences:
            chunks.append(" ".join(current_chunk_sentences))
            
        if not chunks:
            overlap_chunks = self._chunk_overlap(text, metadata)
            for c in overlap_chunks:
                c.metadata["chunk_strategy"] = "sentence"
            return overlap_chunks
            
        result = []
        for idx, chunk_text in enumerate(chunks):
            meta = metadata.copy()
            meta["chunk_strategy"] = "sentence"
            meta["chunk_index"] = idx
            meta["total_chunks"] = len(chunks)
            result.append(Chunk(text=chunk_text, metadata=meta))
            
        return result
