
title: HH Goa 2026 Voice RAG Backend
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
# Voice-Enabled RAG System Backend

This is the backend service for the **HH Goa 2026 Voice-Enabled RAG System** project.

## Project Structure

```text
backend/
├── app/
│   └── inspect_dataset.py  # Dataset exploration script
├── tests/                  # Directory for test cases
├── requirements.txt        # Dependencies list (CPU-focused)
└── README.md               # Backend documentation
```

## Setup Instructions

1. Make sure you are using Python 3.9+.
2. Activate your virtual environment:
   * On Windows (Powershell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Dataset Inspection

To run the dataset inspection script:
```bash
python app/inspect_dataset.py
```
This script dynamically retrieves configurations, splits, schema fields, and displays a single truncated sample record from `ai4bharat/MSMARCO-XI` dataset using Hugging Face datasets streaming mode.

## Phase 3: Chunking & Development Sample

### Core Design Decisions

#### 1. Why a Small Development Sample?
Streaming the dataset with a controlled sample size (e.g. 100 records) allows testing of the data parsing and chunking architecture locally on resource-constrained systems without fetching the massive 50 GB MSMARCO-XI dataset or overloading RAM.

#### 2. Why Passage-Based Chunking (Baseline)?
The dataset passages (`English_passages` and `Translated_passages`) represent semantically distinct chunks selected by search engines or translators. Storing these directly as chunks serves as a baseline to test whether additional split segmentation is necessary.

#### 3. Why Overlapping Chunking?
Overlapping splitters ensure context is preserved across chunk boundaries (especially for longer text segments) so that critical answers aren't bisected. If a passage fits within the target `chunk_size` (e.g., 500 characters), it remains unified to avoid unnecessary fragmentation.

#### 4. Why Sentence/Meaning-Aware Chunking?
Sentence-aware chunking groups whole sentences together without splitting them mid-sentence, maintaining grammatical context for the vector RAG pipeline. It splits on Indic boundaries (like `|` or `؟`) and falls back to character overlapping if sentence bounds are missing.

### Usage

To run the chunker comparison script (running all 3 strategies against a dynamic sample):
```bash
# Runs comparison on train split (size 100)
python app/compare_chunkers.py --sample-size 100

# Runs comparison on validation split (recommended for fast execution)
python app/compare_chunkers.py --sample-size 10 --split validation
```

To run the unit tests:
```bash
python -m unittest tests/test_chunking.py
```

## Phase 4: Embeddings + FAISS Retrieval

### Core Architectural Concepts

#### 1. What is an Embedding?
An embedding is a numerical vector (a list of numbers) representing the semantic meaning of a text segment. By converting chunks and queries into 384-dimensional dense vectors using `sentence-transformers/all-MiniLM-L6-v2`, we represent texts in a vector space where similar meanings sit close together.

#### 2. What is FAISS?
FAISS (Facebook AI Similarity Search) is an open-source library for efficient similarity search of dense vectors. 
- In this phase, we use `faiss.IndexFlatIP` (exhaustive flat Inner Product search).
- Because our vectors are L2-normalized upon encoding, the inner product calculation computes exact Cosine Similarity.
- Flat index is selected for development as it guarantees exact (non-approximate) similarity matches and runs in microseconds for small development pools, avoiding complex indices.

#### 3. What happens during retrieval?
When a query is entered, the following workflow retrieves relevant contexts:
```text
User Question
      ↓
all-MiniLM-L6-v2 (Vectorize & Normalize)
      ↓
Query Vector
      ↓
FAISS Search (Inner Product against Document Index)
      ↓
Top-K Match Indices
      ↓
Metadata Map Lookup (Trace back to source query_id and passage_index)
      ↓
Top-K Chunks with Similarity Scores
```

### Usage

To build the local vector index database (using 15 streamed records on the validation split):
```bash
python app/build_index.py --sample-size 15 --split validation
```
This saves index database files to `data/dev.index` and metadata mapping to `data/dev_metadata.json` (gitignored).

To run the retrieval evaluation, quality check, and latency benchmark:
```bash
python app/test_retrieval.py
```

To run retrieval unit tests:
```bash
python -m unittest tests/test_retrieval_suite.py
```

## Phase 5: LLM + Grounded RAG

### Workflow
```text
User Question
      ↓
FAISS Vector Retrieval
      ↓
Grounded LLM Prompt (forced to answer ONLY from context)
      ↓
Grounded Text Answer
```

### Usage
- Run interactive text session:
  ```bash
  python app/interactive_rag.py
  ```
- Run tests:
  ```bash
  python -m unittest tests/test_rag_pipeline.py
  ```

## Phase 6: RAG Guardrails

### Core Concepts
Guardrails prevent unsupported or unsafe system behaviors.

### Guardrail Flow
```text
Input validation (whitespace/length checks)
      ↓
Retrieval score check (LLM bypass if similarity score < 0.40)
      ↓
Context filtering (deduplication & chunk limiting)
      ↓
Strict grounded prompt
      ↓
Output validation (no leaked secrets or error text signatures)
```
Note: Guardrails reduce hallucination risks but cannot mathematically guarantee zero hallucinations.

### Usage
- Run tests:
  ```bash
  python -m unittest tests/test_guardrails.py
  ```

## Phase 7: Speech-to-Text → Existing RAG

### Core Concepts
- **Speech-to-Text (STT)**: Converts spoken voice recordings into text.
- **Sarvam AI (Saaras v3)**: We utilize the official REST API `POST https://api.sarvam.ai/speech-to-text` with model `saaras:v3` and `mode="transcribe"` for fast, CPU-friendly Indian-accented English/Indic transcriptions.

### Voice RAG Workflow
```text
🎤 Spoken Query
      ↓
Audio Validation (local check: size, format, duration)
      ↓
Sarvam Saaras v3 STT (REST API upload)
      ↓
Query Transcript
      ↓
FAISS Retrieval & RAG Pipeline
      ↓
Guardrails Validation
      ↓
Grounded Response
```

### Setup & Usage
1. Set the API key in your `.env` file:
   ```env
   SARVAM_API_KEY=your_sarvam_subscription_key
   ```
2. To run the voice retriever CLI with a local recording (WAV format, duration <= 30 seconds):
   ```bash
   python app/test_voice_rag.py path/to/recording.wav
   ```
3. To run all voice-related unit tests:
   ```bash
   python -m unittest tests/test_speech_to_text.py
   ```



