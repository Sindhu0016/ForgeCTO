"""Offline demo artifacts when no usable LLM is available."""

from __future__ import annotations

import re
from typing import Any


def _shorten(text: str, limit: int = 80) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _domain_from_idea(idea: str) -> str:
    lower = idea.lower()
    if "dental" in lower and "crm" in lower:
        return "Dental clinic CRM"
    if "crm" in lower:
        return "CRM / practice operations"
    if "marketplace" in lower or "uber for" in lower:
        return "Marketplace platform"
    cleaned = re.sub(r"^i want to build\s+(an?\s+)?", "", idea.strip(), flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    if not cleaned:
        return "Custom product"
    return _shorten(cleaned, 72)


def _keywords(idea: str) -> list[str]:
    stop = {
        "i",
        "want",
        "to",
        "build",
        "an",
        "a",
        "the",
        "for",
        "and",
        "of",
        "with",
        "my",
        "our",
        "that",
        "this",
        "in",
        "on",
        "to",
        "manage",
    }
    words = re.findall(r"[a-zA-Z]{3,}", idea.lower())
    seen: list[str] = []
    for w in words:
        if w in stop or w in seen:
            continue
        seen.append(w)
        if len(seen) >= 6:
            break
    return seen or ["product", "users", "workflow"]


def build_demo_artifacts(idea: str) -> dict[str, Any]:
    """Build a demo CTO pack aligned to the founder's idea (not the pet seed)."""
    idea = idea.strip()
    short = _shorten(idea)
    domain = _domain_from_idea(idea)
    keys = _keywords(idea)
    noun = keys[0] if keys else "product"
    noun2 = keys[1] if len(keys) > 1 else "operations"

    plan = {
        "title": f"Demo CTO pack — {short}",
        "domain": domain,
        "problem_statement": f"Founder idea (demo mode, no live LLM): {idea}",
        "target_users": [
            f"Primary operators working on {domain.lower()}",
            "Admins / clinic or org owners",
            "End customers / patients / clients served by the product",
        ],
        "mvp_scope": [
            f"Core records for {noun} and {noun2}",
            "Scheduling / appointments workflow",
            "User auth and role-based access",
            "Basic dashboard and search",
            "Billing / invoice tracking (lightweight)",
        ],
        "later_scope": [
            "Automations and reminders",
            "Reporting & analytics",
            "Integrations (calendar, payments, messaging)",
        ],
        "success_metrics": [
            "Weekly active operators",
            "Appointments completed / week",
            "Time saved vs spreadsheet baseline",
        ],
        "assumptions": [
            "Generated in offline demo mode without a usable LLM quota",
            "Single-tenant MVP first; multi-location later",
            f"Domain framing derived from idea: {domain}",
        ],
    }

    research = {
        "market_summary": (
            f"Offline demo research for: {idea}. "
            "Live market research requires a working LLM key "
            "(prefer free GEMINI_API_KEY, or a billed OPENAI_API_KEY)."
        ),
        "market_size_notes": (
            f"Niche software for {domain.lower()} is typically sold to SMBs that still "
            "run on phone/spreadsheet workflows."
        ),
        "opportunities": [
            f"Digitize {noun}/{noun2} workflows described in the idea",
            "Replace fragmented tools with one operator console",
            "Automate reminders, follow-ups, and status tracking",
        ],
        "risks": [
            "Data migration from paper/spreadsheets",
            "Adoption by busy staff",
            "Compliance / privacy requirements in the domain",
        ],
        "sources": ["https://example.com/demo-research"],
    }

    competitors = [
        {
            "name": "Legacy niche software",
            "summary": f"Older tools adjacent to {domain.lower()}",
            "strengths": ["Established install base"],
            "weaknesses": ["Clunky UX", "Weak modern integrations"],
            "url": None,
        },
        {
            "name": "Horizontal CRM / SaaS",
            "summary": "General CRMs adapted with custom fields and workarounds",
            "strengths": ["Broad ecosystem"],
            "weaknesses": ["Not purpose-built for this workflow"],
            "url": None,
        },
        {
            "name": "Spreadsheets + phone booking",
            "summary": "Status-quo process many small teams still use",
            "strengths": ["Familiar", "Zero license cost"],
            "weaknesses": ["Error-prone", "No automation", "Hard to scale"],
            "url": None,
        },
    ]

    features = [
        {
            "name": f"{noun.title()} records",
            "description": f"Create and manage core {noun} entities for this product",
            "priority": "P0",
            "rationale": "Core data model",
        },
        {
            "name": "Appointment scheduling",
            "description": "Book, reschedule, and track appointment status",
            "priority": "P0",
            "rationale": "Primary operator workflow",
        },
        {
            "name": "Staff roles & auth",
            "description": "Login with admin/staff permissions",
            "priority": "P0",
            "rationale": "Security baseline",
        },
        {
            "name": "Invoices / billing status",
            "description": "Track charges and payment state linked to records",
            "priority": "P1",
            "rationale": "Monetization / ops completeness",
        },
    ]

    architecture = {
        "recommended_stack": {
            "frontend": "React + TypeScript",
            "backend": "FastAPI",
            "database": "PostgreSQL",
            "auth": "Clerk or JWT",
            "payments": "Stripe (optional)",
        },
        "services": ["api", "web", "worker", "postgres", "redis", "object-storage"],
        "rationale": (
            f"Simple SaaS stack for an MVP in {domain.lower()}, "
            "with async jobs for reminders and exports."
        ),
        "mermaid": """flowchart TB
  User[Operator] --> Web[ReactWeb]
  Patient[EndUser] --> Web
  Web --> API[FastAPI]
  API --> DB[(PostgreSQL)]
  API --> Redis[(Redis)]
  API --> Stripe[Stripe]
  API --> S3[ObjectStorage]
""",
        "non_functional_requirements": [
            "P99 API < 400ms",
            "Role-based access control",
            "Audit log for sensitive record changes",
        ],
    }

    database_schema = {
        "entities": [
            {
                "name": "users",
                "fields": [
                    {"name": "id", "type": "uuid", "nullable": False, "notes": "PK"},
                    {"name": "role", "type": "text", "nullable": False, "notes": "admin|staff"},
                    {"name": "email", "type": "text", "nullable": False, "notes": ""},
                ],
            },
            {
                "name": "customers",
                "fields": [
                    {"name": "id", "type": "uuid", "nullable": False, "notes": "PK"},
                    {"name": "full_name", "type": "text", "nullable": False, "notes": ""},
                    {"name": "phone", "type": "text", "nullable": True, "notes": ""},
                    {"name": "notes", "type": "text", "nullable": True, "notes": ""},
                ],
            },
            {
                "name": "appointments",
                "fields": [
                    {"name": "id", "type": "uuid", "nullable": False, "notes": "PK"},
                    {"name": "customer_id", "type": "uuid", "nullable": False, "notes": "FK"},
                    {"name": "staff_id", "type": "uuid", "nullable": True, "notes": "FK users"},
                    {"name": "status", "type": "text", "nullable": False, "notes": ""},
                    {"name": "scheduled_at", "type": "timestamptz", "nullable": False, "notes": ""},
                ],
            },
            {
                "name": "invoices",
                "fields": [
                    {"name": "id", "type": "uuid", "nullable": False, "notes": "PK"},
                    {"name": "customer_id", "type": "uuid", "nullable": False, "notes": "FK"},
                    {"name": "amount_cents", "type": "int", "nullable": False, "notes": ""},
                    {"name": "status", "type": "text", "nullable": False, "notes": "draft|paid"},
                ],
            },
        ],
        "relationships": [
            {
                "from_entity": "customers",
                "to_entity": "appointments",
                "type": "one-to-many",
                "description": "Customer has many appointments",
            },
            {
                "from_entity": "customers",
                "to_entity": "invoices",
                "type": "one-to-many",
                "description": "Customer has many invoices",
            },
        ],
        "ddl": """CREATE TABLE users (
  id UUID PRIMARY KEY,
  role TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL
);
CREATE TABLE customers (
  id UUID PRIMARY KEY,
  full_name TEXT NOT NULL,
  phone TEXT,
  notes TEXT
);
CREATE TABLE appointments (
  id UUID PRIMARY KEY,
  customer_id UUID REFERENCES customers(id),
  staff_id UUID REFERENCES users(id),
  status TEXT NOT NULL,
  scheduled_at TIMESTAMPTZ NOT NULL
);
CREATE TABLE invoices (
  id UUID PRIMARY KEY,
  customer_id UUID REFERENCES customers(id),
  amount_cents INT NOT NULL,
  status TEXT NOT NULL
);""",
        "er_mermaid": """erDiagram
  USERS ||--o{ APPOINTMENTS : staffs
  CUSTOMERS ||--o{ APPOINTMENTS : books
  CUSTOMERS ||--o{ INVOICES : billed
""",
    }

    api_endpoints = [
        {
            "method": "POST",
            "path": "/api/v1/auth/register",
            "summary": "Register staff/admin user",
            "auth_required": False,
            "request_body": {"email": "string", "role": "admin|staff"},
            "response_body": {"id": "uuid"},
        },
        {
            "method": "GET",
            "path": "/api/v1/customers",
            "summary": "List customers / patients",
            "auth_required": True,
            "request_body": None,
            "response_body": {"items": []},
        },
        {
            "method": "POST",
            "path": "/api/v1/appointments",
            "summary": "Create appointment",
            "auth_required": True,
            "request_body": {
                "customer_id": "uuid",
                "scheduled_at": "datetime",
                "staff_id": "uuid",
            },
            "response_body": {"id": "uuid", "status": "scheduled"},
        },
        {
            "method": "POST",
            "path": "/api/v1/invoices",
            "summary": "Create invoice",
            "auth_required": True,
            "request_body": {"customer_id": "uuid", "amount_cents": 0},
            "response_body": {"id": "uuid", "status": "draft"},
        },
    ]

    aws_design = {
        "services": [
            {"name": "VPC", "purpose": "Network isolation"},
            {"name": "ECS Fargate", "purpose": "API and worker containers"},
            {"name": "RDS PostgreSQL", "purpose": "Primary database"},
            {"name": "S3", "purpose": "Documents and exports"},
            {"name": "CloudFront", "purpose": "CDN for React SPA"},
            {"name": "ALB", "purpose": "HTTPS load balancing"},
        ],
        "mermaid": """flowchart TB
  Users --> CF[CloudFront]
  CF --> S3web[S3_SPA]
  Users --> ALB
  ALB --> ECS[ECS_Fargate_API]
  ECS --> RDS[(RDS_Postgres)]
  ECS --> S3[(S3)]
  ECS --> SM[SecretsManager]
""",
        "monthly_cost_low_usd": 150,
        "monthly_cost_high_usd": 550,
        "cost_notes": "Early SMB traffic; scales with Fargate tasks and RDS size.",
        "deployment_steps": [
            "Create VPC + subnets",
            "Provision RDS",
            "Build/push images to ECR",
            "Deploy ECS services",
            "Front web with CloudFront",
        ],
    }

    artifacts: dict[str, Any] = {
        "plan": plan,
        "market_research": research,
        "competitors": competitors,
        "features": features,
        "architecture": architecture,
        "database_schema": database_schema,
        "api_endpoints": api_endpoints,
        "api_notes": "Version APIs under /api/v1; use JWT or Clerk session tokens.",
        "aws_design": aws_design,
        "cost_estimate": {
            "build_weeks_low": 8,
            "build_weeks_high": 14,
            "engineering_cost_low_usd": 60000,
            "engineering_cost_high_usd": 150000,
            "monthly_infra_low_usd": 150,
            "monthly_infra_high_usd": 550,
            "assumptions": ["2 engineers", "Single-org MVP", f"Scope centered on {domain}"],
        },
        "roadmap": [
            {
                "phase": "Phase 1",
                "title": f"MVP for {domain}",
                "duration_weeks": 8,
                "deliverables": ["Auth", "Core records", "Appointments", "Basic invoices"],
            },
            {
                "phase": "Phase 2",
                "title": "Ops polish",
                "duration_weeks": 4,
                "deliverables": ["Reminders", "Reporting", "Role permissions"],
            },
            {
                "phase": "Phase 3",
                "title": "Growth",
                "duration_weeks": 4,
                "deliverables": ["Integrations", "Automations", "Analytics"],
            },
        ],
        "sprint_plan": [
            {
                "name": "Sprint 1",
                "goal": "Foundation",
                "tasks": [
                    {
                        "title": "Auth & roles",
                        "description": "Staff/admin login and RBAC",
                        "estimate_points": 5,
                    },
                    {
                        "title": "Customer records",
                        "description": f"CRUD for core {noun} records",
                        "estimate_points": 5,
                    },
                ],
            },
            {
                "name": "Sprint 2",
                "goal": "Scheduling loop",
                "tasks": [
                    {
                        "title": "Appointment API",
                        "description": "Create/list/update appointments",
                        "estimate_points": 8,
                    },
                    {
                        "title": "Operator calendar UI",
                        "description": "Day/week schedule view",
                        "estimate_points": 8,
                    },
                ],
            },
        ],
        "github_issues": [
            {
                "title": "Set up monorepo and CI",
                "body": "Scaffold FastAPI + React + Postgres with GitHub Actions for lint/test.",
                "labels": ["infra", "p0"],
            },
            {
                "title": "Implement appointments API",
                "body": f"CRUD appointments tied to customers for: {short}",
                "labels": ["backend", "p0"],
            },
            {
                "title": "Operator dashboard UI",
                "body": "Dashboard for today's appointments and customer search.",
                "labels": ["frontend", "p0"],
            },
        ],
        "docs_markdown": (
            f"# CTO Pack (Demo Mode)\n\n## Idea\n{idea}\n\n"
            f"## Domain\n{domain}\n\n"
            "## Note\nThis pack was generated **without a live LLM** using an idea-aligned "
            "local template. Set `GEMINI_API_KEY` (free) or a working `OPENAI_API_KEY` "
            "in the project root `.env` for a live agent run.\n\n"
            f"## MVP focus\n- {noun} / {noun2} records\n- Appointments\n- Invoices\n- Staff roles\n"
        ),
        "critic_review": {
            "overall_score": 72,
            "buildability": 78,
            "market_fit": 70,
            "technical_risk": 45,
            "inconsistencies": [
                f"Confirm every P0 feature for {noun} has a matching API and table.",
                "Invoice status transitions should be documented in the API notes.",
            ],
            "must_fix_before_launch": [
                "Add auth + role checks on all write endpoints",
                "Define backup/restore for Postgres",
                "Validate appointment double-booking rules",
            ],
            "summary": (
                f"Demo critic review for {domain}: solid MVP shape with {noun}/{noun2} "
                "core loop; tighten API–schema alignment and auth before launch."
            ),
        },
        "errors": [],
        "demo_mode": True,
    }
    from app.services.review_board import build_review_board

    artifacts["review_board"] = build_review_board(idea, artifacts)
    return artifacts
