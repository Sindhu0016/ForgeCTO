from typing import Any

from pydantic import BaseModel, Field


class PlanOutput(BaseModel):
    title: str
    domain: str
    problem_statement: str
    target_users: list[str] = Field(default_factory=list)
    mvp_scope: list[str] = Field(default_factory=list)
    later_scope: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class Competitor(BaseModel):
    name: str
    summary: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    url: str | None = None


class Feature(BaseModel):
    name: str
    description: str
    priority: str = "P1"  # P0/P1/P2
    rationale: str = ""


class ResearchOutput(BaseModel):
    market_summary: str
    market_size_notes: str = ""
    opportunities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    competitors: list[Competitor] = Field(default_factory=list)
    features: list[Feature] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class ArchitectureOutput(BaseModel):
    recommended_stack: dict[str, str] = Field(default_factory=dict)
    services: list[str] = Field(default_factory=list)
    rationale: str = ""
    mermaid: str
    non_functional_requirements: list[str] = Field(default_factory=list)


class EntityField(BaseModel):
    name: str
    type: str
    nullable: bool = False
    notes: str = ""


class Entity(BaseModel):
    name: str
    fields: list[EntityField] = Field(default_factory=list)


class Relationship(BaseModel):
    from_entity: str
    to_entity: str
    type: str  # one-to-many, many-to-many, etc.
    description: str = ""


class DatabaseOutput(BaseModel):
    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    ddl: str
    er_mermaid: str


class APIEndpoint(BaseModel):
    method: str
    path: str
    summary: str
    auth_required: bool = True
    request_body: dict[str, Any] | None = None
    response_body: dict[str, Any] | None = None


class APIOutput(BaseModel):
    base_path: str = "/api/v1"
    endpoints: list[APIEndpoint] = Field(default_factory=list)
    notes: str = ""


class AWSOutput(BaseModel):
    services: list[dict[str, str]] = Field(default_factory=list)
    mermaid: str
    monthly_cost_low_usd: float
    monthly_cost_high_usd: float
    cost_notes: str = ""
    deployment_steps: list[str] = Field(default_factory=list)


class CostEstimate(BaseModel):
    build_weeks_low: int
    build_weeks_high: int
    engineering_cost_low_usd: float
    engineering_cost_high_usd: float
    monthly_infra_low_usd: float
    monthly_infra_high_usd: float
    assumptions: list[str] = Field(default_factory=list)


class RoadmapItem(BaseModel):
    phase: str
    title: str
    duration_weeks: int
    deliverables: list[str] = Field(default_factory=list)


class SprintTask(BaseModel):
    title: str
    description: str
    estimate_points: int = 3


class Sprint(BaseModel):
    name: str
    goal: str
    tasks: list[SprintTask] = Field(default_factory=list)


class GitHubIssueDraft(BaseModel):
    title: str
    body: str
    labels: list[str] = Field(default_factory=list)


class DocumentationOutput(BaseModel):
    cost_estimate: CostEstimate
    roadmap: list[RoadmapItem] = Field(default_factory=list)
    sprint_plan: list[Sprint] = Field(default_factory=list)
    github_issues: list[GitHubIssueDraft] = Field(default_factory=list)
    docs_markdown: str


class CriticOutput(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    buildability: int = Field(..., ge=0, le=100)
    market_fit: int = Field(..., ge=0, le=100)
    technical_risk: int = Field(..., ge=0, le=100)
    inconsistencies: list[str] = Field(default_factory=list)
    must_fix_before_launch: list[str] = Field(default_factory=list)
    summary: str


class CostProjectionTier(BaseModel):
    users: int
    label: str
    monthly_infra_usd: float
    monthly_eng_ops_usd: float
    notes: str = ""


class LoadPrediction(BaseModel):
    users: int
    peak_rps: float
    p95_latency_ms: int
    db_connections: int
    notes: str = ""


class SecurityFinding(BaseModel):
    severity: str  # high | medium | low
    title: str
    detail: str


class HiringRole(BaseModel):
    role: str
    count: int
    timing: str
    rationale: str = ""


class ReviewBoardOutput(BaseModel):
    """AI CTO Review Board — viral scorecard + exploration pack."""

    architecture_score: int = Field(..., ge=0, le=100)
    scalability: int = Field(..., ge=0, le=100)
    security: int = Field(..., ge=0, le=100)
    cost_efficiency: int = Field(..., ge=0, le=100)
    development_time_months: float
    hiring_estimate_engineers: int
    aws_monthly_cost_usd: float
    risk_score: str  # Low | Medium | High
    production_readiness: int = Field(..., ge=0, le=100)
    investor_readiness: int = Field(..., ge=0, le=100)
    executive_summary: str = ""
    cost_projections: list[CostProjectionTier] = Field(default_factory=list)
    load_predictions: list[LoadPrediction] = Field(default_factory=list)
    security_audit: list[SecurityFinding] = Field(default_factory=list)
    hiring_roadmap: list[HiringRole] = Field(default_factory=list)
    investor_pitch_bullets: list[str] = Field(default_factory=list)
