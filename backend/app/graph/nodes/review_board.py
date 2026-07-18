from app.config import get_settings
from app.graph.llm import dump, dumps, invoke_structured
from app.graph.state import CTOState
from app.schemas.artifacts import ReviewBoardOutput
from app.services.review_board import build_review_board


async def review_board_node(state: CTOState) -> dict:
    """Produce the viral AI CTO Review Board after the critic runs."""
    settings = get_settings()
    idea = state.get("idea") or ""
    partial = {
        "plan": state.get("plan"),
        "market_research": state.get("market_research"),
        "features": state.get("features"),
        "architecture": state.get("architecture"),
        "database_schema": state.get("database_schema"),
        "api_endpoints": state.get("api_endpoints"),
        "aws_design": state.get("aws_design"),
        "cost_estimate": state.get("cost_estimate"),
        "critic_review": state.get("critic_review"),
        "sprint_plan": state.get("sprint_plan"),
        "docs_markdown": state.get("docs_markdown"),
    }
    fallback = build_review_board(idea, partial)

    system = (
        "You are an AI CTO Review Board. Score the startup pack for founders and investors. "
        "Return scores 0-100 for architecture_score, scalability, security, cost_efficiency, "
        "production_readiness, investor_readiness. Set development_time_months (e.g. 4.5), "
        "hiring_estimate_engineers, aws_monthly_cost_usd, and risk_score as Low|Medium|High. "
        "Include cost_projections for 100, 10K, 100K, 1M, 10M users; load_predictions; "
        "security_audit findings; hiring_roadmap; investor_pitch_bullets; executive_summary. "
        "Be concrete and optimistic-but-honest."
    )
    user = (
        f"Idea: {idea}\n"
        f"Plan: {dumps(state.get('plan'))}\n"
        f"Architecture: {dumps(state.get('architecture'))}\n"
        f"AWS: {dumps(state.get('aws_design'))}\n"
        f"Cost: {dumps(state.get('cost_estimate'))}\n"
        f"Critic: {dumps(state.get('critic_review'))}\n"
        f"Features count: {len(state.get('features') or [])}\n"
        f"Baseline board (refine, do not invent unrelated domains):\n{dumps(fallback)}\n"
        "Produce the Review Board evaluation."
    )
    try:
        board = await invoke_structured(
            ReviewBoardOutput, system, user, model=settings.docs_model
        )
        data = dump(board)
        # Ensure exploration lists are never empty
        if not data.get("cost_projections"):
            data["cost_projections"] = fallback["cost_projections"]
        if not data.get("load_predictions"):
            data["load_predictions"] = fallback["load_predictions"]
        if not data.get("security_audit"):
            data["security_audit"] = fallback["security_audit"]
        if not data.get("hiring_roadmap"):
            data["hiring_roadmap"] = fallback["hiring_roadmap"]
    except Exception:
        data = fallback

    return {
        "review_board": data,
        "current_step": "review_board",
        "status": "completed",
    }
