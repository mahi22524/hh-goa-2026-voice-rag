import type { RagResponse } from "@/types/rag";
import { INSUFFICIENT_CONTEXT_MESSAGE } from "@/types/rag";

const KB: { match: string[]; answer: string; sources: RagResponse["sources"] }[] = [
  {
    match: ["retrieval", "rag", "how", "work", "grounded"],
    answer:
      "Retrieval-augmented generation first embeds the question, searches the MSMARCO-XI passage index for the nearest passages, and then asks the language model to answer using only those passages as context.",
    sources: [
      {
        rank: 1,
        score: 0.8421,
        language: "en",
        passage:
          "Retrieval-augmented generation combines a dense retriever over a passage corpus with a generative model, so that answers are conditioned on retrieved evidence rather than parametric memory alone.",
        query_id: "demo-1042",
        passage_index: 17,
      },
      {
        rank: 2,
        score: 0.7734,
        language: "en",
        passage:
          "MS MARCO is a large-scale collection of real search queries paired with human-relevant passages, widely used to benchmark passage ranking and open-domain question answering systems.",
        query_id: "demo-1042",
        passage_index: 88,
      },
      {
        rank: 3,
        score: 0.6519,
        language: "es",
        passage:
          "La recuperación multilingüe permite que una consulta en un idioma recupere pasajes relevantes escritos en otro idioma mediante embeddings compartidos.",
        query_id: "demo-1042",
        passage_index: 205,
      },
    ],
  },
  {
    match: ["msmarco", "dataset", "corpus", "index", "xi"],
    answer:
      "MSMARCO-XI is the multilingual passage index used here: each entry keeps a query_id, a passage_index and a language tag, which is why every retrieved source can be traced back to an exact position in the corpus.",
    sources: [
      {
        rank: 1,
        score: 0.9012,
        language: "en",
        passage:
          "Each record in the index stores the originating query identifier, the passage offset within that query's candidate list, and the detected language of the passage text.",
        query_id: "demo-2210",
        passage_index: 3,
      },
      {
        rank: 2,
        score: 0.7108,
        language: "hi",
        passage:
          "बहुभाषी अनुक्रमणिका में प्रत्येक अंश की भाषा टैग की जाती है ताकि उत्तर देते समय स्रोत की भाषा स्पष्ट रहे।",
        query_id: "demo-2210",
        passage_index: 41,
      },
    ],
  },
];

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function demoAnswer(question: string, spokeAloud = false): Promise<RagResponse> {
  await delay(900);
  const q = question.toLowerCase();
  const hit = KB.find((entry) => entry.match.some((token) => q.includes(token)));
  const stt = spokeAloud ? 412 : 0;
  const retrieval = 128;
  const llm = 640;

  return {
    transcript: question,
    language_code: "en",
    answer: hit ? hit.answer : INSUFFICIENT_CONTEXT_MESSAGE,
    grounded: Boolean(hit),
    sources: hit ? hit.sources : [],
    stt_latency_ms: stt,
    retrieval_latency_ms: retrieval,
    rag_latency_ms: llm,
    total_latency_ms: stt + retrieval + llm,
    demo: true,
  };
}