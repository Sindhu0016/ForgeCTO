from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    api_generator_node,
    architecture_node,
    aws_node,
    critic_node,
    database_node,
    documentation_node,
    planner_node,
    research_node,
    review_board_node,
)
from app.graph.state import CTOState

# Node names must not collide with CTOState keys
PIPELINE_STEPS = [
    "planner",
    "research",
    "architecture",
    "database",
    "api",
    "aws",
    "documentation",
    "critic",
    "review_board",
]

NODE_PLANNER = "planner_agent"
NODE_RESEARCH = "research_agent"
NODE_ARCHITECTURE = "architecture_agent"
NODE_DATABASE = "database_agent"
NODE_API = "api_agent"
NODE_AWS = "aws_agent"
NODE_DOCS = "documentation_agent"
NODE_CRITIC = "critic_agent"
NODE_REVIEW = "review_board_agent"


def build_graph():
    graph = StateGraph(CTOState)
    graph.add_node(NODE_PLANNER, planner_node)
    graph.add_node(NODE_RESEARCH, research_node)
    graph.add_node(NODE_ARCHITECTURE, architecture_node)
    graph.add_node(NODE_DATABASE, database_node)
    graph.add_node(NODE_API, api_generator_node)
    graph.add_node(NODE_AWS, aws_node)
    graph.add_node(NODE_DOCS, documentation_node)
    graph.add_node(NODE_CRITIC, critic_node)
    graph.add_node(NODE_REVIEW, review_board_node)

    graph.add_edge(START, NODE_PLANNER)
    graph.add_edge(NODE_PLANNER, NODE_RESEARCH)
    graph.add_edge(NODE_RESEARCH, NODE_ARCHITECTURE)
    graph.add_edge(NODE_ARCHITECTURE, NODE_DATABASE)
    graph.add_edge(NODE_DATABASE, NODE_API)
    graph.add_edge(NODE_API, NODE_AWS)
    graph.add_edge(NODE_AWS, NODE_DOCS)
    graph.add_edge(NODE_DOCS, NODE_CRITIC)
    graph.add_edge(NODE_CRITIC, NODE_REVIEW)
    graph.add_edge(NODE_REVIEW, END)

    return graph.compile()


cto_graph = build_graph()
