from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.database import get_db
from backend.app.models import User, TokenWallet, TokenTransaction
from backend.app.schemas import TokenBalanceResponse, TokenDebitRequest, TokenTransactionResponse
from backend.app.auth import get_current_user

router = APIRouter(prefix="/api/tokens", tags=["Carteira & Tokens de Voz"])

@router.get("/balance", response_model=TokenBalanceResponse)
async def get_balance(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(TokenWallet).where(TokenWallet.workspace_id == current_user.workspace_id)
    wallet = (await db.execute(stmt)).scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Carteira de tokens não encontrada.")

    return TokenBalanceResponse(
        workspace_id=wallet.workspace_id,
        plan_balance=wallet.plan_balance,
        extra_balance=wallet.extra_balance,
        total_balance=wallet.plan_balance + wallet.extra_balance,
        renewal_date=wallet.renewal_date
    )

@router.post("/debit", response_model=TokenTransactionResponse)
async def debit_tokens(
    debit_in: TokenDebitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(TokenWallet).where(TokenWallet.workspace_id == current_user.workspace_id).with_for_update()
    wallet = (await db.execute(stmt)).scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Carteira de tokens não encontrada.")

    total_available = wallet.plan_balance + wallet.extra_balance
    required = debit_in.characters_count

    if total_available < required:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente de tokens. Disponível: {total_available}, Necessário: {required}."
        )

    # Regra de débito: consome primeiro o saldo do plano (que expira todo mês) e depois o avulso
    if wallet.plan_balance >= required:
        wallet.plan_balance -= required
    else:
        remaining_needed = required - wallet.plan_balance
        wallet.plan_balance = 0
        wallet.extra_balance -= remaining_needed

    balance_after = wallet.plan_balance + wallet.extra_balance

    # Registra a transação no ledger imutável
    tx = TokenTransaction(
        wallet_id=wallet.id,
        amount=-required,
        balance_after=balance_after,
        transaction_type="voice_tts",
        description=debit_in.description
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)

    return TokenTransactionResponse(
        id=tx.id,
        amount=tx.amount,
        balance_after=tx.balance_after,
        transaction_type=tx.transaction_type,
        description=tx.description,
        created_at=tx.created_at
    )
