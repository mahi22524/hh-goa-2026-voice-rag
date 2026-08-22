import type { RagResponse, RagSource } from "@/types/rag";
import { INSUFFICIENT_CONTEXT_MESSAGE } from "@/types/rag";

export const API_BASE_URL = (
  (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ?? ""
).replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    public stage: "health" | "stt" | "retrieval" | "llm" | "network" = "network",
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function url(path: string) {
  if (!API_BASE_URL) throw new ApiError("Backend URL is not configured (VITE_API_BASE_URL).");
  return `${API_BASE_URL}${path}`;
}

function num(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function normalizeSources(raw: unknown): RagSource[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item, i) => {
    const s = (item ?? {}) as Record<string, unknown>;
    const meta = (s["metadata"] ?? {}) as Record<string, unknown>;
    return {
      rank: num(s["rank"]) || i + 1,
      score: num(s["score"] ?? s["similarity"] ?? s["similarity_score"]),
      language: String(s["language"] ?? meta["language"] ?? s["language_code"] ?? "unknown"),
      passage: String(s["passage"] ?? s["text"] ?? s["passage_text"] ?? ""),
      query_id: String(s["query_id"] ?? meta["query_id"] ?? "—"),
      passage_index: num(s["passage_index"] ?? meta["passage_index"]),
    };
  });
}

export function normalizeResponse(raw: unknown, fallbackTranscript = ""): RagResponse {
  const r = (raw ?? {}) as Record<string, unknown>;
  const sources = normalizeSources(r["sources"]);
  const answer = String(r["answer"] ?? "").trim();
  const explicitGrounded = r["grounded"];
  const insufficient =
    !answer ||
    answer.toLowerCase().includes("don't have enough information") ||
    sources.length === 0;

  return {
    transcript: String(r["transcript"] ?? fallbackTranscript),
    language_code: String(r["language_code"] ?? "unknown"),
    answer: insufficient ? INSUFFICIENT_CONTEXT_MESSAGE : answer,
    grounded:
      typeof explicitGrounded === "boolean" ? explicitGrounded && !insufficient : !insufficient,
    sources,
    retrieval_latency_ms: num(r["retrieval_latency_ms"]),
    stt_latency_ms: num(r["stt_latency_ms"]),
    rag_latency_ms: num(r["rag_latency_ms"] ?? r["llm_latency_ms"]),
    total_latency_ms: num(r["total_latency_ms"]),
    status: String(r["status"] ?? ""),
  };
}

async function parse(response: Response, stage: ApiError["stage"]) {
  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new ApiError(`Backend responded ${response.status}. ${body.slice(0, 200)}`, stage);
  }
  return response.json();
}

export async function checkHealth(signal?: AbortSignal): Promise<boolean> {
  try {
    const res = await fetch(url("/health"), signal ? { signal } : {});
    return res.ok;
  } catch {
    return false;
  }
}

export async function postQuery(question: string, languageCode?: string): Promise<RagResponse> {
  let res: Response;
  try {
    res = await fetch(url("/query"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: question, question, language_code: languageCode }),
    });
  } catch {
    throw new ApiError("Backend unavailable. Check that the FastAPI server is running.");
  }
  return normalizeResponse(await parse(res, "retrieval"), question);
}

export async function postVoice(audio: Blob, languageCode?: string): Promise<RagResponse> {
  const form = new FormData();
  form.append("file", audio, "recording.webm");
  form.append("audio", audio, "recording.webm");
  if (languageCode) {
    form.append("language_code", languageCode);
  }
  let res: Response;
  try {
    res = await fetch(url("/voice"), { method: "POST", body: form });
  } catch {
    throw new ApiError("Backend unavailable. Check that the FastAPI server is running.");
  }
  return normalizeResponse(await parse(res, "stt"));
}