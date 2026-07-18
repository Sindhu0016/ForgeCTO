import { MermaidView } from "./MermaidView";
import { ReviewBoard } from "./ReviewBoard";
import { RiskDetectionPanel } from "./RiskDetection";
import { detectRisks } from "../lib/risks";
import {
  exportGithub,
  markdownDownloadUrl,
  prdDownloadUrl,
  scaffoldDownloadUrl,
} from "../api/client";
import { useState } from "react";

type Props = {
  projectId: string;
  artifacts: Record<string, any>;
  activeTab: string;
  onTabChange: (tab: string) => void;
};

const TABS = [
  "Board",
  "Research",
  "Features",
  "Architecture",
  "Database",
  "API",
  "AWS",
  "Cost",
  "Roadmap",
  "Sprints",
  "Score",
  "Risks",
  "Docs",
] as const;

export function ArtifactTabs({ projectId, artifacts, activeTab, onTabChange }: Props) {
  const [exportMsg, setExportMsg] = useState("");
  const [repo, setRepo] = useState("");
  const [exporting, setExporting] = useState(false);

  async function handleGithubExport() {
    setExporting(true);
    setExportMsg("");
    try {
      const res = await exportGithub(projectId, repo || undefined);
      setExportMsg(
        `Created ${res.created.length} issue(s); failed ${res.failed.length}.`,
      );
    } catch (err) {
      setExportMsg(err instanceof Error ? err.message : "Export failed");
    } finally {
      setExporting(false);
    }
  }

  const riskCount = detectRisks(artifacts).length;

  return (
    <div className="artifacts">
      <nav className="tab-rail" role="tablist" aria-label="Artifact sections">
        {TABS.map((tab) => (
          <button
            key={tab}
            role="tab"
            aria-selected={activeTab === tab}
            className={activeTab === tab ? "tab active" : "tab"}
            onClick={() => onTabChange(tab)}
            type="button"
          >
            <span>{tab}</span>
            {tab === "Risks" && riskCount > 0 && (
              <span className="tab-count">{riskCount}</span>
            )}
          </button>
        ))}
      </nav>

      <div className="tab-panel" role="tabpanel">
        {activeTab === "Board" && (
          <ReviewBoard projectId={projectId} artifacts={artifacts} />
        )}
        {activeTab === "Research" && <ResearchPanel artifacts={artifacts} />}
        {activeTab === "Features" && <FeaturesPanel features={artifacts.features || []} />}
        {activeTab === "Architecture" && (
          <ArchitecturePanel architecture={artifacts.architecture} />
        )}
        {activeTab === "Database" && <DatabasePanel schema={artifacts.database_schema} />}
        {activeTab === "API" && (
          <APIPanel endpoints={artifacts.api_endpoints || []} notes={artifacts.api_notes} />
        )}
        {activeTab === "AWS" && <AWSPanel aws={artifacts.aws_design} />}
        {activeTab === "Cost" && <CostPanel cost={artifacts.cost_estimate} aws={artifacts.aws_design} />}
        {activeTab === "Roadmap" && <RoadmapPanel roadmap={artifacts.roadmap || []} />}
        {activeTab === "Sprints" && <SprintsPanel sprints={artifacts.sprint_plan || []} />}
        {activeTab === "Score" && <ScorePanel review={artifacts.critic_review} />}
        {activeTab === "Risks" && <RiskDetectionPanel artifacts={artifacts} />}
        {activeTab === "Docs" && (
          <DocsPanel
            markdown={artifacts.docs_markdown || ""}
            issues={artifacts.github_issues || []}
            projectId={projectId}
            repo={repo}
            setRepo={setRepo}
            exporting={exporting}
            exportMsg={exportMsg}
            onGithubExport={handleGithubExport}
          />
        )}
      </div>
    </div>
  );
}

