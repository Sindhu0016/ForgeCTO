from app.config import get_settings
from app.graph.llm import dump, dumps, invoke_structured
from app.graph.state import CTOState
from app.schemas.artifacts import ResearchOutput
from app.tools.tavily_search import search_market


async def research_node(state: CTOState) -> dict:
    settings = get_settings()
    idea = state["idea"]
    plan = state.get("plan") or {}
    search_results = search_market(idea)
    system = (
        "You are a market research analyst for startups. "
        "Use the search snippets to identify competitors, opportunities, risks, and MVP features. "
        "Prioritize features as P0 (must-have MVP), P1, or P2."
    )
    user = (
        f"Idea: {idea}\n\nPlan:\n{dumps(plan)}\n\n"
        f"Search results:\n{dumps(search_results)}\n\n"
        "Synthesize structured market research."
    )
    research = await invoke_structured(ResearchOutput, system, user, model=settings.planner_model)
    return {
        "market_research": {
            "market_summary": research.market_summary,
            "market_size_notes": research.market_size_notes,
            "opportunities": research.opportunities,
            "risks": research.risks,
            "sources": research.sources or [r.get("url") for r in search_results if r.get("url")],
        },
        "competitors": [dump(c) for c in research.competitors],
        "features": [dump(f) for f in research.features],
        "current_step": "research",
        "status": "running",
    }
