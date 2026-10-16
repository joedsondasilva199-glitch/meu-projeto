from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- HEALTH ---
class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    environment: str
    database: str

# --- AUTH & WORKSPACE ---
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    workspace_name: Optional[str] = "Meu Estúdio Dark"
    plan_tier: Optional[str] = "start"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    workspace_id: str
    role: str

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    role: str
    workspace_id: str
    workspace_name: str
    plan_tier: str
    tokens_available: int

# --- TOKENS ---
class TokenBalanceResponse(BaseModel):
    workspace_id: str
    plan_balance: int
    extra_balance: int
    total_balance: int
    renewal_date: datetime

class TokenDebitRequest(BaseModel):
    characters_count: int
    description: str

class TokenTransactionResponse(BaseModel):
    id: str
    amount: int
    balance_after: int
    transaction_type: str
    description: str
    created_at: datetime

# --- VIRAL LAB (NICHE FINDER & RAIO-X) ---
class NicheChannelItem(BaseModel):
    channel_id: str
    title: str
    niche: str
    subscribers: int
    views: int
    age_days: int
    outlier_score: float
    is_monetized: bool
    sparkline: List[float] = []

class VideoAnalysisRequest(BaseModel):
    url_or_id: str

class VideoAnalysisResponse(BaseModel):
    video_id: str
    title: str
    views: int
    estimated_vph: int # views por hora
    retention_score: float # 0 a 100
    hook_strength: str # Alta, Média, Baixa
    tags: List[str]
    is_monetized: bool
    summary: str

class ChannelAnalysisResponse(BaseModel):
    channel_id: str
    title: str
    niche: str
    subscribers: int
    video_frequency: str
    avg_duration_minutes: float
    estimated_monthly_revenue: float
    top_outlier_videos: List[Dict[str, Any]]

# --- ROTEIRIZADOR POV ---
class ScriptCreateRequest(BaseModel):
    title: str
    niche: str
    topic_description: str
    formula_style: Optional[str] = "pov_conflito" # pov_conflito, exilio_honra, rejeicao_reconhecimento
    target_duration_minutes: Optional[int] = 15

class ScriptResponse(BaseModel):
    id: str
    title: str
    niche: str
    hook_text: str
    open_loop: str
    body_text: str
    cta_text: str
    full_script: str
    character_count: int
    estimated_audio_tokens: int

# --- TTS & VOZ ---
class DirectSynthesizeRequest(BaseModel):
    text: str = "Voz gerada pela DarkLAB AI Studio."
    voice_id: Optional[str] = "marcus"
    user_id: Optional[str] = "joedson"

class VoiceGenerateRequest(BaseModel):
    script_id: str
    voice_name: Optional[str] = "Marcus (Tensão/Mistério)"

class VoiceResponse(BaseModel):
    id: str
    script_id: str
    voice_name: str
    characters_count: int
    tokens_debited: int
    duration_seconds: float
    audio_url: str
    remaining_balance: int

# --- STORYBOARD & CENAS ---
class AutoStoryboardRequest(BaseModel):
    script_id: str
    seconds_per_scene: Optional[int] = 4

class StoryboardSceneItem(BaseModel):
    scene_number: int
    start_time: float
    end_time: float
    narration_chunk: str
    visual_prompt: str
    image_url: str
    character_name: Optional[str] = None

class StoryboardResponse(BaseModel):
    script_id: str
    total_scenes: int
    scenes: List[StoryboardSceneItem]

class SRTResponse(BaseModel):
    script_id: str
    srt_content: str

# --- PERSONAGENS ---
class CharacterCreate(BaseModel):
    name: str
    description: str
    trigger_words: Optional[str] = None
    reference_image_url: Optional[str] = None

class CharacterResponse(BaseModel):
    id: str
    name: str
    description: str
    trigger_words: Optional[str] = None
    reference_image_url: Optional[str] = None

# --- KANBAN ---
class KanbanCardCreate(BaseModel):
    title: str
    column_status: Optional[str] = "ideia"
    script_id: Optional[str] = None
    notes: Optional[str] = None

class KanbanCardMove(BaseModel):
    column_status: str
    position_order: Optional[int] = 0

class KanbanCardResponse(BaseModel):
    id: str
    title: str
    column_status: str
    position_order: int
    script_id: Optional[str] = None
    notes: Optional[str] = None
    updated_at: datetime

# --- MIDIA ---
class MediaAssetResponse(BaseModel):
    id: str
    name: str
    media_type: str
    file_path: str
    file_size_bytes: int
    created_at: datetime
