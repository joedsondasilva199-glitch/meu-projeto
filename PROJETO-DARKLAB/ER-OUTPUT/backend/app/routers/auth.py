from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from backend.app.database import get_db
from backend.app.models import User, Workspace, TokenWallet
from backend.app.schemas import UserRegister, UserLogin, TokenResponse, UserProfile
from backend.app.auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Autenticação & Workspace"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    # Verifica se e-mail já existe
    stmt = select(User).where(User.email == user_in.email)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado.")

    # Cria o Workspace
    workspace = Workspace(
        name=user_in.workspace_name or "Meu Estúdio Dark",
        plan_tier=user_in.plan_tier or "start"
    )
    db.add(workspace)
    await db.flush()

    # Cria a Carteira de Tokens com o saldo base do plano (Start = 100k, Plus = 250k, Max = 600k)
    initial_tokens = 100000
    if workspace.plan_tier == "plus":
        initial_tokens = 250000
    elif workspace.plan_tier == "max":
        initial_tokens = 600000

    wallet = TokenWallet(
        workspace_id=workspace.id,
        plan_balance=initial_tokens,
        extra_balance=0
    )
    db.add(wallet)

    # Cria o Usuário Proprietário (Owner)
    user = User(
        workspace_id=workspace.id,
        name=user_in.name,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role="owner"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(data={"sub": user.id, "email": user.email, "workspace_id": workspace.id})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        workspace_id=workspace.id,
        role=user.role
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == credentials.email)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")

    token = create_access_token(data={"sub": user.id, "email": user.email, "workspace_id": user.workspace_id})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        workspace_id=user.workspace_id,
        role=user.role
    )

@router.get("/me", response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Busca dados do workspace e wallet
    ws = (await db.execute(select(Workspace).where(Workspace.id == current_user.workspace_id))).scalar_one()
    wallet = (await db.execute(select(TokenWallet).where(TokenWallet.workspace_id == current_user.workspace_id))).scalar_one_or_none()

    total_tokens = (wallet.plan_balance + wallet.extra_balance) if wallet else 0

    return UserProfile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        workspace_id=ws.id,
        workspace_name=ws.name,
        plan_tier=ws.plan_tier,
        tokens_available=total_tokens
    )
