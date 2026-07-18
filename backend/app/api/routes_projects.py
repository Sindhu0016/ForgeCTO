import asyncio
import json
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import Project
from app.db.session import AsyncSessionLocal, get_db
from app.schemas.api import ChatRequest, ChatResponse, ProjectCreate, ProjectResponse, ProjectSummary
from app.services.cto_chat import answer_cto_question
from app.services.demo import build_demo_artifacts
from app.services.events import event_bus
from app.services.rate_limit import rate_limiter
from app.services.runner import run_demo_pipeline, run_project_pipeline

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _is_stale_pet_demo(project: Project) -> bool:
    """True when a non-seed demo pack still has the old PawRide pet template."""
    if getattr(project, "is_seed", False):
        return False
    arts = project.artifacts or {}
    if not arts.get("demo_mode") and arts.get("fallback_reason") != "openai_insufficient_quota":
        return False
    plan = arts.get("plan") or {}
    if plan.get("domain") != "Pet services marketplace":
        return False
    idea_l = (project.idea or "").lower()
    # Keep true pet ideas on the pet template; heal everything else.
    if "pet" in idea_l or "groom" in idea_l or "dog" in idea_l:
        return False
    return True


def _heal_stale_pet_demo(project: Project) -> bool:
    """Replace stale pet demo artifacts with an idea-aligned pack. Returns True if healed."""
    if not _is_stale_pet_demo(project):
        return False
    old_arts = dict(project.artifacts or {})
    fresh = build_demo_artifacts(project.idea or "")
    if old_arts.get("fallback_reason"):
        fresh["fallback_reason"] = old_arts["fallback_reason"]
    if old_arts.get("errors"):
        fresh["errors"] = list(old_arts.get("errors") or [])
    project.artifacts = fresh
    return True


def _ensure_critic_on_demo(project: Project) -> bool:
    """Backfill critic_review on older demo packs."""
    arts = dict(project.artifacts or {})
    if arts.get("critic_review"):
        return False
    if not (arts.get("demo_mode") or arts.get("fallback_reason") == "openai_insufficient_quota" or project.is_seed):
        return False
    fresh = build_demo_artifacts(project.idea or "")
    arts["critic_review"] = fresh.get("critic_review")
    project.artifacts = arts
    return True


def _ensure_review_board(project: Project) -> bool:
    """Backfill AI CTO Review Board on packs that predate the feature."""
    arts = dict(project.artifacts or {})
    if arts.get("review_board"):
        return False
    if not (
        arts.get("plan")
        or arts.get("critic_review")
        or arts.get("cost_estimate")
        or arts.get("architecture")
    ):
        return False
    from app.services.review_board import build_review_board

    arts["review_board"] = build_review_board(project.idea or "", arts)
    project.artifacts = arts
    return True


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Project:
    settings = get_settings()
    rate_limiter.max_per_minute = settings.rate_limit_per_minute
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again shortly.")

    project = Project(
        idea=body.idea.strip(),
        status="pending",
        current_step="queued",
        artifacts={},
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    if settings.llm_configured:
        asyncio.create_task(run_project_pipeline(project.id, project.idea))
    else:
        # Offline demo so the UI works without a real API key
        asyncio.create_task(run_demo_pipeline(project.id, project.idea))
    return project


@router.get("", response_model=list[ProjectSummary])
async def list_projects(db: AsyncSession = Depends(get_db)) -> list[Project]:
    result = await db.execute(select(Project).order_by(Project.created_at.desc()).limit(50))
    return list(result.scalars().all())


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    changed = _heal_stale_pet_demo(project)
    changed = _ensure_critic_on_demo(project) or changed
    changed = _ensure_review_board(project) or changed
    if changed:
        await db.commit()
        await db.refresh(project)

    return project


@router.post("/{project_id}/chat", response_model=ChatResponse)
async def chat_with_cto(
    project_id: uuid.UUID,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    changed = _heal_stale_pet_demo(project)
    changed = _ensure_critic_on_demo(project) or changed
    changed = _ensure_review_board(project) or changed
    if changed:
        await db.commit()
        await db.refresh(project)

    arts = project.artifacts or {}
    if not arts.get("plan") and not arts.get("features") and not arts.get("database_schema"):
        raise HTTPException(
            status_code=400,
            detail="Project has no artifacts yet. Wait for the pipeline to finish.",
        )

    answer = await answer_cto_question(project.idea, arts, body.message.strip())
    return ChatResponse(reply=answer.reply, citations=answer.citations)


@router.get("/{project_id}/events")
async def project_events(project_id: uuid.UUID) -> StreamingResponse:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if _heal_stale_pet_demo(project):
            await session.commit()
            await session.refresh(project)
        initial_status = project.status
        initial_step = project.current_step
        initial_artifacts = project.artifacts or {}

    async def event_generator() -> AsyncIterator[str]:
        if initial_status in ("completed", "failed"):
            payload = {
                "step": initial_step,
                "status": initial_status,
                "message": "Project ready" if initial_status == "completed" else "Project failed",
                "partial": initial_artifacts,
            }
            yield f"data: {json.dumps(payload)}\n\n"
            return

        async for evt in event_bus.subscribe(str(project_id)):
            payload = {
                "step": evt.step,
                "status": evt.status,
                "message": evt.message,
                "partial": evt.partial,
            }
            yield f"data: {json.dumps(payload)}\n\n"
            if evt.status == "failed":
                break
            if evt.status == "completed" and evt.step == "done":
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
