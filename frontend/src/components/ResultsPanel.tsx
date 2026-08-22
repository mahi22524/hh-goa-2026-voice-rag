import { BadgeCheck, ShieldAlert } from "lucide-react";
import { PerformancePanel } from "@/components/PerformancePanel";
import { SourceCard } from "@/components/SourceCard";
import type { RagResponse } from "@/types/rag";

function SectionTitle({ index, children }: { index: number; children: string }) {
  return (
    <h2 className="flex items-center gap-3 text-sm font-semibold uppercase tracking-[0.2em] text-muted-foreground">
      <span className="font-mono text-primary">{String(index).padStart(2, "0")}</span>
      {children}
    </h2>
  );
}

export function ResultsPanel({ result }: { result: RagResponse }) {
  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <SectionTitle index={1}>Transcript</SectionTitle>
        <div className="panel p-5">
          <p className="text-lg leading-relaxed text-foreground">
            {result.transcript || "—"}
          </p>
          <p className="mt-2 font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
            language: {result.language_code}
          </p>
        </div>
      </section>

      <section className="space-y-3">
        <SectionTitle index={2}>Retrieved sources</SectionTitle>
        {result.sources.length === 0 ? (
          <div className="panel p-5 text-sm text-muted-foreground">
            No passages passed the retrieval threshold for this question.
          </div>
        ) : (
          <div className="grid gap-3">
            {result.sources.map((source) => (
              <SourceCard key={`${source.query_id}-${source.passage_index}-${source.rank}`} source={source} />
            ))}
          </div>
        )}
      </section>

      <section className="space-y-3">
        <SectionTitle index={3}>Grounded answer</SectionTitle>
        <div className="panel p-5">
          <span
            className={
              result.grounded
                ? "inline-flex items-center gap-2 rounded-full bg-success/15 px-3 py-1 font-mono text-[11px] uppercase tracking-wider text-success"
                : "inline-flex items-center gap-2 rounded-full bg-warning/15 px-3 py-1 font-mono text-[11px] uppercase tracking-wider text-warning"
            }
          >
            {result.grounded ? (
              <BadgeCheck className="h-3.5 w-3.5" />
            ) : (
              <ShieldAlert className="h-3.5 w-3.5" />
            )}
            {result.grounded ? "Grounded" : "Insufficient context"}
          </span>
          <p className="mt-4 text-base leading-relaxed text-foreground">{result.answer}</p>
        </div>
      </section>

      <section className="space-y-3">
        <SectionTitle index={4}>Performance</SectionTitle>
        <PerformancePanel result={result} />
      </section>
    </div>
  );
}