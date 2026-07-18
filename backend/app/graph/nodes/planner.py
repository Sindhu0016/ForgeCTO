from app.config import get_settings
from app.graph.llm import dump, invoke_structured
from app.graph.state import CTOState
from app.schemas.artifacts import PlanOutput


async def planner_node(state: CTOState) -> dict:
    settings = get_settings()
    idea = state["idea"]
    system = (
        "You are a startup CTO planner. Clarify the product idea into a crisp plan. "
        "Be concrete and practical for an early-stage MVP."
    )
    user = f"Startup idea:\n{idea}\n\nProduce a structured product plan."
    plan = await invoke_structured(PlanOutput, system, user, model=settings.planner_model)
    return {
        "plan": dump(plan),
        "current_step": "planner",
        "status": "running",
    }
