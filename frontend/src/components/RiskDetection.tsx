import { detectRisks, type RiskItem } from "../lib/risks";

type Props = {
  artifacts: Record<string, any>;
};

const SEVERITY_LABEL: Record<RiskItem["severity"], string> = {
  high: "High",
  medium: "Medium",
  low: "Low",
};

export function riskCounts(artifacts: Record<string, any>) {
  const risks = detectRisks(artifacts);
  return {
    total: risks.length,
    high: risks.filter((r) => r.severity === "high").length,
    medium: risks.filter((r) => r.severity === "medium").length,
    low: risks.filter((r) => r.severity === "low").length,
  };
}

export function RiskDetectionPanel({ artifacts }: Props) {
  const risks = detectRisks(artifacts);

  if (!risks.length) {
    return (
      <div className="panel-stack">
        <section>
          <h3>AI Risk Detection</h3>
          <p className="muted">
            No risks detected yet. Risks are extracted from the critic review, market research,
            API design, and database schema once the pipeline produces them.
          </p>
        </section>
      </div>
    );
  }

  const bySeverity: RiskItem["severity"][] = ["high", "medium", "low"];

  return (
    <div className="panel-stack">
      <section>
        <h3>AI Risk Detection</h3>
        <p className="muted">
          Automatically extracted from the critic review, market research, API design, and
          database schema.
        </p>
        <div className="risk-summary">
          {bySeverity.map((sev) => {
            const count = risks.filter((r) => r.severity === sev).length;
            return (
              <div key={sev} className={`risk-count risk-${sev}`}>
                <span className="risk-count-num">{count}</span>
                <span className="risk-count-label">{SEVERITY_LABEL[sev]}</span>
              </div>
            );
          })}
        </div>
      </section>
      <section>
        <ul className="risk-list">
          {risks.map((r) => (
            <li key={`${r.category}-${r.text}`} className={`risk-item risk-${r.severity}`}>
              <div className="risk-item-head">
                <span className={`risk-badge risk-${r.severity}`}>{SEVERITY_LABEL[r.severity]}</span>
                <span className="risk-category">{r.category}</span>
                <span className="risk-source muted">{r.source}</span>
              </div>
              <p>{r.text}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
