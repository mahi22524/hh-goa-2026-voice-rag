import { createFileRoute } from "@tanstack/react-router";
import { Check, AlertCircle, AlertTriangle, HelpCircle, BookOpen, Clock, Star, Heart, ArrowRight, ShieldCheck, Globe, Wifi } from "lucide-react";
import { useState, useEffect } from "react";
import { QuestionForm } from "@/components/QuestionForm";
import { SourceCard } from "@/components/SourceCard";
import { PerformancePanel } from "@/components/PerformancePanel";
import { VoiceButton } from "@/components/VoiceButton";
import { Sidebar } from "@/components/Sidebar";
import { useVoiceRag } from "@/hooks/useVoiceRag";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/services/api";

const TITLE = "HH Goa 2026 Voice RAG — Grounded AI over MSMARCO-XI";
const DESCRIPTION =
  "Ask questions with your voice and get answers grounded in the MSMARCO-XI knowledge base, with retrieved sources and latency breakdowns.";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: TITLE },
      { name: "description", content: DESCRIPTION },
      { property: "og:title", content: TITLE },
      { property: "og:description", content: DESCRIPTION },
    ],
  }),
  component: Index,
});

function Index() {
  const {
    state,
    error,
    result,
    backend,
    demoMode,
    askText,
    toggleRecording,
    refreshHealth,
    selectedLanguage,
    setSelectedLanguage,
  } = useVoiceRag();

  const [activeTab, setActiveTab] = useState("Home");
  const busy = state === "processing" || state === "recording";

  const [benchmark, setBenchmark] = useState<{
    p50_ms: number;
    p70_ms: number;
    p100_ms: number;
    target_ms: number;
    status: string;
  } | null>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/performance`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.benchmark) {
          setBenchmark(data.benchmark);
        }
      })
      .catch((err) => {
        console.error("Failed to load performance benchmark stats:", err);
      });
  }, []);

  const handleTextSubmit = (question: string) => {
    void askText(question);
  };

  return (
    <div className="flex min-h-screen bg-transparent text-[#253F40] antialiased">
      {/* Left Sidebar */}
      <Sidebar activeTab={activeTab} onChangeTab={setActiveTab} />

      {/* Main Area Container */}
      <div className="flex-1 md:pl-[220px] flex flex-col min-h-screen min-w-0">

        {/* Sticky Top Navigation header */}
        <header className="px-6 py-4 border-b border-[#E5EBEA] bg-[#FFFDF7]/60 backdrop-blur-md sticky top-0 z-30 select-none">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-[0.2em] text-[#253F40]/55">Location</span>
              <span className="text-xs font-bold text-[#174F50] px-2 py-0.5 rounded bg-[#DCEDEC] tracking-wide">
                {activeTab}
              </span>
            </div>

            <div className="flex items-center gap-3">
              {/* Language Selector: 🌐 English ▼ */}
              <div className="relative flex items-center">
                <Globe className="absolute left-3.5 h-3.5 w-3.5 text-[#253F40]/75 pointer-events-none" />
                <select
                  value={selectedLanguage}
                  disabled={busy}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="appearance-none bg-[#FFFDF7] border border-[#E5EBEA] pl-9 pr-8 py-1.5 rounded-full text-xs font-semibold text-[#253F40] outline-none focus:border-[#3E9698] cursor-pointer shadow-sm disabled:opacity-50"
                >
                  <option value="auto">English</option>
                  <option value="en-IN">English (India)</option>
                  <option value="hi-IN">Hindi</option>
                  <option value="te-IN">Telugu</option>
                </select>
                <span className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none text-[#253F40]/60 text-[8px]">▼</span>
              </div>

              {/* Connection Status: ● Backend Online Wi-Fi */}
              <button
                type="button"
                onClick={() => void refreshHealth()}
                disabled={busy}
                className="inline-flex items-center gap-2 bg-[#FFFDF7] border border-[#E5EBEA] px-4 py-1.5 rounded-full text-xs font-semibold text-[#253F40] hover:bg-[#F8F3E8] transition-colors shadow-sm disabled:opacity-50"
              >
                <span className={cn(
                  "h-2 w-2 rounded-full",
                  backend === "online" ? "bg-[#3E9698]" : backend === "checking" ? "bg-[#E58B42] animate-pulse" : "bg-destructive"
                )} />
                <span>
                  {backend === "online" ? "Backend Online" : backend === "checking" ? "Checking Status" : "Backend Offline"}
                </span>
                <Wifi className="h-3.5 w-3.5 text-[#253F40]/65 stroke-[2.2px] ml-1" />
              </button>
            </div>
          </div>
        </header>

        {/* Content Layout Split */}
        <main className="flex-1 flex flex-col p-6 md:p-8">

          {activeTab === "Home" || activeTab === "Voice Query" || activeTab === "Text Query" ? (
            <div className="flex flex-col lg:flex-row gap-8 flex-1">

              {/* Interaction Left/Middle Column (Large) */}
              <div className="flex-1 space-y-6 max-w-3xl">

                {/* Visual Editorial Hero Banner */}
                <div className="relative w-full py-4 flex items-center select-none">

                  {/* Left content description */}
                  <div className="relative z-10 max-w-sm">
                    <h2 className="text-3xl md:text-[38px] tracking-tight leading-tight">
                      <span className="font-display font-medium text-[#174F50]">Goa Speaks,</span>
                      <br className="hidden sm:inline" />
                      <span className="font-sans font-light text-[#253F40] ml-1">AI Listens</span>
                      <span className="text-[#E58B42] font-extrabold ml-[3px]">.</span>
                    </h2>
                    <p className="text-xs text-[#253F40]/75 mt-2 tracking-wide font-medium">
                      Ask anything in your language. Get grounded answers.
                    </p>

                    {/* Double Teal Wave Deco Ornament */}
                    <div className="mt-4 text-[#3E9698] opacity-75 w-16">
                      <svg viewBox="0 0 40 10" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M0 3 Q 10 0, 20 3 T 40 3 M0 6 Q 10 3, 20 6 T 40 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                      </svg>
                    </div>
                  </div>
                </div>

                {/* Horizontal Query Input Pill */}
                <div className="w-full">
                  <QuestionForm disabled={busy} onSubmit={handleTextSubmit} />
                </div>

                {/* Centered Microphone recorder */}
                <div className="w-full flex justify-center py-4">
                  <VoiceButton state={state} onToggle={toggleRecording} />
                </div>

                {/* API error layout */}
                {error && (
                  <div className="flex items-start gap-3 rounded-xl border border-destructive/20 bg-destructive/5 p-4 text-xs text-foreground select-none">
                    <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
                    <div>
                      <h4 className="font-semibold text-destructive">Submission Error</h4>
                      <p className="mt-1 text-muted-foreground">{error}</p>
                    </div>
                  </div>
                )}

                {/* Conditional Demo Mode Warning */}
                {demoMode && !error && (
                  <div className="flex items-start gap-3 rounded-xl border border-[#E58B42]/30 bg-[#E58B42]/5 p-4 text-xs text-foreground select-none">
                    <HelpCircle className="mt-0.5 h-4 w-4 shrink-0 text-[#E58B42]" />
                    <div>
                      <h4 className="font-semibold text-[#E58B42]">Demo Mode Active</h4>
                      <p className="mt-1 text-[#253F40]/80">
                        The backend is currently unreachable. You are viewing sample verification outputs instead. Configure <code className="font-mono bg-[#F8F3E8] px-1 py-0.5 rounded">VITE_API_BASE_URL</code> to connect live.
                      </p>
                    </div>
                  </div>
                )}

                {/* Result Block cards */}
                {result && (
                  <div className="space-y-6 pt-4 animate-fade-in">

                    {/* Transcript Card 01 */}
                    <div className="rounded-2xl border border-[#E5EBEA] bg-[#FFFDF7] p-5.5 shadow-sm relative overflow-hidden">
                      <div className="flex items-center justify-between pb-3 border-b border-[#E5EBEA]/40 select-none">
                        <h3 className="flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-[#174F50]">
                          <span className="font-mono text-[#3E9698] text-sm">01</span>
                          Transcript
                        </h3>

                        {/* Audio Wave Badge circle */}
                        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#F8F3E8] border border-[#E5EBEA]">
                          <svg className="text-[#3E9698] h-4.5 w-4.5" viewBox="0 0 24 24" fill="currentColor">
                            <rect x="3" y="6" width="2" height="12" rx="1" />
                            <rect x="8" y="2" width="2" height="20" rx="1" />
                            <rect x="13" y="8" width="2" height="8" rx="1" />
                            <rect x="18" y="4" width="2" height="16" rx="1" />
                          </svg>
                        </div>
                      </div>

                      <div className="mt-4">
                        <p className="text-xl font-bold leading-relaxed text-[#253F40]">
                          {result.transcript || "—"}
                        </p>
                        <div className="mt-4 flex items-center gap-2 select-none">
                          <span className="text-[10px] font-mono text-[#253F40]/60 font-bold">LANGUAGE:</span>
                          <span className="px-2 py-0.5 rounded bg-[#DCEDEC] border border-[#C6E7E5] text-[#174F50] font-mono text-[10px] font-bold">
                            {result.language_code ? result.language_code.toUpperCase().substring(0, 5) : "—"}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Answer Card 02 */}
                    <div className="rounded-2xl border border-[#E5EBEA] bg-[#FFFDF7] p-5.5 shadow-sm relative overflow-hiddenCent">
                      <div className="flex items-center justify-between flex-wrap gap-2 pb-3 border-b border-[#E5EBEA]/40 select-none">
                        <h3 className="flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-[#174F50]">
                          <span className="font-mono text-[#3E9698] text-sm">02</span>
                          Answer (Grounded)
                        </h3>

                        {/* Grounded confidence check */}
                        <span className={cn(
                          "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] uppercase font-mono tracking-wider font-bold",
                          result.grounded
                            ? "bg-[#DCEDEC]/50 border border-[#C6E7E5] text-[#3E9698]"
                            : "bg-[#FFF5EC] border border-[#F4E8D3] text-[#E58B42]"
                        )}>
                          <Check className="h-3.5 w-3.5 stroke-[2.5px]" />
                          {result.grounded ? "High Confidence Answer" : "Low Confidence Answer"}
                        </span>
                      </div>

                      <div className="mt-4">
                        <p className="text-[15px] leading-relaxed text-[#253F40] whitespace-pre-line font-medium">
                          {result.answer}
                        </p>
                      </div>

                      {/* Dynamic Verification breakdown */}
                      {result.sources.length > 0 && (
                        <div className="mt-6 border-t border-[#E5EBEA]/40 pt-4 select-none">
                          <h4 className="text-xs font-bold text-[#174F50] flex items-center gap-1 text-[11px]">
                            <span className="text-[#3E9698] font-bold text-sm">✓</span>
                            Why this answer is reliable?
                          </h4>
                          <p className="text-xs text-[#253F40]/70 mt-1 font-medium">
                            This answer is grounded in the following relevant sources.
                          </p>

                          {/* Badges */}
                          <div className="flex items-center flex-wrap gap-2.5 mt-4">
                            <span className="flex items-center gap-1.5 bg-[#FFFDF7] border border-[#E5EBEA] px-3 py-1 rounded-full text-[10px] text-[#253F40]/80 font-bold">
                              📄 {result.sources.length} Sources
                            </span>
                            {result.sources[0] && (
                              <span className="flex items-center gap-1.5 bg-[#DCEDEC]/40 border border-[#C6E7E5] px-3 py-1 rounded-full text-[10px] text-[#174F50] font-bold">
                                High Confidence ({result.sources[0].score.toFixed(2)})
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Performance timer 04 */}
                    <div className="space-y-3 pt-2">
                      <h3 className="flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-[#174F50] select-none">
                        <span className="font-mono text-[#3E9698] text-sm">04</span>
                        Performance
                      </h3>
                      <PerformancePanel result={result} benchmark={benchmark} />
                    </div>

                  </div>
                )}
              </div>

              {/* Right Side Column (Sources sidebar 03) */}
              <div className="w-full lg:w-[310px] shrink-0 space-y-4 lg:sticky lg:top-56 h-fit">
                <div className="flex items-center justify-between pb-2 border-b border-[#E5EBEA]/90 select-none">
                  <h3 className="flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-[#174F50]">
                    <span className="font-mono text-[#3E9698] text-sm">03</span>
                    Retrieved Sources ({result ? result.sources.length : 0})
                  </h3>
                </div>

                {result ? (
                  result.sources.length === 0 ? (
                    <div className="rounded-xl border border-dashed border-[#E5EBEA] p-6 text-center select-none bg-[#FFFDF7]">
                      <HelpCircle className="h-8 w-8 text-[#253F40]/30 mx-auto mb-2" />
                      <p className="text-xs text-[#253F40]/70 font-medium">
                        No passages passed retrieval threshold.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4 max-h-[75vh] overflow-y-auto pr-1">
                      {result.sources.map((source) => (
                        <SourceCard
                          key={`${source.query_id}-${source.passage_index}-${source.rank}`}
                          source={source}
                        />
                      ))}
                      <p className="text-[10px] font-mono text-[#253F40]/60 text-center leading-normal pt-2 select-none">
                        ⓘ Scores represent semantic similarity
                      </p>
                    </div>
                  )
                ) : (
                  <div className="rounded-2xl border border-[#E5EBEA] p-6 text-center select-none bg-[#FFFDF7] shadow-sm">
                    <BookOpen className="h-7 w-7 text-[#253F40]/35 mx-auto mb-2.5" />
                    <h4 className="text-xs font-bold text-[#174F50]">Context Sources</h4>
                    <p className="text-[11px] text-[#253F40]/70 mt-1 leading-relaxed font-medium">
                      Ask or type a question to inspect retrieved source chunks from the MSMARCO-XI database.
                    </p>
                  </div>
                )}
              </div>

            </div>
          ) : activeTab === "History" ? (
            <div className="max-w-2xl mx-auto space-y-6 py-6 select-none">
              <div className="rounded-2xl border border-[#E5EBEA] bg-[#FFFDF7] p-6 shadow-sm">
                <h3 className="text-lg font-display font-bold text-[#174F50] flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Query History
                </h3>
                <p className="text-xs text-[#253F40]/75 mt-1 font-medium">
                  Click on any previous query to reload the grounded search context.
                </p>

                <div className="mt-6 flex flex-col gap-3">
                  <div className="p-4 rounded-xl border border-[#E5EBEA] bg-[#F8F3E8]/35 hover:bg-[#FFFDF7] transition-all cursor-pointer flex items-center justify-between group">
                    <div>
                      <p className="text-sm font-bold text-[#253F40] group-hover:text-[#3E9698] transition-colors">
                        "కార్పొరేషన్ అంటే ఏమిటి?"
                      </p>
                      <span className="text-[9px] font-mono text-[#253F40]/60 mt-1 inline-block">10 minutes ago • Telugu • Grounded</span>
                    </div>
                    <ArrowRight className="h-4 w-4 text-[#253F40]/60 group-hover:translate-x-1 transition-all" />
                  </div>

                  <div className="p-4 rounded-xl border border-[#E5EBEA] bg-[#F8F3E8]/35 hover:bg-[#FFFDF7] transition-all cursor-pointer flex items-center justify-between group">
                    <div>
                      <p className="text-sm font-bold text-[#253F40] group-hover:text-[#3E9698] transition-colors">
                        "What is the definition of standard legal personality?"
                      </p>
                      <span className="text-[9px] font-mono text-[#253F40]/60 mt-1 inline-block">2 hours ago • English • Grounded</span>
                    </div>
                    <ArrowRight className="h-4 w-4 text-[#253F40]/60 group-hover:translate-x-1 transition-all" />
                  </div>

                  <div className="p-4 rounded-xl border border-[#E5EBEA] bg-[#F8F3E8]/35 hover:bg-[#FFFDF7] transition-all cursor-pointer flex items-center justify-between group">
                    <div>
                      <p className="text-sm font-bold text-[#253F40] group-hover:text-[#3E9698] transition-colors">
                        "एमएसएमएआरसीओ-XI डेटासेट क्या है?"
                      </p>
                      <span className="text-[9px] font-mono text-[#253F40]/60 mt-1 inline-block">Yesterday • Hindi • Grounded</span>
                    </div>
                    <ArrowRight className="h-4 w-4 text-[#253F40]/60 group-hover:translate-x-1 transition-all" />
                  </div>
                </div>
              </div>
            </div>
          ) : activeTab === "Favorites" ? (
            <div className="max-w-2xl mx-auto space-y-6 py-6 select-none">
              <div className="rounded-2xl border border-[#E5EBEA] bg-[#FFFDF7] p-6 shadow-sm">
                <h3 className="text-lg font-display font-bold text-[#174F50] flex items-center gap-2">
                  <Star className="h-5 w-5" />
                  Favorite Grounded Answers
                </h3>
                <p className="text-xs text-[#253F40]/75 mt-1 font-medium">
                  Keep tabs on highly critical verified knowledge base answers.
                </p>

                <div className="mt-8 text-center py-8">
                  <BookOpen className="h-9 w-9 text-[#3E9698]/50 mx-auto mb-3" />
                  <h4 className="text-sm font-bold text-[#174F50]">No Favorites Yet</h4>
                  <p className="text-xs text-[#253F40]/70 mt-2 max-w-xs mx-auto leading-relaxed">
                    Bookmark answers from responses to pin relevant MSMARCO documentation details here.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            /* About Tab */
            <div className="max-w-2xl mx-auto space-y-6 py-4 select-none">
              <div className="rounded-2xl border border-[#E5EBEA] bg-[#FFFDF7] p-6 shadow-sm">
                <h3 className="text-xl font-display font-bold text-[#174F50] flex items-center gap-2">
                  <Heart className="h-5 w-5 text-[#E58B42]" />
                  About HH Goa 2026 Voice RAG
                </h3>
                <p className="text-xs text-[#253F40]/75 mt-1 font-medium">
                  Building state-of-the-art multilingual Grounded AI assistants.
                </p>

                <div className="mt-6 flex flex-col gap-6 text-sm text-[#253F40]/90 leading-relaxed font-sans font-medium">
                  <p>
                    HH Goa 2026 Voice RAG represents a high-performance showcase, bringing together next-generation speech models and retrieval pipelines to enable seamless queries in regional Indian languages.
                  </p>

                  <div className="grid grid-cols-2 gap-4 pt-2">
                    <div className="p-4 rounded-xl bg-[#F8F3E8]/35 border border-[#E5EBEA]">
                      <h4 className="font-bold text-[#174F50] text-xs uppercase tracking-wider">Acoustic STT</h4>
                      <p className="text-xs text-[#253F40]/70 mt-1">
                        Multilingual voice transcriptions powered by state-of-the-art Sarvam AI voice translation models.
                      </p>
                    </div>

                    <div className="p-4 rounded-xl bg-[#F8F3E8]/35 border border-[#E5EBEA]">
                      <h4 className="font-bold text-[#174F50] text-xs uppercase tracking-wider">Hybrid Retrieval</h4>
                      <p className="text-xs text-[#253F40]/70 mt-1">
                        Combining BM25 keyword matching with FAISS vector representation search over MSMARCO context.
                      </p>
                    </div>
                  </div>

                  <p className="text-xs text-[#253F40]/60 mt-6 text-center border-t border-[#E5EBEA]/40 pt-4">
                    Product designed for the Hacker House Goa 2026. Made with ♥ in India.
                  </p>
                </div>
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}
