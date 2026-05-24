from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.services.card_generator import generate_card_from_image


router = APIRouter(prefix="/api", tags=["cards"])


@router.post("/cards/generate")
async def generate_card(image: UploadFile = File(...), hint: str = Form("")):
    raw = await image.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Missing image content")
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Image is too large")
    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    try:
        return generate_card_from_image(raw, image.content_type or "image/jpeg", hint)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
