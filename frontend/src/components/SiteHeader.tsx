import { AudioLines, RefreshCw, Wifi, WifiOff } from "lucide-react";
import type { BackendStatus } from "@/hooks/useVoiceRag";

export function SiteHeader({
  backend,
  onRefresh,
}: {
  backend: BackendStatus;
  onRefresh: () => void;
}) {
  return (
    <header className="border-b border-border/60">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-4 px-6 py-5">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[image:var(--gradient-accent)] text-primary-foreground">
            <AudioLines className="h-5 w-5" />
          </span>
          <div className="leading-tight">
            <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-muted-foreground">
              HH Goa 2026
            </p>
            <p className="font-display text-lg font-bold text-gradient">VOICE RAG</p>
          </div>
        </div>

        <p className="hidden text-sm text-muted-foreground md:block">
          Grounded AI over MSMARCO-XI
        </p>

        <button
          type="button"
          onClick={onRefresh}
          className="ml-auto inline-flex items-center gap-2 rounded-full border border-border bg-card/60 px-3 py-1.5 font-mono text-[11px] uppercase tracking-wider text-muted-foreground transition-colors hover:text-foreground"
        >
          {backend === "online" ? (
            <Wifi className="h-3.5 w-3.5 text-success" />
          ) : backend === "checking" ? (
            <RefreshCw className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <WifiOff className="h-3.5 w-3.5 text-warning" />
          )}
          {backend === "online" ? "Backend online" : backend === "checking" ? "Checking" : "Demo mode"}
        </button>
      </div>
    </header>
  );
}