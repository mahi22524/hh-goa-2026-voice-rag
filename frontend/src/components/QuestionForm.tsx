import { useState, type FormEvent } from "react";
import { Send } from "lucide-react";

export function QuestionForm({
  disabled,
  onSubmit,
}: {
  disabled: boolean;
  onSubmit: (question: string) => void;
}) {
  const [value, setValue] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!value.trim() || disabled) return;
    onSubmit(value);
    setValue("");
  }

  return (
    <form onSubmit={handleSubmit} className="w-full select-none">
      <label htmlFor="question" className="sr-only">
        Type your question
      </label>
      <div className="flex items-center gap-2 rounded-full border border-[#E5EBEA] bg-card p-1.5 pl-6 pr-1.5 shadow-sm focus-within:border-[#3E9698] transition-all duration-200">
        <input
          id="question"
          value={value}
          disabled={disabled}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Or type a question about the knowledge base..."
          className="w-full bg-transparent text-sm text-[#253F40] outline-none placeholder:text-[#253F40]/50 disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#3E9698] text-[#FFFDF7] hover:bg-[#3E9698]/90 active:scale-95 transition-all disabled:opacity-40 disabled:scale-100 shadow-sm"
          aria-label="Submit query"
        >
          <Send className="h-4.5 w-4.5 stroke-[2.2px] rotate-[-5deg]" />
        </button>
      </div>
    </form>
  );
}