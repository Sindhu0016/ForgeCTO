"""Build the AI CTO Review Board scorecard from pipeline artifacts."""

from __future__ import annotations

from typing import Any

from app.schemas.artifacts import (
    CostProjectionTier,
    HiringRole,
    LoadPrediction,
    ReviewBoardOutput,
    SecurityFinding,
)


def _clamp(n: float, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, int(round(n))))


def _risk_label(technical_risk: int, high_findings: int) -> str:
    if technical_risk >= 65 or high_findings >= 3:
        return "High"
    if technical_risk >= 40 or high_findings >= 1:
        return "Medium"
    return "Low"


def build_review_board(idea: str, artifacts: dict[str, Any]) -> dict[str, Any]:
    arts = artifacts or {}
    critic = arts.get("critic_review") or {}
    cost = arts.get("cost_estimate") or {}
    aws = arts.get("aws_design") or {}
    plan = arts.get("plan") or {}
    features = arts.get("features") or []
    endpoints = arts.get("api_endpoints") or []
    schema = arts.get("database_schema") or {}
    research = arts.get("market_research") or {}

    overall = int(critic.get("overall_score") or 72)
    buildability = int(critic.get("buildability") or 75)
    market_fit = int(critic.get("market_fit") or 70)
    technical_risk = int(critic.get("technical_risk") or 45)

    unauth_writes = 0
    for e in endpoints:
        method = str(e.get("method") or "GET").upper()
        path = str(e.get("path") or "").lower()
        exempt = any(h in path for h in ("auth", "login", "register", "health", "webhook"))
        if e.get("auth_required") is False and method != "GET" and not exempt:
            unauth_writes += 1

    entities = schema.get("entities") or []
    has_users = any("user" in str(e.get("name") or "").lower() for e in entities)

    architecture_score = _clamp(overall * 0.55 + buildability * 0.45 + 8)
    scalability = _clamp(100 - technical_risk * 0.55 + (12 if aws else 0))
    security = _clamp(92 - unauth_writes * 12 - (8 if not has_users and entities else 0) - technical_risk * 0.15)
    infra_mid = float(
        cost.get("monthly_infra_high_usd")
        or aws.get("monthly_cost_high_usd")
        or 400
    )
    infra_low = float(
        cost.get("monthly_infra_low_usd")
        or aws.get("monthly_cost_low_usd")
        or 150
    )
    aws_monthly = round((infra_low + infra_mid) / 2, 0)
    cost_efficiency = _clamp(95 - max(0, aws_monthly - 200) / 20)

    weeks_low = int(cost.get("build_weeks_low") or 8)
    weeks_high = int(cost.get("build_weeks_high") or 14)
    months = round(((weeks_low + weeks_high) / 2) / 4.3, 1)
    engineers = 2 if months <= 3 else (4 if months <= 5 else 6)
    if len(features) > 10:
        engineers = min(8, engineers + 1)

    must_fix = list(critic.get("must_fix_before_launch") or [])
    inconsistencies = list(critic.get("inconsistencies") or [])
    high_findings = len(must_fix) + unauth_writes
    risk_score = _risk_label(technical_risk, high_findings)

    production_readiness = _clamp(
        buildability * 0.5 + security * 0.3 + (100 - technical_risk) * 0.2 - len(must_fix) * 3
    )
    investor_readiness = _clamp(market_fit * 0.55 + overall * 0.25 + production_readiness * 0.2)

    title = plan.get("title") or "this product"
    domain = plan.get("domain") or "the chosen domain"

    security_audit: list[SecurityFinding] = []
    for item in must_fix[:5]:
        security_audit.append(
            SecurityFinding(severity="high", title="Launch blocker", detail=item)
        )
    for item in inconsistencies[:4]:
        security_audit.append(
            SecurityFinding(severity="medium", title="Consistency gap", detail=item)
        )
    if unauth_writes:
        security_audit.append(
            SecurityFinding(
                severity="high",
                title="Unauthenticated write endpoints",
                detail=f"{unauth_writes} write endpoint(s) allow requests without auth.",
            )
        )
    if not has_users and entities:
        security_audit.append(
            SecurityFinding(
                severity="medium",
                title="Missing user/accounts entity",
                detail="Schema may lack a clear users table for ownership and RBAC.",
            )
        )
    for r in (research.get("risks") or [])[:3]:
        security_audit.append(
            SecurityFinding(severity="medium", title="Market risk", detail=str(r))
        )
    if not security_audit:
        security_audit.append(
            SecurityFinding(
                severity="low",
                title="Baseline hardening",
                detail="Add rate limits, secrets management, and dependency scanning before launch.",
            )
        )

    cost_projections = [
        CostProjectionTier(
            users=100,
            label="100 users",
            monthly_infra_usd=round(max(40, aws_monthly * 0.35), 0),
            monthly_eng_ops_usd=2000,
            notes="Single region, shared Postgres, minimal observability.",
        ),
        CostProjectionTier(
            users=10_000,
            label="10K users",
            monthly_infra_usd=round(aws_monthly, 0),
            monthly_eng_ops_usd=8000,
            notes="Autoscale API, managed Postgres, CDN, basic alerting.",
        ),
        CostProjectionTier(
            users=100_000,
            label="100K users",
            monthly_infra_usd=round(aws_monthly * 3.2, 0),
            monthly_eng_ops_usd=18000,
            notes="Read replicas, queue workers, WAF, stronger SLOs.",
        ),
        CostProjectionTier(
            users=1_000_000,
            label="1M users",
            monthly_infra_usd=round(aws_monthly * 12, 0),
            monthly_eng_ops_usd=45000,
            notes="Multi-AZ, caching tier, partitioned hot paths.",
        ),
        CostProjectionTier(
            users=10_000_000,
            label="10M users",
            monthly_infra_usd=round(aws_monthly * 45, 0),
            monthly_eng_ops_usd=120000,
            notes="Multi-region or cell architecture; dedicated platform team.",
        ),
    ]

    load_predictions = [
        LoadPrediction(
            users=100,
            peak_rps=5,
            p95_latency_ms=180,
            db_connections=10,
            notes="Comfortable on a single small API instance.",
        ),
        LoadPrediction(
            users=10_000,
            peak_rps=80,
            p95_latency_ms=220,
            db_connections=40,
            notes="Need connection pooling and async jobs for emails/payouts.",
        ),
        LoadPrediction(
            users=100_000,
            peak_rps=600,
            p95_latency_ms=280,
            db_connections=120,
            notes="Introduce cache for reads; watch booking/hot-row contention.",
        ),
        LoadPrediction(
            users=1_000_000,
            peak_rps=4000,
            p95_latency_ms=320,
            db_connections=350,
            notes="Shard or CQRS for high-write domains; load-test critical APIs.",
        ),
        LoadPrediction(
            users=10_000_000,
            peak_rps=25000,
            p95_latency_ms=400,
            db_connections=800,
            notes="Cell-based deploy; edge caching; dedicated search/index services.",
        ),
    ]

    hiring_roadmap = [
        HiringRole(
            role="Founding full-stack engineer",
            count=2,
            timing="Month 0–1",
            rationale="Ship auth, core loop, and operator UI.",
        ),
        HiringRole(
            role="Backend / platform engineer",
            count=1 if engineers >= 4 else 0,
            timing="Month 2–3",
            rationale="Hardening APIs, jobs, and Postgres performance.",
        ),
        HiringRole(
            role="Product designer",
            count=1,
            timing="Month 1–2",
            rationale="Convert MVP flows into clear conversion UX.",
        ),
        HiringRole(
            role="DevOps / SRE (fractional → full)",
            count=1 if engineers >= 5 else 0,
            timing="Month 3–4",
            rationale="CI/CD, observability, cost controls on AWS.",
        ),
        HiringRole(
            role="QA / automation",
            count=1 if engineers >= 6 else 0,
            timing="Month 4+",
            rationale="Regression suite before scaling marketing spend.",
        ),
    ]
    hiring_roadmap = [h for h in hiring_roadmap if h.count > 0]
    if sum(h.count for h in hiring_roadmap) < engineers:
        hiring_roadmap.append(
            HiringRole(
                role="Additional product engineer",
                count=max(1, engineers - sum(h.count for h in hiring_roadmap)),
                timing="Month 2–4",
                rationale="Absorb feature velocity for P0 backlog.",
            )
        )

    pitch = [
        f"{title} targets {domain} with a scoped MVP of {len(features) or 'core'} features.",
        f"Architecture score {architecture_score}/100 with estimated AWS spend ~${int(aws_monthly)}/mo at early scale.",
        f"Build window ~{months} months with ~{engineers} engineers; production readiness {production_readiness}%.",
        f"Investor readiness {investor_readiness}% — risk rated {risk_score}.",
        "Ask for a pilot cohort, clear unit economics, and a 90-day execution plan from the sprint board.",
    ]

    board = ReviewBoardOutput(
        architecture_score=architecture_score,
        scalability=scalability,
        security=security,
        cost_efficiency=cost_efficiency,
        development_time_months=months,
        hiring_estimate_engineers=engineers,
        aws_monthly_cost_usd=float(aws_monthly),
        risk_score=risk_score,
        production_readiness=production_readiness,
        investor_readiness=investor_readiness,
        executive_summary=(
            critic.get("summary")
            or f"CTO Review Board for {title}: balanced MVP for {domain}. "
            f"Risk {risk_score}; ready for disciplined execution."
        ),
        cost_projections=cost_projections,
        load_predictions=load_predictions,
        security_audit=security_audit,
        hiring_roadmap=hiring_roadmap,
        investor_pitch_bullets=pitch,
    )
    return board.model_dump()
