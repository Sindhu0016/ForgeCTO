from app.config import get_settings
from app.graph.llm import dump, dumps, invoke_structured
from app.graph.state import CTOState
from app.schemas.artifacts import DocumentationOutput


async def documentation_node(state: CTOState) -> dict:
    settings = get_settings()
    system = (
        "You are a startup technical program manager and CTO advisor. "
        "Produce cost estimates, a phased roadmap, 2-week sprint plans, GitHub issue drafts, "
        "and a comprehensive markdown document founders can share with engineers."
    )
    user = (
        f"Idea: {state['idea']}\n"
        f"Plan: {dumps(state.get('plan'))}\n"
        f"Research: {dumps(state.get('market_research'))}\n"
        f"Features: {dumps(state.get('features'))}\n"
        f"Architecture: {dumps(state.get('architecture'))}\n"
        f"Database: {dumps(state.get('database_schema'))}\n"
        f"APIs: {dumps(state.get('api_endpoints'))}\n"
        f"AWS: {dumps(state.get('aws_design'))}\n"
        "Produce documentation pack."
    )
    docs = await invoke_structured(DocumentationOutput, system, user, model=settings.docs_model)
    return {
        "cost_estimate": dump(docs.cost_estimate),
        "roadmap": [dump(r) for r in docs.roadmap],
        "sprint_plan": [dump(s) for s in docs.sprint_plan],
        "github_issues": [dump(i) for i in docs.github_issues],
        "docs_markdown": docs.docs_markdown,
        "current_step": "documentation",
        "status": "running",
    }
