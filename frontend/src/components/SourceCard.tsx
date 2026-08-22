import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { RagSource } from "@/types/rag";

export function SourceCard({ source }: { source: RagSource }) {
  const [expanded, setExpanded] = useState(false);
  const pct = Math.max(0, Math.min(1, source.score));

  const languageNames: Record<string, string> = {
    "en": "English",
    "urd_Arab": "Urdu",
    "hin_Deva": "Hindi",
    "guj_Gujr": "Gujarati",
    "tam_Taml": "Tamil",
    "tel_Telu": "Telugu",
    "ben_Beng": "Bengali",
    "mar_Deva": "Marathi",
    "pan_Guru": "Punjabi",
    "mal_Mlym": "Malayalam",
    "kan_Knda": "Kannada",
    "ory_Orya": "Odia"
  };
  const languageLabel = languageNames[source.language] ?? source.language;

  // Short preview of 100 characters
  const truncatedText = source.passage.slice(0, 100) + (source.passage.length > 100 ? "..." : "");

  return (
    <article className="rounded-xl border border-[#E5EBEA] bg-[#FFFDF7] p-5 shadow-sm select-none">
      <header className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          {/* Circular ranked badge */}
          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#E5EBEA]/70 font-sans text-xs font-bold text-[#253F40]">
            {source.rank}
          </span>
          <span className="text-xs font-semibold text-[#253F40]">
            {languageLabel}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="font-mono text-xs font-bold text-[#3E9698]">
            {source.score.toFixed(2)}
          </span>
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            className="text-[#253F40]/50 hover:text-[#253F40]"
          >
            {expanded ? (
              <ChevronUp className="h-4 w-4 stroke-[2.2px]" />
            ) : (
              <ChevronDown className="h-4 w-4 stroke-[2.2px]" />
            )}
          </button>
        </div>
      </header>

      <div className="mt-3.5">
        <p className="font-sans text-xs leading-relaxed text-[#253F40]/80">
          {expanded ? source.passage : truncatedText}
        </p>

        {source.passage.length > 100 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-2.5 inline-flex items-center text-[11px] font-bold text-[#3E9698] hover:text-[#3E9698]/80 focus:outline-none"
          >
            {expanded ? "Show less ▲" : "Show more ▼"}
          </button>
        )}
      </div>

      <footer className="mt-4 flex flex-wrap gap-x-3 gap-y-1 border-t border-[#E5EBEA]/40 pt-2.5 font-mono text-[9px] text-[#253F40]/45">
        <span>id: {source.query_id}</span>
        <span>index: {source.passage_index}</span>
      </footer>
    </article>
  );
}