import { useState } from "react";
import { MermaidView } from "./MermaidView";
import { RiskDetectionPanel } from "./RiskDetection";
import { markdownDownloadUrl, prdDownloadUrl } from "../api/client";

type Props = {
  projectId: string;
  artifacts: Record<string, any>;
};

type ExploreKey =
  | "architecture"
  | "risks"
  | "cost"
  | "performance"
  | "security"
  | "hiring"
  | "sprints"
  | "investor";

const EXPLORE: { key: ExploreKey; label: string; hint: string }[] = [
  { key: "architecture", label: "Architecture", hint: "Interactive diagrams" },
  { key: "risks", label: "Risk analysis", hint: "AI-generated risks" },
  { key: "cost", label: "Cost projections", hint: "100 users → 10M" },
  { key: "performance", label: "Performance", hint: "Load predictions" },
  { key: "security", label: "Security audit", hint: "Findings & severity" },
  { key: "hiring", label: "Hiring roadmap", hint: "Team plan" },
  { key: "sprints", label: "Sprint planning", hint: "Execution board" },
  { key: "investor", label: "Investor docs", hint: "Pitch-ready pack" },
];

function scoreTone(n: number): string {
  if (n >= 85) return "good";
  if (n >= 70) return "ok";
  return "warn";
}

function riskTone(label: string): string {
  const l = (label || "").toLowerCase();
  if (l === "low") return "good";
  if (l === "medium") return "ok";
  return "warn";
}

