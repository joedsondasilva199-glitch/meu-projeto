from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from backend.app.database import get_db
from backend.app.models import User, ScriptProject
from backend.app.schemas import ScriptCreateRequest, ScriptResponse
from backend.app.adapters.llm_adapter import MockLLMAdapter
from backend.app.auth import get_current_user

router = APIRouter(prefix="/api/scripts", tags=["Roteiros com IA"])
llm = MockLLMAdapter()

@router.post("/generate", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def generate_script(
    req: ScriptCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Gera o roteiro estruturado com gancho de retenção
    gen = llm.generate_retention_script(
        title=req.title,
        niche=req.niche,
        topic=req.topic_description,
        formula_style=req.formula_style
    )

    script = ScriptProject(
        workspace_id=current_user.workspace_id,
        title=req.title,
        niche=req.niche,
        language="pt-BR",
        hook_text=gen["hook_text"],
        open_loop=gen["open_loop"],
        body_text=gen["body_text"],
        cta_text=gen["cta_text"],
        full_script=gen["full_script"],
        status="draft"
    )
    db.add(script)
    await db.commit()
    await db.refresh(script)

    char_count = len(script.full_script)
    return ScriptResponse(
        id=script.id,
        title=script.title,
        niche=script.niche,
        hook_text=script.hook_text,
        open_loop=script.open_loop,
        body_text=script.body_text,
        cta_text=script.cta_text,
        full_script=script.full_script,
        character_count=char_count,
        estimated_audio_tokens=char_count
    )

@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ScriptProject).where(
        ScriptProject.id == script_id,
        ScriptProject.workspace_id == current_user.workspace_id
    )
    script = (await db.execute(stmt)).scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Roteiro não encontrado.")

    char_count = len(script.full_script)
    return ScriptResponse(
        id=script.id,
        title=script.title,
        niche=script.niche,
        hook_text=script.hook_text,
        open_loop=script.open_loop,
        body_text=script.body_text,
        cta_text=script.cta_text,
        full_script=script.full_script,
        character_count=char_count,
        estimated_audio_tokens=char_count
    )

@router.get("/{script_id}/export")
async def export_script(
    script_id: str,
    format: str = "markdown",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Nova Funcionalidade 1: Exportador multi-formato para Teleprompter e OBS Studio."""
    stmt = select(ScriptProject).where(
        ScriptProject.id == script_id,
        ScriptProject.workspace_id == current_user.workspace_id
    )
    script = (await db.execute(stmt)).scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Roteiro não encontrado.")

    if format == "teleprompter":
        text = f"=== {script.title.upper()} ===\n\n[GANCHO 30S]\n{script.hook_text}\n\n[LOOP ABERTO]\n{script.open_loop}\n\n[HISTÓRIA]\n{script.body_text}\n\n[CHAMADA PARA AÇÃO]\n{script.cta_text}"
        return {"format": "teleprompter", "content": text}
    elif format == "json":
        return {
            "title": script.title,
            "niche": script.niche,
            "blocks": {
                "hook": script.hook_text,
                "open_loop": script.open_loop,
                "body": script.body_text,
                "cta": script.cta_text
            }
        }
    else: # markdown
        md = f"# {script.title}\n\n**Nicho:** `{script.niche}` | **Status:** `{script.status}`\n\n## 1. Gancho Inicial (0-30s)\n> {script.hook_text}\n\n## 2. Loop Aberto\n{script.open_loop}\n\n## 3. Desenvolvimento / Corpo\n{script.body_text}\n\n## 4. CTA / Finalização\n{script.cta_text}\n"
        return {"format": "markdown", "content": md}

