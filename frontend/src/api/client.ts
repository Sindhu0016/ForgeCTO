const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8001").replace(
  /localhost:8000\b/g,
  "127.0.0.1:8001",
).replace(/127\.0\.0\.1:8000\b/g, "127.0.0.1:8001");

// #region agent log
fetch('http://127.0.0.1:7701/ingest/ad7c5ab2-98fe-4957-8ef2-d2d5006d8d27',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'5a40ce'},body:JSON.stringify({sessionId:'5a40ce',hypothesisId:'B',location:'client.ts:API_URL',message:'resolved API_URL',data:{env:import.meta.env.VITE_API_URL||null,resolved:API_URL},timestamp:Date.now(),runId:'post-fix'})}).catch(()=>{});
// #endregion

export type HealthStatus = {
  status: string;
  openai_configured?: boolean;
  gemini_configured?: boolean;
  tavily_configured?: boolean;
  llm_provider?: string | null;
  mode?: string;
};

export type Project = {
  id: string;
  idea: string;
  status: string;
  current_step: string;
  artifacts: Record<string, unknown>;
  error_message: string | null;
  is_seed: boolean;
  created_at: string;
  updated_at: string;
};

export type ProjectSummary = {
  id: string;
  idea: string;
  status: string;
  current_step: string;
  is_seed: boolean;
  created_at: string;
};

export type SSEPayload = {
  step: string;
  status: string;
  message: string;
  partial?: Record<string, unknown> | null;
};

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const detail = data.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join(", ")
          : res.statusText || "Request failed";
    throw new Error(message);
  }
  return res.json();
}

export async function getHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_URL}/api/health`);
  return handle(res);
}

export async function createProject(idea: string): Promise<Project> {
  const res = await fetch(`${API_URL}/api/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ idea }),
  });
  return handle(res);
}

export async function listProjects(): Promise<ProjectSummary[]> {
  const res = await fetch(`${API_URL}/api/projects`);
  return handle(res);
}

export async function getProject(id: string): Promise<Project> {
  const res = await fetch(`${API_URL}/api/projects/${id}`);
  return handle(res);
}

export function streamProjectEvents(
  id: string,
  onEvent: (evt: SSEPayload) => void,
  onError?: (err: Event) => void,
): () => void {
  const es = new EventSource(`${API_URL}/api/projects/${id}/events`);
  es.onmessage = (msg) => {
    try {
      onEvent(JSON.parse(msg.data) as SSEPayload);
    } catch {
      /* ignore malformed */
    }
  };
  es.onerror = (err) => {
    onError?.(err);
  };
  return () => es.close();
}

export async function exportGithub(
  id: string,
  repo?: string,
): Promise<{ created: unknown[]; failed: unknown[] }> {
  const res = await fetch(`${API_URL}/api/projects/${id}/export/github`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo: repo || null }),
  });
  return handle(res);
}

export function markdownDownloadUrl(id: string): string {
  return `${API_URL}/api/projects/${id}/export/markdown/download`;
}

export function prdDownloadUrl(id: string): string {
  return `${API_URL}/api/projects/${id}/export/prd`;
}

export function scaffoldDownloadUrl(id: string): string {
  return `${API_URL}/api/projects/${id}/export/scaffold`;
}

export async function askCto(
  id: string,
  message: string,
): Promise<{ reply: string; citations: string[] }> {
  const res = await fetch(`${API_URL}/api/projects/${id}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  return handle(res);
}

export type ChatHistoryMessage = {
  role: "user" | "assistant";
  content: string;
};

export async function askGeneralChat(
  message: string,
  history: ChatHistoryMessage[] = [],
): Promise<{ reply: string }> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });
  return handle(res);
}
