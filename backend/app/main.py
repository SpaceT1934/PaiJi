from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.cards import router as cards_router
from app.core.config import settings


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "ok": True,
        "model": settings.model,
        "defaultVisionModel": settings.default_vision_model,
        "mockAi": settings.mock_ai,
    }


app.include_router(cards_router)
