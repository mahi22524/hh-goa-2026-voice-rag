# Voice RAG Frontend

Build the frontend for my EXISTING GitHub repository:

https://github.com/mahi22524/hh-goa-2026-voice-rag

IMPORTANT:

This is an EXISTING project.

Do NOT create a new GitHub repository.

Do NOT create a separate project repository.

The frontend must be created inside the existing repository under:

frontend/

The existing backend is already implemented under:

backend/

DO NOT modify, delete, overwrite, or recreate the existing backend.

==================================================

PROJECT

==================================================

HH Goa 2026 — Voice-Enabled RAG System

Theme:

"World's largest AI x Crypto Hacker House"

Build only the frontend.

==================================================

GITHUB / CODE REQUIREMENT

==================================================

The final frontend code MUST be exportable/importable into the existing GitHub repository:

mahi22524/hh-goa-2026-voice-rag

Target location:

hh-goa-2026-voice-rag/

└── frontend/

Before making changes, respect the existing repository structure.

Do not put frontend files in the repository root.

Do not replace README.md.

Do not modify backend files.

If Lovable GitHub integration is available, connect to the EXISTING repository:

mahi22524/hh-goa-2026-voice-rag

and work on the main branch or the appropriate existing branch.

If direct GitHub synchronization is not available, provide/export the complete frontend source code so it can be copied into:

frontend/

and committed to the existing repository manually.

==================================================

FRONTEND TECHNOLOGY

==================================================

Use:

- React

- TypeScript

- Vite

- Tailwind CSS

- modern responsive components

Create:

frontend/

├── package.json

├── vite.config.*

├── index.html

├── src/

│   ├── components/

│   ├── services/

│   ├── hooks/

│   ├── types/

│   ├── App.tsx

│   └── main.tsx

└── README.md

==================================================

UI

==================================================

Create a polished hackathon-quality interface.

Header:

HH GOA 2026

VOICE RAG

Subtitle:

"Grounded AI over MSMARCO-XI"

Hero:

"Ask. Retrieve. Verify."

Description:

"Ask questions using your voice and get answers grounded in the provided knowledge base."

VOICE:

Large microphone button.

States:

- Idle

- Recording

- Processing

- Completed

- Error

Show:

"Tap to speak"

Also provide text input as a fallback.

==================================================

RESULTS

==================================================

After a question is submitted, display:

1. Transcript

2. Retrieved Sources

Each source should display:

- rank

- similarity score

- language

- passage text

- query_id

- passage_index

3. Grounded Answer

4. Performance

Display:

- STT latency

- Retrieval latency

- LLM latency

- Total latency

==================================================

GUARDRAIL UI

==================================================

Show:

"Grounded"

when sufficient context exists.

If the backend returns insufficient context, display:

"I don't have enough information in the provided context to answer that."

Never invent an answer in the frontend.

==================================================

BACKEND CONNECTION

==================================================

Prepare the frontend to connect to the existing FastAPI backend.

Use:

VITE_API_BASE_URL

Do NOT hardcode localhost throughout the application.

Prepare these API calls:

GET /health

POST /query

POST /voice

Voice response:

{

  transcript,

  language_code,

  answer,

  sources,

  retrieval_latency_ms,

  stt_latency_ms,

  rag_latency_ms,

  total_latency_ms

}

==================================================

DEMO MODE

==================================================

If the backend is unavailable, provide a clearly labelled:

"Demo Mode"

so the UI can still be previewed.

Do NOT pretend demo data is real backend data.

==================================================

ERROR HANDLING

==================================================

Handle:

- microphone permission denied

- STT failure

- backend unavailable

- retrieval failure

- LLM failure

- insufficient context

==================================================

IMPORTANT

==================================================

Do NOT:

- create another backend

- create another GitHub repository

- modify backend/

- delete existing files

- replace the root README.md

- add authentication

- add payments

- add unnecessary databases

- add unrelated features

The final result must be a frontend that can live inside:

mahi22524/hh-goa-2026-voice-rag/frontend/

==================================================

FINAL STEP

==================================================

After building the frontend:

1. Verify the frontend builds successfully.

2. Show the files created.

3. Confirm the frontend is located under frontend/.

4. Confirm the existing backend was not modified.

5. If GitHub integration is available, sync/import the code into the EXISTING repository:

   mahi22524/hh-goa-2026-voice-rag

6. If automatic GitHub sync is unavailable, give exact instructions for importing the generated code into the existing repository.

7. Do NOT create a new repository.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/58d93c6a-1262-40d4-8c99-870bc2c60576).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
