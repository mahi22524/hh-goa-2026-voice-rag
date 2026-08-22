import { AlertTriangle, Check, Loader2, Mic, Square } from "lucide-react";
import { useEffect, useState } from "react";
import type { VoiceState } from "@/types/rag";
import { cn } from "@/lib/utils";

const LABELS: Record<VoiceState, string> = {
  idle: "Tap to speak",
  recording: "Recording… tap to stop",
  processing: "Processing your question",
  completed: "Tap to speak",
  error: "Tap to try again",
};

export function VoiceButton({
  state,
  onToggle,
}: {
  state: VoiceState;
  onToggle: () => void;
}) {
  const busy = state === "processing";
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    if (state !== "recording") {
      setSeconds(0);
      return;
    }
    const interval = setInterval(() => {
      setSeconds((s) => s + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [state]);

  const formatTime = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="flex flex-col items-center gap-5 py-2 select-none">
      <div className="flex items-center gap-7 md:gap-9">
        {/* Left Equalizer Lines: heights 10px, 20px, 32px, 18px, 8px */}
        <div className="flex items-center gap-[6px] h-12 w-20 justify-end">
          {state === "recording" ? (
            <>
              <span className="w-[3px] rounded-full bg-[#3E9698] animate-[pulse_0.8s_infinite_alternate]" style={{ height: "30%" }} />
              <span className="w-[3px] rounded-full bg-[#3E9698] animate-[pulse_1s_infinite_alternate_0.1s]" style={{ height: "60%" }} />
              <span className="w-[3px] rounded-full bg-[#3E9698] animate-[pulse_1.2s_infinite_alternate_0.2s]" style={{ height: "100%" }} />
              <span className="w-[3px] rounded-full bg-[#3E9698] animate-[pulse_0.9s_infinite_alternate_0.1s]" style={{ height: "55%" }} />
              <span className="w-[3px] rounded-full bg-[#3E9698] animate-[pulse_1.1s_infinite_alternate_0.3s]" style={{ height: "25%" }} />
            </>
          ) : (
            <>
              <span className="w-[3px] h-[8px] rounded-full bg-[#3E9698]/40" />
              <span className="w-[3px] h-[16px] rounded-full bg-[#3E9698]/45" />
              <span className="w-[3px] h-[28px] rounded-full bg-[#3E9698]/50" />
              <span className="w-[3px] h-[18px] rounded-full bg-[#3E9698]/45" />
              <span className="w-[3px] h-[6px] rounded-full bg-[#3E9698]/40" />
            </>
          )}
        </div>

        {/* Central rings structure */}
        <div className="relative flex h-48 w-48 items-center justify-center">
          {/* Outer soft cream circle: diameter ~180px (w-44 h-44) */}
          <div className="flex h-44 w-44 items-center justify-center rounded-full bg-[#F8F3E8] border border-[#E5EBEA] p-3 shadow-sm relative">

            {/* Middle thin teal border ring */}
            <div className={cn(
              "flex h-full w-full items-center justify-center rounded-full border transition-all duration-300 p-2.5",
              state === "recording" ? "border-[#3E9698] animate-pulse" : "border-[#3E9698]/30"
            )}>

              {/* Inner white/cream circle */}
              <button
                type="button"
                onClick={onToggle}
                disabled={busy}
                aria-label={LABELS[state]}
                className={cn(
                  "relative flex h-full w-full items-center justify-center rounded-full transition-all duration-200 shadow-md",
                  busy ? "cursor-wait bg-[#F8F3E8] text-[#253F40]/50" : "bg-[#FFFDF7] text-[#3E9698] hover:bg-[#FFFDF7]/85 active:scale-95 border border-[#E5EBEA]"
                )}
              >
                {state === "recording" ? (
                  <Square className="h-8.5 w-8.5 fill-current text-[#3E9698]" />
                ) : busy ? (
                  <Loader2 className="h-8.5 w-8.5 animate-spin" />
                ) : state === "error" ? (
                  <AlertTriangle className="h-8.5 w-8.5 text-accent animate-bounce" />
                ) : state === "completed" ? (
                  <Check className="h-8.5 w-8.5 text-[#3E9698]" />
                ) : (
                  <Mic className="h-8.5 w-8.5" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Equalizer Lines */}
        <div className="flex items-center gap-[6px] h-12 w-20 justify-start">
          {state === "recording" ? (
            <>
              <span className="w-[3px] rounded-full bg-[#3E9698] animate-[pulse_1.1s_infinite_alternate_0.3s]" style={{ height: "25%" }} />
              <span className="w-[3px] rounded-full bg-[#3E9698] animate-[pulse_0.9s_infinite_alternate_0.1s]" style={{ height: "55%" }} />
              <span className="w-[3px] rounded-full bg-[#3E9698] animate-[pulse_1.2s_infinite_alternate_0.2s]" style={{ height: "100%" }} />
              <span className="w-[3px] rounded-full bg-[#3E9698] animate-[pulse_1s_infinite_alternate_0.1s]" style={{ height: "60%" }} />
              <span className="w-[3px] rounded-full bg-[#3E9698] animate-[pulse_0.8s_infinite_alternate]" style={{ height: "30%" }} />
            </>
          ) : (
            <>
              <span className="w-[3px] h-[6px] rounded-full bg-[#3E9698]/40" />
              <span className="w-[3px] h-[18px] rounded-full bg-[#3E9698]/45" />
              <span className="w-[3px] h-[28px] rounded-full bg-[#3E9698]/50" />
              <span className="w-[3px] h-[16px] rounded-full bg-[#3E9698]/45" />
              <span className="w-[3px] h-[8px] rounded-full bg-[#3E9698]/40" />
            </>
          )}
        </div>
      </div>

      <div className="text-center mt-[-6px]">
        {state === "recording" && (
          <div className="mb-0.5 text-xs font-mono font-bold text-[#E58B42]">
            {formatTime(seconds)}
          </div>
        )}
        <p className="font-sans text-xs font-semibold text-[#3E9698]">
          {LABELS[state]}
        </p>
      </div>
    </div>
  );
}