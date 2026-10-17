#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
ORQUESTRADOR MESTRE: PIPELINE SEED AUDIO + SEEDANCE 2.5 (32GB DUAL T4)
Executa a esteira aditiva de ponta a ponta com Hot-Swapping cirúrgico de VRAM:
Etapa 1: Seed Audio 1.0 (Clonagem Multi-Voz + voice_timeline.json)
Etapa 2: Adobe Podcast Enhance (Restauração Acústica DSP EBU R128)
Etapa 3: Compositor de Character Sheets (@imagem1, @imagem2, @imagem4)
Etapa 4: Seedance 2.5 (Vídeo Audio-Driven Wan 2.1 em 480p Draft)
Etapa 5: Reconstrução Super-Resolução 1080p Full HD
================================================================================
"""

import os
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stage1_seed_audio import run_stage_seed_audio
from stage2_audio_enhance import run_stage_audio_enhance
from stage3_character_sheets import run_stage_character_sheets
from stage4_audio_driven_video import run_stage_audio_driven_video
from stage5_upscale_project import run_stage_upscale

def main():
    start_time = time.time()
    print("=" * 75)
    print("🚀 INICIANDO PIPELINE MODULAR SEED AUDIO + SEEDANCE 2.5 (32GB VRAM)")
    print("=" * 75)

    # 1. Etapa 1: Seed Audio 1.0
    print("\n[PASSO 1/5] Executando Seed Audio 1.0...")
    dialogo_bruto, timeline_json = run_stage_seed_audio()

    # 2. Etapa 2: Adobe Podcast Enhance
    print("\n[PASSO 2/5] Executando Adobe Podcast Enhance...")
    audio_enhanced = run_stage_audio_enhance(dialogo_bruto)

    # 3. Etapa 3: Character Sheets
    print("\n[PASSO 3/5] Compondo Character Sheets...")
    quadro_base, quadro_climax = run_stage_character_sheets()

    # 4. Etapa 4: Seedance 2.5 Audio-Driven Video
    print("\n[PASSO 4/5] Renderizando Vídeo 480p Draft Audio-Driven...")
    draft_video = run_stage_audio_driven_video(quadro_base, quadro_climax, audio_enhanced, timeline_json)

    # 5. Etapa 5: Upscale 1080p
    print("\n[PASSO 5/5] Reconstruindo Vídeo para 1080p Full HD...")
    final_1080p = run_stage_upscale(draft_video)

    total_elapsed = round(time.time() - start_time, 1)
    print("\n" + "=" * 75)
    print(f"🎉 PIPELINE SEEDANCE 2.5 CONCLUÍDO COM SUCESSO EM {total_elapsed}s!")
    print(f"📁 Vídeo Draft (480p): {draft_video}")
    print(f"📁 Vídeo Final (1080p): {final_1080p}")
    print("=" * 75)

if __name__ == "__main__":
    main()
