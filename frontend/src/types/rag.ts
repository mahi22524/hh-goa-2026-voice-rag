export type VoiceState = "idle" | "recording" | "processing" | "completed" | "error";

export interface RagSource {
  rank: number;
  score: number;
  language: string;
  passage: string;
  query_id: string;
  passage_index: number;
}

export interface RagResponse {
  transcript: string;
  language_code: string;
  answer: string;
  grounded: boolean;
  sources: RagSource[];
  retrieval_latency_ms: number;
  stt_latency_ms: number;
  rag_latency_ms: number;
  total_latency_ms: number;
  status: string;
  demo?: boolean;
}

export const INSUFFICIENT_CONTEXT_MESSAGE =
  "I don't have enough information in the provided context to answer that.";