export function ReviewBoard({ projectId, artifacts }: Props) {
  const board = (artifacts.review_board || {}) as Record<string, any>;
  const [explore, setExplore] = useState<ExploreKey>("architecture");

  if (!artifacts.review_board && !artifacts.critic_review && !artifacts.architecture) {
    return (
      <div className="panel-stack">
        <p className="muted">
          The AI CTO Review Board appears when the pipeline finishes scoring your pack.
        </p>
      </div>
    );
  }

  const metrics: { label: string; value: string; tone: string }[] = [
    {
      label: "Architecture Score",
      value: `${board.architecture_score ?? "—"}/100`,
      tone: scoreTone(Number(board.architecture_score ?? 0)),
    },
    {
      label: "Scalability",
      value: `${board.scalability ?? "—"}/100`,
      tone: scoreTone(Number(board.scalability ?? 0)),
    },
    {
      label: "Security",
      value: `${board.security ?? "—"}/100`,
      tone: scoreTone(Number(board.security ?? 0)),
    },
    {
      label: "Cost Efficiency",
      value: `${board.cost_efficiency ?? "—"}/100`,
      tone: scoreTone(Number(board.cost_efficiency ?? 0)),
    },
    {
      label: "Development Time",
      value: board.development_time_months != null ? `${board.development_time_months} Months` : "—",
      tone: "neutral",
    },
    {
      label: "Hiring Estimate",
      value: board.hiring_estimate_engineers != null ? `${board.hiring_estimate_engineers} Engineers` : "—",
      tone: "neutral",
    },
    {
      label: "AWS Monthly Cost",
      value: board.aws_monthly_cost_usd != null ? `$${Number(board.aws_monthly_cost_usd).toLocaleString()}` : "—",
      tone: "neutral",
    },
    {
      label: "Risk Score",
      value: board.risk_score || "—",
      tone: riskTone(String(board.risk_score || "")),
    },
    {
      label: "Production Readiness",
      value: board.production_readiness != null ? `${board.production_readiness}%` : "—",
      tone: scoreTone(Number(board.production_readiness ?? 0)),
    },
    {
      label: "Investor Readiness",
      value: board.investor_readiness != null ? `${board.investor_readiness}%` : "—",
      tone: scoreTone(Number(board.investor_readiness ?? 0)),
    },
  ];

  return (
    <div className="review-board">
      <header className="review-board-head">
        <p className="review-kicker">AI CTO Review Board</p>
        <h3>Comprehensive evaluation</h3>
        {board.executive_summary && <p className="muted">{board.executive_summary}</p>}
      </header>

      <div className="scorecard" role="list">
        {metrics.map((m) => (
          <div key={m.label} className={`scorecard-cell tone-${m.tone}`} role="listitem">
            <span className="scorecard-dot" aria-hidden />
            <div>
              <p className="scorecard-label">{m.label}</p>
              <p className="scorecard-value">{m.value}</p>
            </div>
          </div>
        ))}
      </div>

      <section className="review-explore">
        <h3>Explore the pack</h3>
        <div className="explore-rail" role="tablist" aria-label="Review board sections">
          {EXPLORE.map((item) => (
            <button
              key={item.key}
              type="button"
              role="tab"
              aria-selected={explore === item.key}
              className={explore === item.key ? "explore-tab active" : "explore-tab"}
              onClick={() => setExplore(item.key)}
            >
              <span className="explore-label">{item.label}</span>
              <span className="explore-hint muted">{item.hint}</span>
            </button>
          ))}
        </div>

        <div className="explore-panel" role="tabpanel">
          {explore === "architecture" && (
            <div className="panel-stack">
              <p>{artifacts.architecture?.rationale || "Architecture diagram from the pipeline."}</p>
              <MermaidView chart={artifacts.architecture?.mermaid || ""} id="board-arch" />
              {artifacts.aws_design?.mermaid && (
                <>
                  <h4>AWS layout</h4>
                  <MermaidView chart={artifacts.aws_design.mermaid} id="board-aws" />
                </>
              )}
            </div>
          )}

          {explore === "risks" && <RiskDetectionPanel artifacts={artifacts} />}

          {explore === "cost" && (
            <div className="panel-stack">
              <p className="muted">Projected monthly spend from early traction to hyperscale.</p>
              <div className="proj-table">
                {(board.cost_projections || []).map((row: any) => (
                  <div key={row.users} className="proj-row">
                    <strong>{row.label || `${row.users?.toLocaleString()} users`}</strong>
                    <span>Infra ${Number(row.monthly_infra_usd).toLocaleString()}/mo</span>
                    <span>Ops ${Number(row.monthly_eng_ops_usd).toLocaleString()}/mo</span>
                    <p className="muted">{row.notes}</p>
                  </div>
                ))}
              </div>
              {!board.cost_projections?.length && (
                <p className="muted">Cost projections will appear with the Review Board.</p>
              )}
            </div>
          )}

          {explore === "performance" && (
            <div className="panel-stack">
              <p className="muted">AI load & latency predictions by user scale.</p>
              <ul className="load-list">
                {(board.load_predictions || []).map((row: any) => (
                  <li key={row.users}>
                    <strong>{Number(row.users).toLocaleString()} users</strong>
                    <span>
                      ~{row.peak_rps} peak RPS · p95 {row.p95_latency_ms}ms · {row.db_connections} DB
                      conns
                    </span>
                    <p className="muted">{row.notes}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {explore === "security" && (
            <div className="panel-stack">
              <ul className="sec-list">
                {(board.security_audit || []).map((f: any, i: number) => (
                  <li key={`${f.title}-${i}`} className={`sec-item sev-${f.severity}`}>
                    <div className="sec-head">
                      <span className={`risk-badge risk-${f.severity === "high" ? "high" : f.severity === "medium" ? "medium" : "low"}`}>
                        {f.severity}
                      </span>
                      <strong>{f.title}</strong>
                    </div>
                    <p>{f.detail}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {explore === "hiring" && (
            <div className="panel-stack">
              <p>
                Target team: <strong>{board.hiring_estimate_engineers ?? "—"}</strong> engineers over{" "}
                <strong>{board.development_time_months ?? "—"}</strong> months.
              </p>
              <ul className="hire-list">
                {(board.hiring_roadmap || []).map((h: any) => (
                  <li key={`${h.role}-${h.timing}`}>
                    <strong>
                      {h.count}× {h.role}
                    </strong>
                    <span className="muted">{h.timing}</span>
                    <p>{h.rationale}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {explore === "sprints" && (
            <div className="panel-stack">
              {(artifacts.sprint_plan || []).length === 0 ? (
                <p className="muted">Sprint plan pending…</p>
              ) : (
                (artifacts.sprint_plan || []).map((s: any) => (
                  <section key={s.name}>
                    <h4>
                      {s.name}: {s.goal}
                    </h4>
                    <ul>
                      {(s.tasks || []).map((t: any) => (
                        <li key={t.title}>
                          <strong>{t.title}</strong> ({t.estimate_points} pts) — {t.description}
                        </li>
                      ))}
                    </ul>
                  </section>
                ))
              )}
            </div>
          )}

          {explore === "investor" && (
            <div className="panel-stack">
              <ul>
                {(board.investor_pitch_bullets || []).map((b: string) => (
                  <li key={b}>{b}</li>
                ))}
              </ul>
              <div className="export-row">
                <a className="btn primary" href={prdDownloadUrl(projectId)}>
                  Download PRD
                </a>
                <a className="btn secondary" href={markdownDownloadUrl(projectId)}>
                  Download CTO pack
                </a>
              </div>
              {artifacts.docs_markdown && (
                <pre className="docs-md">{String(artifacts.docs_markdown).slice(0, 2500)}</pre>
              )}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
