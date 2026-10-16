from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from backend.app.database import get_db
from backend.app.models import User, KanbanCard
from backend.app.schemas import KanbanCardCreate, KanbanCardMove, KanbanCardResponse
from backend.app.auth import get_current_user

router = APIRouter(prefix="/api/kanban", tags=["Pipeline Kanban (Organizar)"])

VALID_COLUMNS = ["ideia", "ideias", "roteiro", "narracao", "audio", "cenas", "edicao", "publicado", "concluido"]

@router.get("/board")
async def get_board(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(KanbanCard).where(
        KanbanCard.workspace_id == current_user.workspace_id
    ).order_by(KanbanCard.position_order)
    cards = (await db.execute(stmt)).scalars().all()

    # Agrupa por colunas
    board: Dict[str, List[Any]] = {col: [] for col in VALID_COLUMNS}
    for card in cards:
        col = card.column_status if card.column_status in board else "ideia"
        board[col].append({
            "id": card.id,
            "title": card.title,
            "column_status": card.column_status,
            "position_order": card.position_order,
            "script_id": card.script_id,
            "notes": card.notes,
            "updated_at": card.updated_at
        })
    # Retorna tanto em formato 'columns' quanto chave direta para compatibilidade universal
    return {
        "columns": board,
        **board
    }

@router.post("/cards", response_model=KanbanCardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(
    card_in: KanbanCardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    col = card_in.column_status if card_in.column_status in VALID_COLUMNS else "ideia"
    card = KanbanCard(
        workspace_id=current_user.workspace_id,
        title=card_in.title,
        column_status=col,
        script_id=card_in.script_id,
        notes=card_in.notes
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return KanbanCardResponse(
        id=card.id,
        title=card.title,
        column_status=card.column_status,
        position_order=card.position_order,
        script_id=card.script_id,
        notes=card.notes,
        updated_at=card.updated_at
    )

@router.put("/cards/{card_id}/move", response_model=KanbanCardResponse)
async def move_card(
    card_id: str,
    move_in: KanbanCardMove,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if move_in.column_status not in VALID_COLUMNS:
        raise HTTPException(status_code=400, detail=f"Coluna inválida. Permitidas: {VALID_COLUMNS}")

    stmt = select(KanbanCard).where(
        KanbanCard.id == card_id,
        KanbanCard.workspace_id == current_user.workspace_id
    )
    card = (await db.execute(stmt)).scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card do Kanban não encontrado.")

    card.column_status = move_in.column_status
    card.position_order = move_in.position_order or 0
    await db.commit()
    await db.refresh(card)

    return KanbanCardResponse(
        id=card.id,
        title=card.title,
        column_status=card.column_status,
        position_order=card.position_order,
        script_id=card.script_id,
        notes=card.notes,
        updated_at=card.updated_at
    )

@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(KanbanCard).where(
        KanbanCard.id == card_id,
        KanbanCard.workspace_id == current_user.workspace_id
    )
    card = (await db.execute(stmt)).scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card do Kanban não encontrado.")

    await db.delete(card)
    await db.commit()
    return None
