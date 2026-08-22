import unittest
from backend.app.chunker import PassageChunker, Chunk

class TestChunking(unittest.TestCase):
    def setUp(self):
        # Initialize chunker with 100 character chunk size and 20 character overlap for easy testing
        self.chunk_size = 100
        self.overlap = 20
        self.chunker = PassageChunker(chunk_size=self.chunk_size, overlap=self.overlap)
        self.dummy_metadata = {
            "query_id": 12345,
            "passage_index": 2,
            "language": "en"
        }

    def test_short_passage(self):
        """
        Test 1: Short passage.
        A passage shorter than or equal to chunk_size should yield exactly one chunk.
        """
        short_text = "This is a very short passage."
        
        # Test passage strategy
        chunks_p = self.chunker.chunk(short_text, self.dummy_metadata, strategy="passage")
        self.assertEqual(len(chunks_p), 1)
        self.assertEqual(chunks_p[0].text, short_text)
        
        # Test overlap strategy
        chunks_o = self.chunker.chunk(short_text, self.dummy_metadata, strategy="overlap")
        self.assertEqual(len(chunks_o), 1)
        self.assertEqual(chunks_o[0].text, short_text)
        
        # Test sentence strategy
        chunks_s = self.chunker.chunk(short_text, self.dummy_metadata, strategy="sentence")
        self.assertEqual(len(chunks_s), 1)
        self.assertEqual(chunks_s[0].text, short_text)

    def test_long_passage(self):
        """
        Test 2: Long passage.
        A passage longer than chunk_size should split into multiple chunks under overlap/sentence.
        """
        long_text = (
            "This is sentence one that is quite long indeed. "
            "This is sentence two that is also long and detailed. "
            "This is sentence three, adding more length to exceed the limit."
        )
        # Verify text length is indeed greater than 100 characters
        self.assertTrue(len(long_text) > self.chunk_size)
        
        # Test overlap strategy
        chunks_o = self.chunker.chunk(long_text, self.dummy_metadata, strategy="overlap")
        self.assertGreater(len(chunks_o), 1)
        
        # Test sentence strategy
        chunks_s = self.chunker.chunk(long_text, self.dummy_metadata, strategy="sentence")
        self.assertGreater(len(chunks_s), 1)

    def test_overlap_verification(self):
        """
        Test 3: Overlap.
        Verify that adjacent chunks actually overlap when the passage requires splitting.
        """
        long_text = (
            "abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz"
            "1234567890abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnop"
        )
        self.assertTrue(len(long_text) > self.chunk_size)
        
        # Stride is 100 - 20 = 80 characters
        chunks_o = self.chunker.chunk(long_text, self.dummy_metadata, strategy="overlap")
        self.assertGreater(len(chunks_o), 1)
        
        # Verify overlap between chunk 0 and chunk 1
        chunk0_text = chunks_o[0].text
        chunk1_text = chunks_o[1].text
        
        # The stride is 80, so chunk 1 starts at index 80 of long_text
        # Chunk 0 ends at index 100 of long_text
        # The overlapping part should be characters from index 80 to 100 of long_text
        expected_overlap_part = long_text[80:100]
        
        # Check that chunk 0 ends with the overlapping part
        self.assertTrue(chunk0_text.endswith(expected_overlap_part))
        # Check that chunk 1 starts with the overlapping part
        self.assertTrue(chunk1_text.startswith(expected_overlap_part))
        # Verify its length is exactly overlap size
        self.assertEqual(len(expected_overlap_part), self.overlap)

    def test_metadata_preservation(self):
        """
        Test 4: Metadata.
        Verify that query_id, passage_index, and language are preserved in chunk metadata.
        """
        text = "This is a passage to verify metadata trace capabilities."
        
        for strategy in ["passage", "overlap", "sentence"]:
            chunks = self.chunker.chunk(text, self.dummy_metadata, strategy=strategy)
            self.assertGreater(len(chunks), 0)
            for c in chunks:
                self.assertEqual(c.metadata.get("query_id"), 12345)
                self.assertEqual(c.metadata.get("passage_index"), 2)
                self.assertEqual(c.metadata.get("language"), "en")
                self.assertEqual(c.metadata.get("chunk_strategy"), strategy)
                self.assertIn("chunk_index", c.metadata)

    def test_empty_invalid_text(self):
        """
        Test 5: Empty/invalid text.
        The system should handle it safely without crashing, returning empty lists.
        """
        invalid_inputs = [None, "", "   ", "\n\n"]
        
        for inp in invalid_inputs:
            for strategy in ["passage", "overlap", "sentence"]:
                chunks = self.chunker.chunk(inp, self.dummy_metadata, strategy=strategy)
                self.assertEqual(chunks, [])

if __name__ == "__main__":
    unittest.main()
