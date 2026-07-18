from app.config import get_settings
from app.graph.llm import dump, dumps, invoke_structured
from app.graph.state import CTOState
from app.schemas.artifacts import APIOutput


async def api_generator_node(state: CTOState) -> dict:
    settings = get_settings()
    system = (
        "You are an API designer. Generate REST endpoints that map cleanly to the database "
        "entities and MVP features. Use clear resource paths and include request/response shapes."
    )
    user = (
        f"Idea: {state['idea']}\n"
        f"Features: {dumps(state.get('features'))}\n"
        f"Database: {dumps(state.get('database_schema'))}\n"
        "Produce API endpoints."
    )
    api = await invoke_structured(APIOutput, system, user, model=settings.heavy_model)
    return {
        "api_endpoints": [dump(e) for e in api.endpoints],
        "api_notes": api.notes,
        "current_step": "api",
        "status": "running",
    }
