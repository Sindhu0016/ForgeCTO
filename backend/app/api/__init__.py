from fastapi import APIRouter

from app.api.routes_chat import router as chat_router
from app.api.routes_export import router as export_router
from app.api.routes_projects import router as projects_router

api_router = APIRouter()
api_router.include_router(projects_router)
api_router.include_router(export_router)
api_router.include_router(chat_router)
