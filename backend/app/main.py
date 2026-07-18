from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from app.api import api_router
from app.config import get_settings, reload_settings
from app.db.base import Base
from app.db.models import Project
from app.db.session import AsyncSessionLocal, engine
from app.services.seed import SEED_ARTIFACTS, SEED_IDEA


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = reload_settings()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if settings.seed_on_startup:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Project).where(Project.is_seed.is_(True)).limit(1))
            existing = result.scalar_one_or_none()
            if not existing:
                session.add(
                    Project(
                        idea=SEED_IDEA,
                        status="completed",
                        current_step="done",
                        artifacts=SEED_ARTIFACTS,
                        is_seed=True,
                    )
                )
                await session.commit()
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    settings = reload_settings()
    app = FastAPI(title="AI Startup CTO Agent", version="1.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        # Allow any local Vite/dev origin (localhost or 127.0.0.1)
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.get("/")
    async def root(request: Request):
        ui_url = "http://127.0.0.1:5173"
        accept = (request.headers.get("accept") or "").lower()
        ua = (request.headers.get("user-agent") or "").lower()
        # Browsers (and most UI navigations) should land on the React app
        wants_html = "text/html" in accept or "mozilla" in ua
        # #region agent log
        try:
            import json as _json, time as _time
            from pathlib import Path as _Path
            _log = _Path(__file__).resolve().parents[2] / "debug-5a40ce.log"
            with _log.open("a", encoding="utf-8") as _f:
                _f.write(
                    _json.dumps(
                        {
                            "sessionId": "5a40ce",
                            "hypothesisId": "A",
                            "location": "main.py:root",
                            "message": "API root / hit",
                            "data": {
                                "path": str(request.url.path),
                                "host": request.headers.get("host"),
                                "accept": accept[:80],
                                "wants_html": wants_html,
                                "redirecting": wants_html,
                                "user_agent": (request.headers.get("user-agent") or "")[:80],
                            },
                            "timestamp": int(_time.time() * 1000),
                            "runId": "post-fix",
                        }
                    )
                    + "\n"
                )
        except Exception:
            pass
        # #endregion
        if wants_html:
            return RedirectResponse(url=ui_url, status_code=307)
        return {
            "name": "AI Startup CTO Agent",
            "ui": ui_url,
            "health": "/api/health",
            "docs": "/docs",
            "hint": "Open the ui URL for the ForgeCTO web app. This port is the API only.",
        }

    @app.get("/api/health")
    async def health(request: Request):
        s = reload_settings()
        # #region agent log
        try:
            import json as _json, time as _time
            from pathlib import Path as _Path
            _log = _Path(__file__).resolve().parents[2] / "debug-5a40ce.log"
            with _log.open("a", encoding="utf-8") as _f:
                _f.write(
                    _json.dumps(
                        {
                            "sessionId": "5a40ce",
                            "hypothesisId": "B",
                            "location": "main.py:health",
                            "message": "health checked",
                            "data": {
                                "origin": request.headers.get("origin"),
                                "host": request.headers.get("host"),
                                "mode": "live" if s.llm_configured else "demo",
                                "provider": s.active_llm_provider,
                            },
                            "timestamp": int(_time.time() * 1000),
                            "runId": "pre-fix",
                        }
                    )
                    + "\n"
                )
        except Exception:
            pass
        # #endregion
        return {
            "status": "ok",
            "openai_configured": s.openai_configured,
            "gemini_configured": s.gemini_configured,
            "tavily_configured": bool(
                s.tavily_api_key and not s.tavily_api_key.startswith("tvly-your")
            ),
            "llm_provider": s.active_llm_provider,
            "mode": "live" if s.llm_configured else "demo",
        }

    return app


app = create_app()
