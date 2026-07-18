from app.config import get_settings
from app.graph.llm import dump, dumps, invoke_structured
from app.graph.state import CTOState
from app.schemas.artifacts import AWSOutput


async def aws_node(state: CTOState) -> dict:
    settings = get_settings()
    system = (
        "You are an AWS solutions architect. Propose a production-ready but cost-aware MVP "
        "deployment on AWS (VPC, ECS/Fargate or App Runner, RDS Postgres, S3, CloudFront, "
        "ALB, Secrets Manager as appropriate). Include Mermaid flowchart and monthly USD cost range."
    )
    user = (
        f"Idea: {state['idea']}\n"
        f"Architecture: {dumps(state.get('architecture'))}\n"
        f"Database: {dumps(state.get('database_schema'))}\n"
        "Produce AWS deployment design."
    )
    aws = await invoke_structured(AWSOutput, system, user, model=settings.heavy_model)
    return {
        "aws_design": dump(aws),
        "current_step": "aws",
        "status": "running",
    }
