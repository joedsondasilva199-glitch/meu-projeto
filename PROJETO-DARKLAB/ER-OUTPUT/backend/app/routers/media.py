from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from backend.app.database import get_db
from backend.app.models import User, MediaAsset
from backend.app.schemas import MediaAssetResponse
from backend.app.auth import get_current_user

router = APIRouter(prefix="/api/media", tags=["Biblioteca de Mídia"])

@router.get("/library", response_model=List[MediaAssetResponse])
async def list_media(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(MediaAsset).where(MediaAsset.workspace_id == current_user.workspace_id)
    assets = (await db.execute(stmt)).scalars().all()
    # Se a biblioteca estiver vazia, pré-carrega assets padrão livres de royalties
    if not assets:
        defaults = [
            MediaAsset(workspace_id=current_user.workspace_id, name="Trilha Suspense Sombrio (No Copyright)", media_type="music", file_path="/static/audio/dark_ambient_1.mp3", file_size_bytes=3400000),
            MediaAsset(workspace_id=current_user.workspace_id, name="SFX Batida de Porta Antiga", media_type="sfx", file_path="/static/audio/door_creak.mp3", file_size_bytes=120000),
            MediaAsset(workspace_id=current_user.workspace_id, name="SFX Sussurro Noturno", media_type="sfx", file_path="/static/audio/whisper_sfx.mp3", file_size_bytes=240000)
        ]
        db.add_all(defaults)
        await db.commit()
        assets = defaults

    return [
        MediaAssetResponse(
            id=a.id,
            name=a.name,
            media_type=a.media_type,
            file_path=a.file_path,
            file_size_bytes=a.file_size_bytes,
            created_at=a.created_at
        )
        for a in assets
    ]
