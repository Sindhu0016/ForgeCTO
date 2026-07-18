import traceback
import uuid
from typing import Any

from sqlalchemy import select

from app.db.models import Project, RunEvent
from app.db.session import AsyncSessionLocal
from app.graph.graph import PIPELINE_STEPS, cto_graph
from app.services.events import ProgressEvent, event_bus


def artifacts_from_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "plan": state.get("plan"),
        "market_research": state.get("market_research"),
        "competitors": state.get("competitors"),
        "features": state.get("features"),
        "architecture": state.get("architecture"),
        "database_schema": state.get("database_schema"),
        "api_endpoints": state.get("api_endpoints"),
        "api_notes": state.get("api_notes"),
        "aws_design": state.get("aws_design"),
        "cost_estimate": state.get("cost_estimate"),
        "roadmap": state.get("roadmap"),
        "sprint_plan": state.get("sprint_plan"),
        "github_issues": state.get("github_issues"),
        "docs_markdown": state.get("docs_markdown"),
        "critic_review": state.get("critic_review"),
        "review_board": state.get("review_board"),
        "errors": state.get("errors") or [],
    }


STEP_LABELS = {
    "planner": "Planning product scope",
    "research": "Researching market and competitors",
    "architecture": "Designing system architecture",
    "database": "Designing database schema",
    "api": "Generating API endpoints",
    "aws": "Designing AWS deployment",
    "documentation": "Writing roadmap, cost, and docs",
    "critic": "Scoring plan consistency and risks",
    "review_board": "Convening AI CTO Review Board",
}


async def _persist_progress(
    project_id: uuid.UUID,
    step: str,
    status: str,
    message: str,
    artifacts: dict | None = None,
    error_message: str | None = None,
) -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one()
        project.current_step = step
        project.status = status
        if artifacts is not None:
            project.artifacts = artifacts
        if error_message is not None:
            project.error_message = error_message
        session.add(
            RunEvent(
                project_id=project_id,
                step=step,
                message=message,
                status=status,
                payload={"partial_keys": list((artifacts or {}).keys())},
            )
        )
        await session.commit()

    await event_bus.publish(
        str(project_id),
        ProgressEvent(step=step, status=status, message=message, partial=artifacts),
    )


async def run_project_pipeline(project_id: uuid.UUID, idea: str) -> None:
    await _persist_progress(project_id, "queued", "running", "Pipeline started")

    # Announce upcoming steps
    for step in PIPELINE_STEPS:
        await event_bus.publish(
            str(project_id),
            ProgressEvent(
                step=step,
                status="pending",
                message=f"Queued: {STEP_LABELS.get(step, step)}",
            ),
        )

    try:
        # Stream node updates via astream
        initial: dict[str, Any] = {
            "idea": idea,
            "project_id": str(project_id),
            "status": "running",
            "current_step": "planner",
            "errors": [],
        }
        final_state: dict[str, Any] = dict(initial)

        async for event in cto_graph.astream(initial, stream_mode="updates"):
            # event is {node_name: update_dict}
            for node_name, update in event.items():
                if not isinstance(update, dict):
                    continue
                final_state.update(update)
                step = update.get("current_step") or node_name
                status = update.get("status") or "running"
                artifacts = artifacts_from_state(final_state)
                message = STEP_LABELS.get(step, f"Completed {step}")
                await _persist_progress(project_id, step, status if status == "completed" else "running", message, artifacts)

        final_artifacts = artifacts_from_state(final_state)
        await _persist_progress(
            project_id,
            "done",
            "completed",
            "All CTO agents finished",
            final_artifacts,
        )
    except Exception as exc:  # noqa: BLE001
        tb = traceback.format_exc()
        err_text = str(exc)
        is_quota = (
            "insufficient_quota" in err_text
            or "Error code: 429" in err_text
            or "exceeded your current quota" in err_text.lower()
        )

        if is_quota:
            # OpenAI billing/quota exhausted — finish with offline demo pack
            await _persist_progress(
                project_id,
                "research",
                "running",
                "OpenAI quota exceeded — switching to free demo pack",
            )
            await run_demo_pipeline(project_id, idea)
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Project).where(Project.id == project_id))
                project = result.scalar_one()
                artifacts = dict(project.artifacts or {})
                artifacts["fallback_reason"] = "openai_insufficient_quota"
                artifacts["errors"] = list(artifacts.get("errors") or []) + [
                    "Live LLM failed due to OpenAI quota; an idea-aligned demo pack was generated instead. "
                    "Add a free GEMINI_API_KEY in .env for live agents without OpenAI billing."
                ]
                project.artifacts = artifacts
                project.error_message = None
                project.status = "completed"
                project.current_step = "done"
                await session.commit()
            await event_bus.publish(
                str(project_id),
                ProgressEvent(
                    step="done",
                    status="completed",
                    message="Completed with free demo pack (OpenAI quota exceeded)",
                    partial=artifacts,
                ),
            )
            return

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one()
            errors = list((project.artifacts or {}).get("errors") or [])
            errors.append(str(exc))
            artifacts = dict(project.artifacts or {})
            artifacts["errors"] = errors
            project.artifacts = artifacts
            project.status = "failed"
            project.current_step = "error"
            project.error_message = f"{exc}\n{tb}"
            session.add(
                RunEvent(
                    project_id=project_id,
                    step="error",
                    message=str(exc),
                    status="failed",
                    payload={"traceback": tb},
                )
            )
            await session.commit()

        await event_bus.publish(
            str(project_id),
            ProgressEvent(step="error", status="failed", message=str(exc), partial=None),
        )


async def run_demo_pipeline(project_id: uuid.UUID, idea: str) -> None:
    """Simulate the agent pipeline offline using template artifacts."""
    import asyncio

    from app.services.demo import build_demo_artifacts

    await _persist_progress(project_id, "queued", "running", "Demo pipeline started (no OpenAI key)")
    artifacts = build_demo_artifacts(idea)

    for step in PIPELINE_STEPS:
        await _persist_progress(
            project_id,
            step,
            "running",
            f"Demo: {STEP_LABELS.get(step, step)}",
            artifacts,
        )
        await asyncio.sleep(0.35)

    await _persist_progress(
        project_id,
        "done",
        "completed",
        "Demo CTO pack ready — add free GEMINI_API_KEY for live agents",
        artifacts,
    )
