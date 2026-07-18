from app.config import get_settings
from app.graph.llm import dump, dumps, invoke_structured
from app.graph.state import CTOState
from app.schemas.artifacts import ArchitectureOutput


async def architecture_node(state: CTOState) -> dict:
    settings = get_settings()
    system = (
        "You are a principal software architect. Propose a pragmatic cloud-native architecture "
        "for an MVP. Include a Mermaid flowchart (flowchart TB) for the system diagram. "
        "Prefer FastAPI/React/Postgres unless the domain clearly needs something else."
    )
    user = (
        f"Idea: {state['idea']}\n"
        f"Plan: {dumps(state.get('plan'))}\n"
        f"Features: {dumps(state.get('features'))}\n"
        "Produce architecture JSON including mermaid."
    )
    arch = await invoke_structured(ArchitectureOutput, system, user, model=settings.heavy_model)
    return {
        "architecture": dump(arch),
        "current_step": "architecture",
        "status": "running",
    }
