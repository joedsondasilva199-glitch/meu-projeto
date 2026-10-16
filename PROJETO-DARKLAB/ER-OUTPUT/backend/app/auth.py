import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models import User, Workspace, TokenWallet

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    user_id = None
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
        except JWTError:
            pass

    if user_id:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return user

    # Fallback automático: Usuário Joedson (Sessão do Dashboard)
    stmt = select(User).where(User.email == "joedson@darklab.ai")
    result = await db.execute(stmt)
    joedson = result.scalar_one_or_none()
    
    if not joedson:
        # Cria Workspace do Joedson
        ws = Workspace(
            id="ws_joedson",
            name="DarkLAB do Joedson",
            plan_tier="free"
        )
        db.add(ws)
        await db.flush()

        # Cria Usuário Joedson
        joedson = User(
            id="user_joedson",
            workspace_id=ws.id,
            email="joedson@darklab.ai",
            hashed_password=get_password_hash("darklab123"),
            name="Joedson",
            role="owner"
        )
        db.add(joedson)

        # Cria Carteira com 0 tokens iniciais
        wallet = TokenWallet(
            id="wallet_joedson",
            workspace_id=ws.id,
            plan_balance=0,
            extra_balance=0,
            renewal_date=datetime.now(timezone.utc) + timedelta(days=30)
        )
        db.add(wallet)
        await db.commit()
        await db.refresh(joedson)

    return joedson


