import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import Project
from app.db.session import get_db
from app.schemas.api import GitHubExportRequest, GitHubExportResponse, MarkdownExportResponse
from app.services.prd import build_prd
from app.services.scaffold import build_scaffold_zip

router = APIRouter(prefix="/api/projects", tags=["export"])


@router.get("/{project_id}/export/markdown", response_model=MarkdownExportResponse)
async def export_markdown(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> MarkdownExportResponse:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    artifacts = project.artifacts or {}
    content = artifacts.get("docs_markdown") or _build_fallback_markdown(project.idea, artifacts)
    title = (artifacts.get("plan") or {}).get("title") or "cto-pack"
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in title.lower())[:48]
    return MarkdownExportResponse(filename=f"{safe or 'cto-pack'}.md", content=content)


@router.get("/{project_id}/export/markdown/download")
async def download_markdown(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> PlainTextResponse:
    exported = await export_markdown(project_id, db)
    return PlainTextResponse(
        content=exported.content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{exported.filename}"'},
    )


@router.get("/{project_id}/export/prd")
async def export_prd(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> PlainTextResponse:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    artifacts = project.artifacts or {}
    if not artifacts.get("plan") and not artifacts.get("features"):
        raise HTTPException(
            status_code=400,
            detail="Product artifacts are not ready yet. Wait for the pipeline to finish.",
        )

    title = (artifacts.get("plan") or {}).get("title") or "product"
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in str(title).lower())[:40]
    filename = f"{safe or 'product'}-prd.md"
    return PlainTextResponse(
        content=build_prd(project.idea, artifacts),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{project_id}/export/scaffold")
async def export_scaffold(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Response:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    artifacts = project.artifacts or {}
    schema = artifacts.get("database_schema") or {}
    endpoints = artifacts.get("api_endpoints") or []
    if not schema.get("entities") and not endpoints:
        raise HTTPException(
            status_code=400,
            detail="No database schema or API endpoints available to scaffold yet.",
        )

    title = (artifacts.get("plan") or {}).get("title") or "cto-scaffold"
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in str(title).lower())[:40]
    filename = f"{safe or 'cto-scaffold'}.zip"
    data = build_scaffold_zip(project.idea, artifacts)
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{project_id}/export/github", response_model=GitHubExportResponse)
async def export_github(
    project_id: uuid.UUID,
    body: GitHubExportRequest,
    db: AsyncSession = Depends(get_db),
) -> GitHubExportResponse:
    settings = get_settings()
    if not settings.github_token:
        raise HTTPException(status_code=400, detail="GITHUB_TOKEN is not configured")

    repo = body.repo or settings.github_repo
    if not repo or "/" not in repo:
        raise HTTPException(status_code=400, detail="Provide repo as owner/name via body or GITHUB_REPO")

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    issues = (project.artifacts or {}).get("github_issues") or []
    if not issues:
        raise HTTPException(status_code=400, detail="No github_issues in project artifacts yet")

    created: list[dict] = []
    failed: list[dict] = []
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        for issue in issues:
            payload = {
                "title": issue.get("title") or "Untitled",
                "body": issue.get("body") or "",
                "labels": issue.get("labels") or [],
            }
            resp = await client.post(
                f"https://api.github.com/repos/{repo}/issues",
                headers=headers,
                json=payload,
            )
            if resp.status_code >= 300:
                failed.append({"title": payload["title"], "error": resp.text, "status": resp.status_code})
            else:
                data = resp.json()
                created.append({"title": payload["title"], "number": data.get("number"), "url": data.get("html_url")})

    return GitHubExportResponse(created=created, failed=failed)


def _build_fallback_markdown(idea: str, artifacts: dict) -> str:
    parts = [f"# CTO Pack\n\n## Idea\n{idea}\n"]
    if artifacts.get("plan"):
        parts.append(f"## Plan\n```json\n{artifacts['plan']}\n```\n")
    if artifacts.get("features"):
        parts.append("## Features\n")
        for f in artifacts["features"]:
            parts.append(f"- **{f.get('name')}** ({f.get('priority')}): {f.get('description')}\n")
    if artifacts.get("docs_markdown"):
        parts.append(artifacts["docs_markdown"])
    return "\n".join(parts)
