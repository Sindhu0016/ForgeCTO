from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages


class CTOState(TypedDict, total=False):
    idea: str
    project_id: str
    plan: dict[str, Any]
    market_research: dict[str, Any]
    competitors: list[dict[str, Any]]
    features: list[dict[str, Any]]
    architecture: dict[str, Any]
    database_schema: dict[str, Any]
    api_endpoints: list[dict[str, Any]]
    api_notes: str
    aws_design: dict[str, Any]
    cost_estimate: dict[str, Any]
    roadmap: list[dict[str, Any]]
    sprint_plan: list[dict[str, Any]]
    github_issues: list[dict[str, Any]]
    docs_markdown: str
    critic_review: dict[str, Any]
    review_board: dict[str, Any]
    current_step: str
    status: str
    errors: list[str]
    messages: Annotated[list, add_messages]
