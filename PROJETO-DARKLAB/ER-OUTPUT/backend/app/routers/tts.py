import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.database import get_db
from backend.app.models import User, ScriptProject, TokenWallet, TokenTransaction, VoiceGeneration
from backend.app.schemas import VoiceGenerateRequest, VoiceResponse, DirectSynthesizeRequest
from backend.app.adapters.tts_adapter import MockTTSAdapter
from backend.app.auth import get_current_user

router = APIRouter(prefix="/api/tts", tags=["Narração com IA (TTS)"])
tts_adapter = MockTTSAdapter()

@router.post("/generate-voice", response_model=VoiceResponse, status_code=status.HTTP_201_CREATED)
async def generate_voice(
    req: VoiceGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Busca o roteiro
    stmt = select(ScriptProject).where(
        ScriptProject.id == req.script_id,
        ScriptProject.workspace_id == current_user.workspace_id
    )
    script = (await db.execute(stmt)).scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Roteiro não encontrado.")

    # 2. Calcula quantidade de caracteres do texto
    char_count = len(script.full_script)
    tokens_required = char_count # 1 token = 1 caractere

    # 3. Trava e valida saldo na carteira
    stmt_wallet = select(TokenWallet).where(TokenWallet.workspace_id == current_user.workspace_id).with_for_update()
    wallet = (await db.execute(stmt_wallet)).scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Carteira de tokens não encontrada.")

    total_available = wallet.plan_balance + wallet.extra_balance
    if total_available < tokens_required:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Disponível: {total_available} tokens, Necessário: {tokens_required} tokens."
        )

    # 4. Debita atomicamente da carteira
    if wallet.plan_balance >= tokens_required:
        wallet.plan_balance -= tokens_required
    else:
        remaining = tokens_required - wallet.plan_balance
        wallet.plan_balance = 0
        wallet.extra_balance -= remaining

    balance_after = wallet.plan_balance + wallet.extra_balance

    # 5. Registra a transação no ledger
    tx = TokenTransaction(
        wallet_id=wallet.id,
        amount=-tokens_required,
        balance_after=balance_after,
        transaction_type="voice_tts",
        description=f"Narração do roteiro '{script.title}' ({char_count} caracteres)"
    )
    db.add(tx)

    # 6. Sintetiza o áudio real com o adaptador
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    static_base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(curr_dir))), "static", "audio")
    output_dir = static_base
    os.makedirs(output_dir, exist_ok=True)
    audio_filename = f"voice_{script.id}_{int(balance_after)}.wav"
    output_path = os.path.join(output_dir, audio_filename)

    synth_res = tts_adapter.synthesize_speech(
        text=script.full_script,
        voice_name=req.voice_name or "Marcus (Tensão/Mistério)",
        output_path=output_path
    )

    # 7. Salva o registro de áudio
    voice_gen = VoiceGeneration(
        script_id=script.id,
        voice_name=req.voice_name or "Marcus (Tensão/Mistério)",
        characters_count=char_count,
        tokens_debited=tokens_required,
        duration_seconds=synth_res["duration_seconds"],
        audio_path=f"/static/audio/{audio_filename}"
    )
    db.add(voice_gen)
    script.status = "voiced"

    await db.commit()
    await db.refresh(voice_gen)

    return VoiceResponse(
        id=voice_gen.id,
        script_id=script.id,
        voice_name=voice_gen.voice_name,
        characters_count=char_count,
        tokens_debited=tokens_required,
        duration_seconds=voice_gen.duration_seconds,
        audio_url=voice_gen.audio_path,
        remaining_balance=balance_after
    )

@router.post("/synthesize")
async def direct_synthesize(req: DirectSynthesizeRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    text = req.text or "Voz gerada com sucesso pela DarkLAB AI Studio."
    voice_name = req.voice_id or "Marcus (Sombrio)"
    char_count = len(text)

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    static_base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(curr_dir))), "static", "audio")
    output_dir = static_base
    os.makedirs(output_dir, exist_ok=True)
    import time
    audio_filename = f"synth_{int(time.time())}.wav"
    output_path = os.path.join(output_dir, audio_filename)

    synth_res = tts_adapter.synthesize_speech(
        text=text,
        voice_name=voice_name,
        output_path=output_path
    )

    return {
        "status": "success",
        "audio_url": f"/static/audio/{audio_filename}",
        "duration_seconds": synth_res.get("duration_seconds", 5),
        "characters_count": char_count,
        "voice": voice_name
    }

