import { Home, Mic, FileText, History, Star, Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
    activeTab?: string;
    onChangeTab?: (tab: string) => void;
    className?: string;
}

export function Sidebar({ activeTab = "Home", onChangeTab, className }: SidebarProps) {
    const navItems = [
        { name: "Home", icon: Home },
        { name: "Voice Query", icon: Mic },
        { name: "Text Query", icon: FileText },
        { name: "History", icon: History },
        { name: "Favorites", icon: Star },
        { name: "About", icon: Info },
    ];

    return (
        <aside
            className={cn(
                "fixed bottom-0 top-0 left-0 z-40 flex w-[220px] flex-col border-r border-[#E5EBEA] bg-[#F8F3E8] p-5 h-full select-none justify-between",
                className
            )}
        >
            {/* Upper Content */}
            <div className="flex flex-col gap-6 w-full">
                {/* Brand Logo & Header */}
                <div className="flex items-center gap-3.5 mt-2">
                    {/* Goa Postcard Logo */}
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-[#FFFDF7] border border-[#E5EBEA] p-1.5 shadow-sm relative overflow-hidden">
                        <svg className="h-full w-full text-[#174F50]" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                            {/* Ground sand line */}
                            <path d="M10 80 C 40 75, 60 85, 90 80" stroke="currentColor" strokeWidth="2.5" />
                            {/* Seagulls */}
                            <path d="M65 25 C 68 21, 71 25, 74 21" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                            {/* Sun */}
                            <circle cx="50" cy="55" r="14" className="fill-[#E58B42]/10 stroke-[#E58B42]" strokeWidth="1.5" />
                            {/* Palm Tree */}
                            <path d="M30 80 Q 25 50, 36 32" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                            <path d="M36 32 C 45 28, 52 35, 52 35" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
                            <path d="M36 32 C 26 28, 18 35, 18 35" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
                            <path d="M36 32 C 34 20, 42 16, 42 16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                        </svg>
                    </div>

                    <div className="leading-tight">
                        <span className="font-sans text-[10px] font-bold text-[#253F40]/65 uppercase tracking-[0.2em] block">
                            HH GOA 2026
                        </span>
                        <span className="font-display text-base font-extrabold tracking-wide block">
                            <span className="text-[#174F50]">VOICE </span>
                            <span className="text-[#E58B42]">RAG</span>
                        </span>
                    </div>
                </div>

                {/* Subtitle */}
                <span className="text-[10px] font-medium text-[#253F40]/75 tracking-wider block mt-[-10px]">
                    Grounded AI over MSMARCO-XI
                </span>

                {/* Navigation items */}
                <nav className="flex flex-col gap-1 mt-4">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = activeTab === item.name;
                        return (
                            <button
                                key={item.name}
                                onClick={() => onChangeTab?.(item.name)}
                                className={cn(
                                    "flex w-full items-center gap-3.5 rounded-lg px-3.5 py-3 text-xs font-semibold tracking-wide transition-all duration-150",
                                    isActive
                                        ? "bg-[#DCEDEC]/55 text-[#174F50] border-l-[3.5px] border-[#3E9698] shadow-sm rounded-l-none"
                                        : "text-[#253F40]/80 hover:bg-[#FFFDF7]/60 hover:text-[#174F50]"
                                )}
                            >
                                <Icon className={cn("h-4.5 w-4.5", isActive ? "text-[#174F50] stroke-[2.2px]" : "slice-stroke stroke-[1.6px]")} />
                                {item.name}
                            </button>
                        );
                    })}
                </nav>
            </div>

            {/* Lower Sidebar with Coastal Postcard Sketch */}
            <div className="relative pt-6 border-t border-[#E5EBEA]/70 overflow-hidden flex flex-col justify-end min-h-[140px]">
                {/* Postcard Line Art Illustration SVG */}
                <div className="absolute inset-x-0 bottom-12 h-20 opacity-35 text-[#253F40]/60 pointer-events-none transform scale-110">
                    <svg className="w-full h-full" viewBox="0 0 160 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                        {/* Ground beach shore */}
                        <path d="M10 65 Q 40 60, 80 68 T 150 63" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
                        <path d="M0 72 Q 50 68, 100 74 T 160 69" stroke="currentColor" strokeWidth="0.7" opacity="0.5" />

                        {/* Lifeguard Shack tiny outline */}
                        <g transform="translate(15, 42)" stroke="currentColor" strokeWidth="0.8">
                            <rect x="5" y="10" width="12" height="12" />
                            <polygon points="2,10 11,2 20,10" />
                            <line x1="8" y1="22" x2="8" y2="25" />
                            <line x1="14" y1="22" x2="14" y2="25" />
                        </g>

                        {/* Palm trees detail */}
                        <g transform="translate(115, 12)" stroke="currentColor" strokeWidth="1">
                            {/* Palm 1 */}
                            <path d="M12 55 Q 6 35, 10 12" strokeWidth="1.6" />
                            <path d="M10 12 Q 22 10, 24 18" />
                            <path d="M10 12 Q 0 8, -6 12" />
                            <path d="M10 12 Q 18 5, 18 -2" />
                            <path d="M10 12 Q 4 4, -1 -4" />

                            {/* Palm 2 smaller */}
                            <path d="M22 55 Q 18 42, 21 24" strokeWidth="1.2" />
                            <path d="M21 24 Q 28 22, 30 28" />
                            <path d="M21 24 Q 14 20, 10 23" />
                        </g>

                        {/* Seagulls flying */}
                        <path d="M52 14 Q 54.5 11, 57 14 Q 59.5 11, 62 14" stroke="currentColor" strokeWidth="0.7" />
                        <path d="M78 22 Q 80 20, 82 22 Q 84 20, 86 22" stroke="currentColor" strokeWidth="0.5" opacity="0.7" />
                    </svg>
                </div>

                {/* Footer text signature */}
                <div className="relative z-10 flex flex-col items-start gap-1">
                    <p className="text-[11px] font-semibold text-[#253F40] flex items-center gap-1.5">
                        Made with <span className="text-[#E58B42] text-[13px] animate-[pulse_1.5s_infinite]">❤️</span> in India
                    </p>
                    {/* Subtle wave decoration */}
                    <div className="text-[#3E9698] opacity-75 w-14">
                        <svg viewBox="0 0 30 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M0 3 Q 7.5 1, 15 3 T 30 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                        </svg>
                    </div>
                </div>
            </div>
        </aside>
    );
}
