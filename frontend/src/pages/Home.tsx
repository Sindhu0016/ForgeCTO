import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createProject, getHealth, listProjects, type ProjectSummary } from "../api/client";
import { AuthHeaderActions } from "../components/AuthHeaderActions";

export function Home() {
  const [idea, setIdea] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [liveReady, setLiveReady] = useState<boolean | null>(null);
  const [provider, setProvider] = useState<string | null>(null);
  const [apiDown, setApiDown] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // #region agent log
    fetch('http://127.0.0.1:7701/ingest/ad7c5ab2-98fe-4957-8ef2-d2d5006d8d27',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'5a40ce'},body:JSON.stringify({sessionId:'5a40ce',hypothesisId:'C',location:'Home.tsx:mount',message:'ForgeCTO Home mounted',data:{href:window.location.href,viteEnv:import.meta.env.VITE_API_URL||null},timestamp:Date.now(),runId:'post-fix'})}).catch(()=>{});
    // #endregion
    listProjects()
      .then((list) => {
        setProjects(list);
        setApiDown(false);
        // #region agent log
        fetch('http://127.0.0.1:7701/ingest/ad7c5ab2-98fe-4957-8ef2-d2d5006d8d27',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'5a40ce'},body:JSON.stringify({sessionId:'5a40ce',hypothesisId:'B',location:'Home.tsx:listProjects',message:'listProjects ok',data:{count:list.length},timestamp:Date.now(),runId:'pre-fix'})}).catch(()=>{});
        // #endregion
      })
      .catch((err) => {
        setApiDown(true);
        // #region agent log
        fetch('http://127.0.0.1:7701/ingest/ad7c5ab2-98fe-4957-8ef2-d2d5006d8d27',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'5a40ce'},body:JSON.stringify({sessionId:'5a40ce',hypothesisId:'B',location:'Home.tsx:listProjects',message:'listProjects failed',data:{error:String(err)},timestamp:Date.now(),runId:'pre-fix'})}).catch(()=>{});
        // #endregion
      });
    getHealth()
      .then((h) => {
        setLiveReady(h.mode === "live");
        setProvider(h.llm_provider ?? null);
        setApiDown(false);
        // #region agent log
        fetch('http://127.0.0.1:7701/ingest/ad7c5ab2-98fe-4957-8ef2-d2d5006d8d27',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'5a40ce'},body:JSON.stringify({sessionId:'5a40ce',hypothesisId:'D',location:'Home.tsx:getHealth',message:'getHealth ok',data:{mode:h.mode,provider:h.llm_provider},timestamp:Date.now(),runId:'pre-fix'})}).catch(()=>{});
        // #endregion
      })
      .catch((err) => {
        setLiveReady(null);
        setApiDown(true);
        // #region agent log
        fetch('http://127.0.0.1:7701/ingest/ad7c5ab2-98fe-4957-8ef2-d2d5006d8d27',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'5a40ce'},body:JSON.stringify({sessionId:'5a40ce',hypothesisId:'B',location:'Home.tsx:getHealth',message:'getHealth failed',data:{error:String(err)},timestamp:Date.now(),runId:'pre-fix'})}).catch(()=>{});
        // #endregion
      });
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const project = await createProject(idea.trim());
      navigate(`/projects/${project.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start");
    } finally {
      setLoading(false);
    }
  }

  const seed = projects.find((p) => p.is_seed);

  return (
    <div className="page home-page">
      <div className="atmosphere" aria-hidden />
      <header className="site-header home-header">
        <p className="brand">ForgeCTO</p>
        <AuthHeaderActions />
      </header>

      <main className="hero">
        <h1 className="brand-hero">ForgeCTO</h1>
        <p className="tagline">
          Your virtual startup CTO — from one idea to architecture, schema, APIs, and a roadmap.
        </p>

        {apiDown && (
          <p className="error-text">
            Backend is not reachable. Start uvicorn (port 8001), then refresh.
          </p>
        )}

        {!apiDown && liveReady === false && (
          <p className="seed-link">
            Running in <strong>demo mode</strong>. For free live agents, add{" "}
            <code>GEMINI_API_KEY</code> from{" "}
            <a href="https://aistudio.google.com/apikey" target="_blank" rel="noreferrer">
              Google AI Studio
            </a>{" "}
            to the project root <code>.env</code>, then restart the backend.
          </p>
        )}
        {!apiDown && liveReady === true && (
          <p className="seed-link">
            Live agents enabled via <strong>{provider === "gemini" ? "Gemini (free)" : provider || "LLM"}</strong>.
          </p>
        )}

        <form className="idea-form" onSubmit={onSubmit}>
          <label htmlFor="idea" className="sr-only">
            Startup idea
          </label>
          <textarea
            id="idea"
            rows={3}
            placeholder='e.g. "I want to build an Uber for pet grooming."'
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            required
            minLength={10}
          />
          <button
            className="btn primary"
            type="submit"
            disabled={loading || idea.trim().length < 10 || apiDown}
          >
            {loading
              ? liveReady
                ? "Starting agents…"
                : "Building demo pack…"
              : liveReady === false
                ? "Run demo pipeline"
                : "Run CTO pipeline"}
          </button>
        </form>

        {error && <p className="error-text">{error}</p>}

        {seed && (
          <p className="seed-link">
            Or open the{" "}
            <Link to={`/projects/${seed.id}`}>seed demo (pet grooming)</Link> — no API key required.
          </p>
        )}
      </main>
    </div>
  );
}
