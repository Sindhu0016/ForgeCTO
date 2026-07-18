SEED_ARTIFACTS = {
    "plan": {
        "title": "PawRide — On-demand pet grooming",
        "domain": "Pet services marketplace",
        "problem_statement": "Pet owners struggle to book trusted mobile groomers quickly.",
        "target_users": ["Busy pet owners", "Independent groomers", "Pet salons expanding to mobile"],
        "mvp_scope": [
            "Customer booking",
            "Groomer profiles & availability",
            "Payments & tip",
            "In-app messaging",
            "Basic ratings",
        ],
        "later_scope": ["Subscriptions", "Multi-city dispatch optimization", "Retail upsells"],
        "success_metrics": ["Bookings/week", "Groomer utilization", "Repeat booking rate"],
        "assumptions": ["Launch in one metro", "Groomers bring own equipment"],
    },
    "market_research": {
        "market_summary": (
            "The pet grooming and wellness market continues to grow with rising pet ownership. "
            "On-demand mobile grooming sits between at-home DIY and salon visits."
        ),
        "market_size_notes": "Fragmented local market; winners combine trust, scheduling, and supply density.",
        "opportunities": [
            "Mobile convenience for busy owners",
            "Groomer income flexibility",
            "Photo-rich trust layer",
        ],
        "risks": ["Supply cold-start", "Cancellation rates", "Liability/insurance"],
        "sources": ["https://example.com/pet-market"],
    },
    "competitors": [
        {
            "name": "The Dog Stop Mobile",
            "summary": "Regional mobile grooming fleets",
            "strengths": ["Brand trust", "Vans"],
            "weaknesses": ["Limited markets"],
            "url": None,
        },
        {
            "name": "Local independent groomers",
            "summary": "Scheduled via Instagram/phone",
            "strengths": ["Relationships"],
            "weaknesses": ["No marketplace discovery"],
            "url": None,
        },
    ],
    "features": [
        {
            "name": "Book a groomer",
            "description": "Select pet, service, time window, address",
            "priority": "P0",
            "rationale": "Core loop",
        },
        {
            "name": "Groomer onboarding",
            "description": "Profile, services, rates, availability calendar",
            "priority": "P0",
            "rationale": "Supply side",
        },
        {
            "name": "Payments",
            "description": "Card checkout and payouts",
            "priority": "P0",
            "rationale": "Monetization",
        },
        {
            "name": "Live tracking",
            "description": "Groomer ETA map",
            "priority": "P1",
            "rationale": "Differentiator",
        },
    ],
    "architecture": {
        "recommended_stack": {
            "frontend": "React + TypeScript",
            "backend": "FastAPI",
            "database": "PostgreSQL",
            "payments": "Stripe",
            "maps": "Mapbox / Google Maps",
        },
        "services": ["api", "web", "worker", "postgres", "redis", "object-storage"],
        "rationale": "Simple stack for marketplace MVP with async jobs for payouts and notifications.",
        "mermaid": """flowchart TB
  User[PetOwner] --> Web[ReactWeb]
  Groomer[Groomer] --> Web
  Web --> API[FastAPI]
  API --> DB[(PostgreSQL)]
  API --> Redis[(Redis)]
  API --> Stripe[Stripe]
  API --> Maps[MapsAPI]
  API --> S3[ObjectStorage]
""",
        "non_functional_requirements": ["P99 API < 400ms", "PCI via Stripe", "RBAC for roles"],
    },
    "database_schema": {
        "entities": [
            {
                "name": "users",
                "fields": [
                    {"name": "id", "type": "uuid", "nullable": False, "notes": "PK"},
                    {"name": "role", "type": "text", "nullable": False, "notes": "owner|groomer|admin"},
                    {"name": "email", "type": "text", "nullable": False, "notes": ""},
                ],
            },
            {
                "name": "pets",
                "fields": [
                    {"name": "id", "type": "uuid", "nullable": False, "notes": "PK"},
                    {"name": "owner_id", "type": "uuid", "nullable": False, "notes": "FK users"},
                    {"name": "name", "type": "text", "nullable": False, "notes": ""},
                    {"name": "species", "type": "text", "nullable": False, "notes": ""},
                ],
            },
            {
                "name": "bookings",
                "fields": [
                    {"name": "id", "type": "uuid", "nullable": False, "notes": "PK"},
                    {"name": "owner_id", "type": "uuid", "nullable": False, "notes": ""},
                    {"name": "groomer_id", "type": "uuid", "nullable": False, "notes": ""},
                    {"name": "status", "type": "text", "nullable": False, "notes": ""},
                    {"name": "scheduled_at", "type": "timestamptz", "nullable": False, "notes": ""},
                ],
            },
        ],
        "relationships": [
            {
                "from_entity": "users",
                "to_entity": "pets",
                "type": "one-to-many",
                "description": "Owner has many pets",
            },
            {
                "from_entity": "users",
                "to_entity": "bookings",
                "type": "one-to-many",
                "description": "Owner and groomer related to bookings",
            },
        ],
        "ddl": """CREATE TABLE users (
  id UUID PRIMARY KEY,
  role TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL
);
CREATE TABLE pets (
  id UUID PRIMARY KEY,
  owner_id UUID REFERENCES users(id),
  name TEXT NOT NULL,
  species TEXT NOT NULL
);
CREATE TABLE bookings (
  id UUID PRIMARY KEY,
  owner_id UUID REFERENCES users(id),
  groomer_id UUID REFERENCES users(id),
  status TEXT NOT NULL,
  scheduled_at TIMESTAMPTZ NOT NULL
);""",
        "er_mermaid": """erDiagram
  USERS ||--o{ PETS : owns
  USERS ||--o{ BOOKINGS : books
  USERS ||--o{ BOOKINGS : fulfills
  PETS ||--o{ BOOKINGS : includes
""",
    },
    "api_endpoints": [
        {
            "method": "POST",
            "path": "/api/v1/auth/register",
            "summary": "Register owner or groomer",
            "auth_required": False,
            "request_body": {"email": "string", "role": "owner|groomer"},
            "response_body": {"id": "uuid"},
        },
        {
            "method": "GET",
            "path": "/api/v1/groomers",
            "summary": "List available groomers",
            "auth_required": True,
            "request_body": None,
            "response_body": {"items": []},
        },
        {
            "method": "POST",
            "path": "/api/v1/bookings",
            "summary": "Create booking",
            "auth_required": True,
            "request_body": {"groomer_id": "uuid", "pet_id": "uuid", "scheduled_at": "datetime"},
            "response_body": {"id": "uuid", "status": "pending"},
        },
    ],
    "api_notes": "Version APIs under /api/v1; use JWT auth.",
    "aws_design": {
        "services": [
            {"name": "VPC", "purpose": "Network isolation"},
            {"name": "ECS Fargate", "purpose": "API and worker containers"},
            {"name": "RDS PostgreSQL", "purpose": "Primary database"},
            {"name": "S3", "purpose": "Pet photos and docs"},
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
        "monthly_cost_low_usd": 180,
        "monthly_cost_high_usd": 650,
        "cost_notes": "Early traffic; scales with Fargate tasks and RDS size.",
        "deployment_steps": [
            "Create VPC + subnets",
            "Provision RDS",
            "Build/push images to ECR",
            "Deploy ECS services",
            "Front web with CloudFront",
        ],
    },
    "cost_estimate": {
        "build_weeks_low": 10,
        "build_weeks_high": 16,
        "engineering_cost_low_usd": 80000,
        "engineering_cost_high_usd": 180000,
        "monthly_infra_low_usd": 180,
        "monthly_infra_high_usd": 650,
        "assumptions": ["2-3 engineers", "Single city MVP", "Stripe handles payments compliance"],
    },
    "roadmap": [
        {
            "phase": "Phase 1",
            "title": "MVP booking marketplace",
            "duration_weeks": 8,
            "deliverables": ["Auth", "Listings", "Bookings", "Payments"],
        },
        {
            "phase": "Phase 2",
            "title": "Trust & ops",
            "duration_weeks": 4,
            "deliverables": ["Ratings", "Support tools", "Basic dispatch"],
        },
        {
            "phase": "Phase 3",
            "title": "Growth",
            "duration_weeks": 4,
            "deliverables": ["Referrals", "Subscriptions", "Analytics"],
        },
    ],
    "sprint_plan": [
        {
            "name": "Sprint 1",
            "goal": "Foundation",
            "tasks": [
                {"title": "Auth & roles", "description": "JWT auth for owners/groomers", "estimate_points": 5},
                {"title": "Pet profiles", "description": "CRUD pets", "estimate_points": 3},
            ],
        },
        {
            "name": "Sprint 2",
            "goal": "Marketplace loop",
            "tasks": [
                {"title": "Groomer search", "description": "Filter by distance/service", "estimate_points": 8},
                {"title": "Booking flow", "description": "Create and confirm bookings", "estimate_points": 8},
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
            "title": "Implement booking API",
            "body": "POST/GET bookings with status transitions and ownership checks.",
            "labels": ["backend", "p0"],
        },
        {
            "title": "Owner booking UI",
            "body": "Booking wizard: pet, service, time, address, payment.",
            "labels": ["frontend", "p0"],
        },
    ],
    "docs_markdown": """# PawRide CTO Pack

## Summary
On-demand marketplace connecting pet owners with mobile groomers.

## MVP
- Booking, profiles, payments, messaging, ratings

## Stack
React, FastAPI, PostgreSQL, Stripe, AWS ECS/RDS

## Next steps
1. Validate groomer supply in one city
2. Build MVP booking loop
3. Soft-launch with insurance partner
""",
    "critic_review": {
        "overall_score": 76,
        "buildability": 80,
        "market_fit": 74,
        "technical_risk": 42,
        "inconsistencies": [
            "Live tracking (P1) has no dedicated tracking table yet.",
            "Messaging feature needs a messages entity if in MVP.",
        ],
        "must_fix_before_launch": [
            "Insurance / liability partner for mobile grooming",
            "Stripe Connect payouts for groomers",
            "Background checks on groomer onboarding",
        ],
        "summary": "Solid marketplace MVP; tighten schema coverage for messaging/tracking before scale.",
    },
    "errors": [],
}

from app.services.review_board import build_review_board

SEED_IDEA = "I want to build an Uber for pet grooming. (Seed demo — no API calls)"
SEED_ARTIFACTS["review_board"] = build_review_board(SEED_IDEA, SEED_ARTIFACTS)
