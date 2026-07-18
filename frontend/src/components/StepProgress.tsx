const STEPS = [
  { key: "planner", label: "Planner" },
  { key: "research", label: "Research" },
  { key: "architecture", label: "Architecture" },
  { key: "database", label: "Database" },
  { key: "api", label: "API" },
  { key: "aws", label: "AWS" },
  { key: "documentation", label: "Docs" },
  { key: "critic", label: "Critic" },
  { key: "review_board", label: "Board" },
];

type Props = {
  currentStep: string;
  status: string;
};

export function StepProgress({ currentStep, status }: Props) {
  const order = STEPS.map((s) => s.key);
  const currentIdx =
    currentStep === "done"
      ? STEPS.length
      : currentStep === "error"
        ? -1
        : Math.max(0, order.indexOf(currentStep === "queued" ? "planner" : currentStep));

  return (
    <ol className="step-rail" aria-label="Agent pipeline progress">
      {STEPS.map((step, idx) => {
        let state = "pending";
        if (status === "failed" && idx === currentIdx) state = "failed";
        else if (status === "completed" || idx < currentIdx) state = "done";
        else if (idx === currentIdx && status === "running") state = "active";
        else if (idx === currentIdx && status !== "pending") state = "active";

        return (
          <li key={step.key} className={`step-item step-${state}`}>
            <span className="step-dot" />
            <span className="step-label">{step.label}</span>
          </li>
        );
      })}
    </ol>
  );
}
