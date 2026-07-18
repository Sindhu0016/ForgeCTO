from fastapi import APIRouter, HTTPException, Request

from app.config import get_settings
from app.schemas.api import GeneralChatRequest, GeneralChatResponse
from app.services.general_chat import HistoryTurn, answer_general_question
from app.services.rate_limit import rate_limiter

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=GeneralChatResponse)
async def general_chat(body: GeneralChatRequest, request: Request) -> GeneralChatResponse:
    settings = get_settings()
    rate_limiter.max_per_minute = settings.rate_limit_per_minute
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again shortly.")

    history = [HistoryTurn(role=h.role, content=h.content) for h in body.history[-8:]]
    answer = await answer_general_question(body.message.strip(), history)
    return GeneralChatResponse(reply=answer.reply)
