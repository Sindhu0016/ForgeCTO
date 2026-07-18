import { useEffect, useRef, useState, type FormEvent, type RefObject } from "react";
import { askGeneralChat, type ChatHistoryMessage } from "../api/client";

type Msg = { role: "user" | "assistant"; text: string };

type Props = {
  /** When true, renders as a full-page panel instead of a floating widget */
  embedded?: boolean;
};

const WELCOME: Msg = {
  role: "assistant",
  text: "Hi — I'm ForgeCTO Assistant. Ask about stacks, MVP scope, architecture, APIs, cloud, or founder planning. For pack-specific answers on a project, use Ask the CTO on the dashboard.",
};

export function GeneralChat({ embedded = false }: Props) {
  const [open, setOpen] = useState(embedded);
  const [messages, setMessages] = useState<Msg[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, open]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const q = input.trim();
    if (!q || loading) return;
    setInput("");
    setError("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const history: ChatHistoryMessage[] = messages
        .filter((m) => m !== WELCOME)
        .slice(-8)
        .map((m) => ({ role: m.role, content: m.text }));
      const res = await askGeneralChat(q, history);
      setMessages((m) => [...m, { role: "assistant", text: res.reply }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat failed");
    } finally {
      setLoading(false);
    }
  }

  if (embedded) {
    return (
      <div className="general-chat general-chat-embedded" aria-label="General chatbot">
        <header className="general-chat-head">
          <h2>ForgeCTO Assistant</h2>
          <p className="muted">General startup & engineering help — not tied to one project</p>
        </header>
        <ChatBody
          messages={messages}
          error={error}
          loading={loading}
          input={input}
          setInput={setInput}
          onSubmit={onSubmit}
          bottomRef={bottomRef}
        />
      </div>
    );
  }

  return (
    <div className="general-chat-float">
      {open && (
        <div className="general-chat general-chat-panel" aria-label="General chatbot">
          <header className="general-chat-head">
            <div>
              <h2>Assistant</h2>
              <p className="muted">Ask anything about building your startup</p>
            </div>
            <button
              type="button"
              className="general-chat-close"
              onClick={() => setOpen(false)}
              aria-label="Close chat"
            >
              ×
            </button>
          </header>
          <ChatBody
            messages={messages}
            error={error}
            loading={loading}
            input={input}
            setInput={setInput}
            onSubmit={onSubmit}
            bottomRef={bottomRef}
          />
        </div>
      )}
      <button
        type="button"
        className={`general-chat-fab ${open ? "is-open" : ""}`}
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label={open ? "Close assistant" : "Open assistant"}
      >
        {open ? "Close" : "Chat"}
      </button>
    </div>
  );
}

function ChatBody({
  messages,
  error,
  loading,
  input,
  setInput,
  onSubmit,
  bottomRef,
}: {
  messages: Msg[];
  error: string;
  loading: boolean;
  input: string;
  setInput: (v: string) => void;
  onSubmit: (e: FormEvent) => void;
  bottomRef: RefObject<HTMLDivElement | null>;
}) {
  return (
    <>
      <div className="general-chat-messages">
        {messages.map((m, i) => (
          <div key={`${m.role}-${i}`} className={`ask-msg ask-${m.role}`}>
            <p>{m.text}</p>
          </div>
        ))}
        {loading && <p className="muted general-chat-typing">Thinking…</p>}
        <div ref={bottomRef} />
      </div>
      {error && <p className="error-text">{error}</p>}
      <form className="ask-cto-form" onSubmit={onSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. What stack for a marketplace MVP?"
          disabled={loading}
        />
        <button className="btn primary" type="submit" disabled={loading || input.trim().length < 2}>
          {loading ? "…" : "Send"}
        </button>
      </form>
    </>
  );
}
