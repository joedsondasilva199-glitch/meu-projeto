import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, Float, BigInteger, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    plan_tier = Column(String(50), default="start") # start, plus, max
    created_at = Column(DateTime, default=get_utc_now)

    users = relationship("User", back_populates="workspace", cascade="all, delete-orphan")
    wallet = relationship("TokenWallet", back_populates="workspace", uselist=False, cascade="all, delete-orphan")
    channels = relationship("YouTubeChannel", back_populates="workspace", cascade="all, delete-orphan")
    scripts = relationship("ScriptProject", back_populates="workspace", cascade="all, delete-orphan")
    characters = relationship("CharacterProfile", back_populates="workspace", cascade="all, delete-orphan")
    kanban_cards = relationship("KanbanCard", back_populates="workspace", cascade="all, delete-orphan")
    media_assets = relationship("MediaAsset", back_populates="workspace", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="owner") # owner, editor, viewer
    created_at = Column(DateTime, default=get_utc_now)

    workspace = relationship("Workspace", back_populates="users")

class TokenWallet(Base):
    __tablename__ = "token_wallets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), unique=True, nullable=False)
    plan_balance = Column(BigInteger, default=100000) # Saldo mensal de caracteres
    extra_balance = Column(BigInteger, default=0)     # Saldo avulso que nunca expira
    renewal_date = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    workspace = relationship("Workspace", back_populates="wallet")
    transactions = relationship("TokenTransaction", back_populates="wallet", cascade="all, delete-orphan")

class TokenTransaction(Base):
    __tablename__ = "token_transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    wallet_id = Column(String(36), ForeignKey("token_wallets.id"), nullable=False)
    amount = Column(BigInteger, nullable=False) # Negativo para débito, positivo para recarga
    balance_after = Column(BigInteger, nullable=False)
    transaction_type = Column(String(50), nullable=False) # voice_tts, plan_renewal, extra_purchase
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=get_utc_now)

    wallet = relationship("TokenWallet", back_populates="transactions")

class YouTubeChannel(Base):
    __tablename__ = "youtube_channels"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    channel_id = Column(String(100), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    niche = Column(String(100), nullable=False)
    subscribers = Column(BigInteger, default=0)
    total_views = Column(BigInteger, default=0)
    video_count = Column(Integer, default=0)
    is_monetized = Column(Boolean, default=True)
    outlier_score = Column(Float, default=1.0)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    workspace = relationship("Workspace", back_populates="channels")

class ScriptProject(Base):
    __tablename__ = "script_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    title = Column(String(255), nullable=False)
    niche = Column(String(100), nullable=False)
    language = Column(String(10), default="pt-BR")
    hook_text = Column(Text, nullable=True)      # Gancho dos primeiros 30s
    open_loop = Column(Text, nullable=True)      # Retenção e curiosidade
    body_text = Column(Text, nullable=True)      # Desenvolvimento POV
    cta_text = Column(Text, nullable=True)       # Chamada para ação final
    full_script = Column(Text, nullable=False)   # Roteiro concatenado completo
    status = Column(String(50), default="draft") # draft, voiced, ready
    created_at = Column(DateTime, default=get_utc_now)

    workspace = relationship("Workspace", back_populates="scripts")
    voices = relationship("VoiceGeneration", back_populates="script", cascade="all, delete-orphan")
    scenes = relationship("StoryboardScene", back_populates="script", cascade="all, delete-orphan")

class VoiceGeneration(Base):
    __tablename__ = "voice_generations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    script_id = Column(String(36), ForeignKey("script_projects.id"), nullable=False)
    voice_name = Column(String(100), default="Marcus (Tensão/Mistério)")
    characters_count = Column(Integer, nullable=False)
    tokens_debited = Column(BigInteger, nullable=False)
    duration_seconds = Column(Float, default=0.0)
    audio_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=get_utc_now)

    script = relationship("ScriptProject", back_populates="voices")

class StoryboardScene(Base):
    __tablename__ = "storyboard_scenes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    script_id = Column(String(36), ForeignKey("script_projects.id"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    start_time = Column(Float, default=0.0)
    end_time = Column(Float, default=0.0)
    narration_chunk = Column(Text, nullable=False)
    visual_prompt = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    character_name = Column(String(100), nullable=True)

    script = relationship("ScriptProject", back_populates="scenes")

class CharacterProfile(Base):
    __tablename__ = "character_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    trigger_words = Column(String(255), nullable=True)
    reference_image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    workspace = relationship("Workspace", back_populates="characters")

class KanbanCard(Base):
    __tablename__ = "kanban_cards"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    script_id = Column(String(36), ForeignKey("script_projects.id"), nullable=True)
    title = Column(String(255), nullable=False)
    column_status = Column(String(50), default="ideia") # ideia, roteiro, narracao, cenas, edicao, concluido
    position_order = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    workspace = relationship("Workspace", back_populates="kanban_cards")

class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    media_type = Column(String(50), nullable=False) # music, sfx, image, video
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(BigInteger, default=0)
    created_at = Column(DateTime, default=get_utc_now)

    workspace = relationship("Workspace", back_populates="media_assets")
