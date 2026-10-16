from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from backend.app.database import get_db
from backend.app.models import User, ScriptProject, StoryboardScene, CharacterProfile
from backend.app.schemas import (
    AutoStoryboardRequest, StoryboardResponse, StoryboardSceneItem,
    SRTResponse, CharacterCreate, CharacterResponse
)
from backend.app.auth import get_current_user

router = APIRouter(prefix="/api/storyboard", tags=["Produção & Storyboard"])

def format_timestamp_srt(seconds: float) -> str:
    millis = int((seconds - int(seconds)) * 1000)
    secs = int(seconds) % 60
    mins = (int(seconds) // 60) % 60
    hours = int(seconds) // 3600
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"

@router.post("/auto-scenes", response_model=StoryboardResponse, status_code=status.HTTP_201_CREATED)
async def auto_generate_scenes(
    req: AutoStoryboardRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ScriptProject).where(
        ScriptProject.id == req.script_id,
        ScriptProject.workspace_id == current_user.workspace_id
    )
    script = (await db.execute(stmt)).scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Roteiro não encontrado.")

    # Remove cenas anteriores se existirem
    delete_stmt = select(StoryboardScene).where(StoryboardScene.script_id == script.id)
    old_scenes = (await db.execute(delete_stmt)).scalars().all()
    for sc in old_scenes:
        await db.delete(sc)

    # Quebra o roteiro em frases/blocos
    raw_sentences = [s.strip() for s in script.full_script.replace("\n", " ").split(".") if len(s.strip()) > 10]
    if not raw_sentences:
        raw_sentences = ["Cena inicial de abertura misteriosa", "Desenvolvimento dramático", "Clímax da narrativa"]

    sec_per_scene = req.seconds_per_scene or 4
    current_time = 0.0
    created_scenes = []

    for idx, sentence in enumerate(raw_sentences, start=1):
        start_t = current_time
        end_t = round(start_t + sec_per_scene, 2)
        current_time = end_t

        visual_prompt = (
            f"Cinematic 8k film still, dramatic chiaroscuro lighting, dark atmospheric tone, "
            f"scene depicting: '{sentence[:80]}', ultra-realistic 35mm photograph, octane render."
        )

        scene = StoryboardScene(
            script_id=script.id,
            scene_number=idx,
            start_time=start_t,
            end_time=end_t,
            narration_chunk=sentence,
            visual_prompt=visual_prompt,
            image_url=f"/static/previews/scene_{idx}.webp",
            character_name="Investigador Principal"
        )
        db.add(scene)
        created_scenes.append(scene)

    await db.commit()

    return StoryboardResponse(
        script_id=script.id,
        total_scenes=len(created_scenes),
        scenes=[
            StoryboardSceneItem(
                scene_number=sc.scene_number,
                start_time=sc.start_time,
                end_time=sc.end_time,
                narration_chunk=sc.narration_chunk,
                visual_prompt=sc.visual_prompt,
                image_url=sc.image_url,
                character_name=sc.character_name
            )
            for sc in created_scenes
        ]
    )

@router.get("/{script_id}/srt", response_model=SRTResponse)
async def get_srt_subtitles(
    script_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StoryboardScene).where(StoryboardScene.script_id == script_id).order_by(StoryboardScene.scene_number)
    scenes = (await db.execute(stmt)).scalars().all()
    if not scenes:
        raise HTTPException(status_code=404, detail="Nenhuma cena gerada para este roteiro.")

    srt_lines = []
    for idx, sc in enumerate(scenes, start=1):
        t_start = format_timestamp_srt(sc.start_time)
        t_end = format_timestamp_srt(sc.end_time)
        srt_lines.append(f"{idx}\n{t_start} --> {t_end}\n{sc.narration_chunk}\n")

    return SRTResponse(
        script_id=script_id,
        srt_content="\n".join(srt_lines)
    )

@router.get("/characters", response_model=List[CharacterResponse])
async def list_characters(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(CharacterProfile).where(CharacterProfile.workspace_id == current_user.workspace_id)
    chars = (await db.execute(stmt)).scalars().all()
    return [
        CharacterResponse(
            id=c.id,
            name=c.name,
            description=c.description,
            trigger_words=c.trigger_words,
            reference_image_url=c.reference_image_url
        )
        for c in chars
    ]

@router.post("/characters", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    char_in: CharacterCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    char = CharacterProfile(
        workspace_id=current_user.workspace_id,
        name=char_in.name,
        description=char_in.description,
        trigger_words=char_in.trigger_words,
        reference_image_url=char_in.reference_image_url
    )
    db.add(char)
    await db.commit()
    await db.refresh(char)
    return CharacterResponse(
        id=char.id,
        name=char.name,
        description=char.description,
        trigger_words=char.trigger_words,
        reference_image_url=char.reference_image_url
    )
