from app.config import get_settings
from app.graph.llm import dump, dumps, invoke_structured
from app.graph.state import CTOState
from app.schemas.artifacts import DatabaseOutput


async def database_node(state: CTOState) -> dict:
    settings = get_settings()
    system = (
        "You are a senior database designer. Design a PostgreSQL schema for the MVP. "
        "Provide entities, relationships, CREATE TABLE DDL, and an ER Mermaid diagram "
        "(erDiagram syntax)."
    )
    user = (
        f"Idea: {state['idea']}\n"
        f"Features: {dumps(state.get('features'))}\n"
        f"Architecture: {dumps(state.get('architecture'))}\n"
        "Produce database design."
    )
    db = await invoke_structured(DatabaseOutput, system, user, model=settings.heavy_model)
    return {
        "database_schema": dump(db),
        "current_step": "database",
        "status": "running",
    }
