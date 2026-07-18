import { useEffect, useRef } from "react";
import mermaid from "mermaid";

mermaid.initialize({
  startOnLoad: false,
  theme: "neutral",
  securityLevel: "loose",
  fontFamily: "IBM Plex Sans, sans-serif",
});

type Props = {
  chart: string;
  id?: string;
};

export function MermaidView({ chart, id = "mermaid-diagram" }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    async function render() {
      if (!ref.current || !chart?.trim()) return;
      try {
        const { svg } = await mermaid.render(`${id}-${Date.now()}`, chart.trim());
        if (!cancelled && ref.current) {
          ref.current.innerHTML = svg;
        }
      } catch (err) {
        if (!cancelled && ref.current) {
          ref.current.innerHTML = `<pre class="mermaid-fallback">${chart}</pre>`;
        }
        console.warn("Mermaid render failed", err);
      }
    }
    void render();
    return () => {
      cancelled = true;
    };
  }, [chart, id]);

  if (!chart?.trim()) {
    return <p className="muted">Diagram not available yet.</p>;
  }

  return <div className="mermaid-wrap" ref={ref} />;
}
