# HH Goa 2026 — Voice RAG (frontend)

React + TypeScript + Vite + Tailwind CSS frontend for the existing FastAPI backend.
This is the code that belongs in `hh-goa-2026-voice-rag/frontend/`.

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_BASE_URL
npm run dev
```

## Environment

| Variable | Description |
| --- | --- |
| `VITE_API_BASE_URL` | Base URL of the FastAPI backend, no trailing slash |

No localhost URL is hardcoded anywhere in the app code.

## Backend endpoints used

- `GET /health` — status badge in the header; drives Demo Mode
- `POST /query` — JSON `{ query }` for the text fallback
- `POST /voice` — multipart audio upload from the microphone

Expected response: transcript, language_code, answer, sources[] (rank, score, language,
passage, query_id, passage_index), retrieval_latency_ms, stt_latency_ms, rag_latency_ms,
total_latency_ms.

## Structure

```
src/
├── components/   VoiceButton, QuestionForm, ResultsPanel, SourceCard, PerformancePanel, SiteHeader
├── services/     api.ts (health/query/voice + response normalisation), demo.ts
├── hooks/        useVoiceRag.ts (recording, state machine, backend health)
├── types/        rag.ts
└── routes/       index.tsx (the page)
```

## Guardrails

- Answers render exactly as returned by the backend; nothing is invented client-side.
- When the backend returns no answer or no sources, the UI shows
  "I don't have enough information in the provided context to answer that."
- A green "Grounded" badge appears only when supporting sources exist.
- "Demo Mode" is labelled explicitly whenever the backend is unreachable; sample data is
  never presented as real backend output.

## Errors handled

Microphone permission denied, unsupported browser, empty recording, backend unavailable,
non-2xx responses from STT / retrieval / LLM stages, and insufficient context.
