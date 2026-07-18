"""Ask-the-CTO: answer questions grounded only in project artifacts."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from app.graph.llm import invoke_structured


class ChatAnswer(BaseModel):
    reply: str
    citations: list[str] = Field(default_factory=list)


def _truncate(text: str, limit: int = 2500) -> str:
    text = text or ""
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def build_artifact_context(artifacts: dict[str, Any], idea: str) -> str:
    arts = artifacts or {}
    schema = arts.get("database_schema") or {}
    parts = [
        f"## Idea\n{idea}",
        f"## Plan\n{_truncate(json.dumps(arts.get('plan') or {}, default=str), 2000)}",
        f"## Research\n{_truncate(json.dumps(arts.get('market_research') or {}, default=str), 2000)}",
        f"## Competitors\n{_truncate(json.dumps(arts.get('competitors') or [], default=str), 1500)}",
        f"## Features\n{_truncate(json.dumps(arts.get('features') or [], default=str), 2000)}",
        f"## Architecture\n{_truncate(json.dumps(arts.get('architecture') or {}, default=str), 2000)}",
        f"## Database entities\n{_truncate(json.dumps(schema.get('entities') or [], default=str), 2000)}",
        f"## Database DDL\n{_truncate(str(schema.get('ddl') or ''), 2000)}",
        f"## API endpoints\n{_truncate(json.dumps(arts.get('api_endpoints') or [], default=str), 2000)}",
        f"## AWS\n{_truncate(json.dumps(arts.get('aws_design') or {}, default=str), 1500)}",
        f"## Cost\n{_truncate(json.dumps(arts.get('cost_estimate') or {}, default=str), 1000)}",
        f"## Roadmap\n{_truncate(json.dumps(arts.get('roadmap') or [], default=str), 1500)}",
        f"## Critic\n{_truncate(json.dumps(arts.get('critic_review') or {}, default=str), 1500)}",
        f"## Review Board\n{_truncate(json.dumps(arts.get('review_board') or {}, default=str), 2000)}",
    ]
    return "\n\n".join(parts)


async def answer_cto_question(idea: str, artifacts: dict[str, Any], message: str) -> ChatAnswer:
    context = build_artifact_context(artifacts, idea)
    system = (
        "You are the project's virtual CTO. Answer ONLY using the provided CTO pack context. "
        "If the answer is not in the context, say you don't have that in the pack yet. "
        "Citations must be section names from: Idea, Plan, Research, Competitors, Features, "
        "Architecture, Database, API, AWS, Cost, Roadmap, Critic."
    )
    user = f"CTO pack context:\n{context}\n\nFounder question:\n{message}\n\nAnswer with citations."
    try:
        return await invoke_structured(ChatAnswer, system, user)
    except Exception:
        # Offline / no LLM: heuristic reply from artifacts
        return _offline_answer(artifacts, message)


def _offline_answer(artifacts: dict[str, Any], message: str) -> ChatAnswer:
    msg = message.lower()
    schema = artifacts.get("database_schema") or {}
    entities = schema.get("entities") or []
    endpoints = artifacts.get("api_endpoints") or []
    features = artifacts.get("features") or []
    critic = artifacts.get("critic_review") or {}

    if any(k in msg for k in ("table", "schema", "database", "entity", "entities")):
        names = [e.get("name") for e in entities if e.get("name")]
        return ChatAnswer(
            reply=(
                "From the Database section, the pack defines these entities/tables: "
                + (", ".join(names) if names else "none listed yet")
                + "."
            ),
            citations=["Database"],
        )
    if any(k in msg for k in ("api", "endpoint", "route")):
        paths = [f"{e.get('method')} {e.get('path')}" for e in endpoints[:8]]
        return ChatAnswer(
            reply="From the API section: " + ("; ".join(paths) if paths else "no endpoints yet") + ".",
            citations=["API"],
        )
    if any(k in msg for k in ("feature", "mvp", "scope")):
        names = [f.get("name") for f in features if f.get("name")]
        return ChatAnswer(
            reply="Key features in the pack: " + (", ".join(names) if names else "none yet") + ".",
            citations=["Features"],
        )
    if any(k in msg for k in ("score", "risk", "critic")):
        return ChatAnswer(
            reply=(
                f"Critic overall score: {critic.get('overall_score', 'n/a')}. "
                f"{critic.get('summary') or 'No critic summary yet.'}"
            ),
            citations=["Critic"],
        )
    plan = artifacts.get("plan") or {}
    return ChatAnswer(
        reply=(
            f"This pack covers “{plan.get('title') or 'the idea'}”. "
            "Ask about tables, APIs, features, cost, or critic score for specifics. "
            "(Offline answer — configure GEMINI_API_KEY for live CTO chat.)"
        ),
        citations=["Plan"],
    )
