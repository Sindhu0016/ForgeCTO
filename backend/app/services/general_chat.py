"""General ForgeCTO assistant — not tied to a single project pack."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.config import get_settings
from app.graph.llm import invoke_structured


class GeneralChatAnswer(BaseModel):
    reply: str


class HistoryTurn(BaseModel):
    role: str
    content: str


async def answer_general_question(
    message: str,
    history: list[HistoryTurn] | None = None,
) -> GeneralChatAnswer:
    settings = get_settings()
    history = history or []
    transcript = "\n".join(
        f"{t.role}: {t.content}" for t in history[-8:] if t.content.strip()
    )
    system = (
        "You are ForgeCTO Assistant, a helpful startup and software engineering coach. "
        "You can discuss product ideas, MVP scoping, tech stacks, architecture trade-offs, "
        "databases, APIs, cloud costs, fundraising basics, and founder workflows. "
        "Be concise, practical, and actionable. If something needs a full CTO pack "
        "(architecture + schema + APIs), suggest generating one from the home page. "
        "Do not invent private project artifacts you were not given."
    )
    user = (
        (f"Recent conversation:\n{transcript}\n\n" if transcript else "")
        + f"User: {message}\n\nReply helpfully."
    )
    if not settings.llm_configured:
        return _offline_answer(message)
    try:
        return await invoke_structured(GeneralChatAnswer, system, user)
    except Exception:
        return _offline_answer(message)


def _offline_answer(message: str) -> GeneralChatAnswer:
    msg = message.lower()
    if any(k in msg for k in ("stack", "framework", "react", "fastapi", "tech")):
        return GeneralChatAnswer(
            reply=(
                "For most marketplace or SaaS MVPs, a solid starter stack is React + TypeScript "
                "on the frontend, FastAPI on the backend, PostgreSQL for data, and Stripe for "
                "payments. Generate a CTO pack from the home page for a stack tailored to your idea. "
                "(Offline reply — add GEMINI_API_KEY for live chat.)"
            )
        )
    if any(k in msg for k in ("mvp", "scope", "launch", "first version")):
        return GeneralChatAnswer(
            reply=(
                "Keep the MVP tiny: one core user journey, auth, the main transaction "
                "(book/buy/order), and a simple admin/ops view. Cut nice-to-haves until "
                "you have paying users. Paste your idea on the home page to get a scoped plan."
            )
        )
    if any(k in msg for k in ("aws", "cloud", "deploy", "hosting")):
        return GeneralChatAnswer(
            reply=(
                "Early stage: put the API on a small container host (ECS/Fargate or Railway/Render), "
                "managed Postgres (RDS or Neon), object storage for uploads, and a CDN for the SPA. "
                "Avoid multi-region until you have real traffic."
            )
        )
    if any(k in msg for k in ("cost", "budget", "price", "pricing")):
        return GeneralChatAnswer(
            reply=(
                "Ballpark for a solo/early MVP: infra often stays under a few hundred USD/month; "
                "the bigger cost is engineering weeks. Use the Cost tab in a generated CTO pack "
                "for idea-specific ranges."
            )
        )
    return GeneralChatAnswer(
        reply=(
            "I'm ForgeCTO Assistant. Ask about stacks, MVP scope, architecture, APIs, "
            "databases, cloud, or founder planning. For a full generated pack (schema, APIs, "
            "roadmap), describe your idea on the home page. "
            "(Offline answer — configure GEMINI_API_KEY for live replies.)"
        )
    )
