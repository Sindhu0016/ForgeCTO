export type RiskItem = {
  text: string;
  category: string;
  severity: "high" | "medium" | "low";
  source: string;
};

const AUTH_PATH_HINTS = ["auth", "login", "register", "signup", "webhook", "health"];

export function detectRisks(artifacts: Record<string, any>): RiskItem[] {
  const items: RiskItem[] = [];
  const critic = (artifacts?.critic_review as Record<string, any>) || {};
  const research = (artifacts?.market_research as Record<string, any>) || {};
  const endpoints = (artifacts?.api_endpoints as Record<string, any>[]) || [];
  const schema = (artifacts?.database_schema as Record<string, any>) || {};

  for (const t of critic.must_fix_before_launch || []) {
    items.push({ text: t, category: "Launch blocker", severity: "high", source: "Critic agent" });
  }
  for (const t of critic.inconsistencies || []) {
    items.push({ text: t, category: "Consistency", severity: "medium", source: "Critic agent" });
  }
  for (const t of research.risks || []) {
    items.push({ text: t, category: "Market", severity: "medium", source: "Research agent" });
  }

  for (const e of endpoints) {
    const path = String(e.path || "").toLowerCase();
    const method = String(e.method || "GET").toUpperCase();
    const isAuthExempt = AUTH_PATH_HINTS.some((h) => path.includes(h));
    if (e.auth_required === false && method !== "GET" && !isAuthExempt) {
      items.push({
        text: `${method} ${e.path} allows writes without authentication`,
        category: "Security",
        severity: "high",
        source: "Endpoint scan",
      });
    }
  }

  const entities = (schema.entities as Record<string, any>[]) || [];
  const hasUsers = entities.some((e) => String(e.name || "").toLowerCase().includes("user"));
  if (entities.length > 0 && !hasUsers) {
    items.push({
      text: "Schema has no users/accounts table — auth and ownership checks may be undefined",
      category: "Security",
      severity: "medium",
      source: "Schema scan",
    });
  }

  const tr = critic.technical_risk;
  if (typeof tr === "number" && tr >= 60) {
    items.push({
      text: `Technical risk score is ${tr}/100 — consider de-scoping the MVP`,
      category: "Technical",
      severity: "high",
      source: "Critic agent",
    });
  }

  const order = { high: 0, medium: 1, low: 2 } as const;
  return items.sort((a, b) => order[a.severity] - order[b.severity]);
}
