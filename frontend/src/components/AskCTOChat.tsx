import { useState, type FormEvent } from "react";
import { askCto } from "../api/client";

type Msg = { role: "user" | "assistant"; text: string; citations?: string[] };

type Props = {
  projectId: string;
  enabled?: boolean;
};

export function AskCTOChat({ projectId, enabled = true }: Props) {
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "assistant",
      text: "Ask me about this CTO pack — tables, APIs, features, cost, or critic score. I only use what’s in the pack.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const q = input.trim();
    if (!q || loading || !enabled) return;
    setInput("");
    setError("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const res = await askCto(projectId, q);
      setMessages((m) => [
        ...m,
        { role: "assistant", text: res.reply, citations: res.citations },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <aside className="ask-cto" aria-label="Ask the CTO">
      <header className="ask-cto-head">
        <h2>Ask the CTO</h2>
        <p className="muted">Answers grounded in this project’s artifacts</p>
      </header>
      <div className="ask-cto-messages">
        {messages.map((m, i) => (
          <div key={`${m.role}-${i}`} className={`ask-msg ask-${m.role}`}>
            <p>{m.text}</p>
            {!!m.citations?.length && (
              <p className="ask-cite">Sources: {m.citations.join(", ")}</p>
            )}
          </div>
        ))}
      </div>
      {error && <p className="error-text">{error}</p>}
      <form className="ask-cto-form" onSubmit={onSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={enabled ? "e.g. Which tables do I need?" : "Wait for artifacts…"}
          disabled={!enabled || loading}
        />
        <button className="btn primary" type="submit" disabled={!enabled || loading || input.trim().length < 2}>
          {loading ? "…" : "Ask"}
        </button>
      </form>
    </aside>
  );
}
