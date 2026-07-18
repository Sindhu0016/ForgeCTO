import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getProject, streamProjectEvents, type Project } from "../api/client";
import { AskCTOChat } from "../components/AskCTOChat";
import { ArtifactTabs } from "../components/ArtifactTabs";
import { AuthHeaderActions } from "../components/AuthHeaderActions";
import { StepProgress } from "../components/StepProgress";
import { riskCounts } from "../components/RiskDetection";

export function ProjectDashboard() {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("Board");
  const [liveMessage, setLiveMessage] = useState("");

  useEffect(() => {
    if (!id) return;
    let mounted = true;
    getProject(id)
      .then((p) => {
        if (mounted) setProject(p);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Load failed"));

    const close = streamProjectEvents(
      id,
      (evt) => {
        setLiveMessage(evt.message);
        if (evt.partial) {
          setProject((prev) =>
            prev
              ? {
                  ...prev,
                  artifacts: { ...prev.artifacts, ...evt.partial },
                  status: evt.status === "pending" ? prev.status : evt.status,
                  current_step: evt.step,
                }
              : prev,
          );
        } else {
          setProject((prev) =>
            prev
              ? {
                  ...prev,
                  status: evt.status === "pending" ? prev.status : evt.status,
                  current_step: evt.step,
                }
              : prev,
          );
        }
        if (evt.status === "completed" || evt.status === "failed") {
          getProject(id).then(setProject).catch(() => undefined);
        }
      },
      () => {
        /* EventSource reconnects; refresh snapshot */
        getProject(id).then(setProject).catch(() => undefined);
      },
    );

    return () => {
      mounted = false;
      close();
    };
  }, [id]);

  if (error) {
    return (
      <div className="page">
        <p className="error-text">{error}</p>
        <Link to="/">Back</Link>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="page">
        <p className="muted">Loading project…</p>
      </div>
    );
  }

  const planTitle = (project.artifacts?.plan as { title?: string } | undefined)?.title;
  const risks = riskCounts(project.artifacts || {});

  return (
    <div className="page dash-page">
      <div className="atmosphere subtle" aria-hidden />
      <header className="dash-header">
        <Link className="brand-link" to="/">
          ForgeCTO
        </Link>
        <div className="dash-meta">
          <p className={`status-pill status-${project.status}`}>{project.status}</p>
          {liveMessage && <p className="live-msg">{liveMessage}</p>}
          <AuthHeaderActions />
        </div>
      </header>

      <section className="dash-hero">
        <div className="dash-hero-main">
          <h1>{planTitle || "CTO workspace"}</h1>
          <p className="idea-quote">“{project.idea}”</p>
          <StepProgress currentStep={project.current_step} status={project.status} />
          {project.error_message && <pre className="error-box">{project.error_message}</pre>}
        </div>
        {risks.total > 0 && (
          <button
            type="button"
            className="risk-strip"
            onClick={() => setActiveTab("Risks")}
            title="Open AI Risk Detection"
          >
            <span className="risk-strip-title">AI Risk Detection</span>
            <span className="risk-strip-counts">
              <span className="risk-pill risk-high">{risks.high} high</span>
              <span className="risk-pill risk-medium">{risks.medium} medium</span>
              <span className="risk-pill risk-low">{risks.low} low</span>
            </span>
            <span className="risk-strip-cta">View details →</span>
          </button>
        )}
      </section>

      <div className="dash-body">
        <ArtifactTabs
          projectId={project.id}
          artifacts={project.artifacts || {}}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
        <AskCTOChat
          projectId={project.id}
          enabled={Boolean(
            project.artifacts &&
              (project.artifacts.plan ||
                project.artifacts.features ||
                project.artifacts.database_schema),
          )}
        />
      </div>
    </div>
  );
}