function ResearchPanel({ artifacts }: { artifacts: Record<string, any> }) {
  const research = artifacts.market_research || {};
  const competitors = artifacts.competitors || [];
  const plan = artifacts.plan || {};

  return (
    <div className="panel-stack">
      {plan.title && (
        <section>
          <h3>{plan.title}</h3>
          <p>{plan.problem_statement}</p>
          <p className="muted">Domain: {plan.domain}</p>
        </section>
      )}
      <section>
        <h3>Market</h3>
        <p>{research.market_summary || "Waiting for research…"}</p>
        {research.market_size_notes && <p className="muted">{research.market_size_notes}</p>}
      </section>
      {!!research.opportunities?.length && (
        <section>
          <h3>Opportunities</h3>
          <ul>
            {research.opportunities.map((o: string) => (
              <li key={o}>{o}</li>
            ))}
          </ul>
        </section>
      )}
      {!!research.risks?.length && (
        <section>
          <h3>Risks</h3>
          <ul>
            {research.risks.map((r: string) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        </section>
      )}
      <section>
        <h3>Competitors</h3>
        {competitors.length === 0 ? (
          <p className="muted">No competitors yet.</p>
        ) : (
          <div className="comp-list">
            {competitors.map((c: any) => (
              <article key={c.name} className="comp-item">
                <h4>{c.name}</h4>
                <p>{c.summary}</p>
                {c.url && (
                  <a href={c.url} target="_blank" rel="noreferrer">
                    Source
                  </a>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function FeaturesPanel({ features }: { features: any[] }) {
  if (!features.length) return <p className="muted">Features will appear after research.</p>;
  return (
    <ul className="feature-list">
      {features.map((f) => (
        <li key={f.name}>
          <div className="feature-head">
            <strong>{f.name}</strong>
            <span className={`prio prio-${f.priority}`}>{f.priority}</span>
          </div>
          <p>{f.description}</p>
          {f.rationale && <p className="muted">{f.rationale}</p>}
        </li>
      ))}
    </ul>
  );
}

function ArchitecturePanel({ architecture }: { architecture: any }) {
  if (!architecture) return <p className="muted">Architecture pending…</p>;
  return (
    <div className="panel-stack">
      <p>{architecture.rationale}</p>
      <section>
        <h3>Recommended stack</h3>
        <ul>
          {Object.entries(architecture.recommended_stack || {}).map(([k, v]) => (
            <li key={k}>
              <strong>{k}:</strong> {String(v)}
            </li>
          ))}
        </ul>
      </section>
      <MermaidView chart={architecture.mermaid || ""} id="arch" />
    </div>
  );
}

function DatabasePanel({ schema }: { schema: any }) {
  if (!schema) return <p className="muted">Database schema pending…</p>;
  return (
    <div className="panel-stack">
      <MermaidView chart={schema.er_mermaid || ""} id="er" />
      <section>
        <h3>Entities</h3>
        <ul>
          {(schema.entities || []).map((e: any) => (
            <li key={e.name}>
              <strong>{e.name}</strong> — {(e.fields || []).map((f: any) => f.name).join(", ")}
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h3>DDL</h3>
        <pre className="code-block">{schema.ddl}</pre>
      </section>
    </div>
  );
}

function APIPanel({ endpoints, notes }: { endpoints: any[]; notes?: string }) {
  if (!endpoints.length) return <p className="muted">API endpoints pending…</p>;
  return (
    <div className="panel-stack">
      {notes && <p className="muted">{notes}</p>}
      <ul className="endpoint-list">
        {endpoints.map((e) => (
          <li key={`${e.method}-${e.path}`}>
            <code className="method">{e.method}</code>
            <code>{e.path}</code>
            <span>{e.summary}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function AWSPanel({ aws }: { aws: any }) {
  if (!aws) return <p className="muted">AWS design pending…</p>;
  return (
    <div className="panel-stack">
      <p>
        Est. monthly infra: ${aws.monthly_cost_low_usd} – ${aws.monthly_cost_high_usd}
      </p>
      {aws.cost_notes && <p className="muted">{aws.cost_notes}</p>}
      <ul>
        {(aws.services || []).map((s: any) => (
          <li key={s.name}>
            <strong>{s.name}</strong> — {s.purpose}
          </li>
        ))}
      </ul>
      <MermaidView chart={aws.mermaid || ""} id="aws" />
    </div>
  );
}

function CostPanel({ cost, aws }: { cost: any; aws: any }) {
  if (!cost) return <p className="muted">Cost estimate pending…</p>;
  return (
    <div className="panel-stack">
      <p>
        Build time: {cost.build_weeks_low}–{cost.build_weeks_high} weeks
      </p>
      <p>
        Engineering: ${cost.engineering_cost_low_usd?.toLocaleString()} – $
        {cost.engineering_cost_high_usd?.toLocaleString()}
      </p>
      <p>
        Monthly infra: ${cost.monthly_infra_low_usd ?? aws?.monthly_cost_low_usd} – $
        {cost.monthly_infra_high_usd ?? aws?.monthly_cost_high_usd}
      </p>
      <p className="muted">Ranges are rough CTO guidance, not a quote.</p>
      {!!cost.assumptions?.length && (
        <ul>
          {cost.assumptions.map((a: string) => (
            <li key={a}>{a}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function RoadmapPanel({ roadmap }: { roadmap: any[] }) {
  if (!roadmap.length) return <p className="muted">Roadmap pending…</p>;
  return (
    <ol className="roadmap">
      {roadmap.map((r) => (
        <li key={`${r.phase}-${r.title}`}>
          <h3>
            {r.phase}: {r.title}
          </h3>
          <p className="muted">{r.duration_weeks} weeks</p>
          <ul>
            {(r.deliverables || []).map((d: string) => (
              <li key={d}>{d}</li>
            ))}
          </ul>
        </li>
      ))}
    </ol>
  );
}

function SprintsPanel({ sprints }: { sprints: any[] }) {
  if (!sprints.length) return <p className="muted">Sprint plan pending…</p>;
  return (
    <div className="panel-stack">
      {sprints.map((s) => (
        <section key={s.name}>
          <h3>{s.name}</h3>
          <p>{s.goal}</p>
          <ul>
            {(s.tasks || []).map((t: any) => (
              <li key={t.title}>
                <strong>{t.title}</strong> ({t.estimate_points} pts) — {t.description}
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}

function ScorePanel({ review }: { review: any }) {
  if (!review) {
    return <p className="muted">Critic score appears after the critic agent finishes.</p>;
  }
  return (
    <div className="panel-stack">
      <section>
        <h3>Overall score</h3>
        <p className="score-hero">{review.overall_score ?? "—"} / 100</p>
        <p>{review.summary}</p>
      </section>
      <section>
        <h3>Dimensions</h3>
        <ul className="score-dims">
          <li>
            <strong>Buildability</strong> {review.buildability}
          </li>
          <li>
            <strong>Market fit</strong> {review.market_fit}
          </li>
          <li>
            <strong>Technical risk</strong> {review.technical_risk}{" "}
            <span className="muted">(higher = more risk)</span>
          </li>
        </ul>
      </section>
      {!!review.inconsistencies?.length && (
        <section>
          <h3>Inconsistencies</h3>
          <ul>
            {review.inconsistencies.map((i: string) => (
              <li key={i}>{i}</li>
            ))}
          </ul>
        </section>
      )}
      {!!review.must_fix_before_launch?.length && (
        <section>
          <h3>Must-fix before launch</h3>
          <ul>
            {review.must_fix_before_launch.map((i: string) => (
              <li key={i}>{i}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function DocsPanel({
  markdown,
  issues,
  projectId,
  repo,
  setRepo,
  exporting,
  exportMsg,
  onGithubExport,
}: {
  markdown: string;
  issues: any[];
  projectId: string;
  repo: string;
  setRepo: (v: string) => void;
  exporting: boolean;
  exportMsg: string;
  onGithubExport: () => void;
}) {
  return (
    <div className="panel-stack">
      <div className="export-row">
        <a className="btn primary" href={prdDownloadUrl(projectId)}>
          Download PRD
        </a>
        <a className="btn secondary" href={markdownDownloadUrl(projectId)}>
          Download CTO pack
        </a>
        <a className="btn secondary" href={scaffoldDownloadUrl(projectId)}>
          Download code scaffold
        </a>
        <input
          className="repo-input"
          placeholder="owner/repo (optional)"
          value={repo}
          onChange={(e) => setRepo(e.target.value)}
        />
        <button className="btn secondary" type="button" disabled={exporting} onClick={onGithubExport}>
          {exporting ? "Creating…" : "Create GitHub Issues"}
        </button>
      </div>
      {exportMsg && <p className="muted">{exportMsg}</p>}
      {!!issues.length && (
        <section>
          <h3>Issue drafts</h3>
          <ul>
            {issues.map((i) => (
              <li key={i.title}>
                <strong>{i.title}</strong>
                <p className="muted">{i.body}</p>
              </li>
            ))}
          </ul>
        </section>
      )}
      <section>
        <h3>Documentation</h3>
        <pre className="docs-md">{markdown || "Docs will appear when the documentation agent finishes."}</pre>
      </section>
    </div>
  );
}
