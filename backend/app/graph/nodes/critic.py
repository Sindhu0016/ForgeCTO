from app.config import get_settings
from app.graph.llm import dump, dumps, invoke_structured
from app.graph.state import CTOState
from app.schemas.artifacts import CriticOutput


async def critic_node(state: CTOState) -> dict:
    settings = get_settings()
    system = (
        "You are a skeptical principal engineer reviewing a startup CTO pack. "
        "Score overall quality 0-100. Score buildability, market_fit, and technical_risk "
        "(higher technical_risk = more risk). Flag inconsistencies between features, "
        "database entities, and API endpoints. List must-fix items before launch. "
        "Be concrete and concise."
    )
    user = (
        f"Idea: {state['idea']}\n"
        f"Plan: {dumps(state.get('plan'))}\n"
        f"Features: {dumps(state.get('features'))}\n"
        f"Database: {dumps(state.get('database_schema'))}\n"
        f"APIs: {dumps(state.get('api_endpoints'))}\n"
        f"Architecture: {dumps(state.get('architecture'))}\n"
        f"AWS: {dumps(state.get('aws_design'))}\n"
        f"Cost: {dumps(state.get('cost_estimate'))}\n"
        "Produce a structured critic review."
    )
    review = await invoke_structured(CriticOutput, system, user, model=settings.docs_model)
    return {
        "critic_review": dump(review),
        "current_step": "critic",
        "status": "running",
    }
