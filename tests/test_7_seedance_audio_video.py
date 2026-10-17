#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
TESTE 7: SEEDANCE 2.5 — VÍDEO AUDIO-DRIVEN (MULTITALK / FANTASY-TALKING)
7º Especialista: Geração de Vídeo Multi-Personagens Condicionada por Áudio.
================================================================================
"""

import os
import sys
import time
import subprocess
import torch

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_locator import find_model_path
from vram_manager import VRAMManager

OUTPUT_DIR = os.path.abspath("outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_test():
    print("=" * 70)
    print("🎬 INICIANDO TESTE 7: SEEDANCE 2.5 (VÍDEO CONDICIONADO POR ÁUDIO)")
    print("🎯 7º Especialista: Multi-Personagens com Voice Map e Clímax com Criatura")
    print("=" * 70)

    VRAMManager.audit("Pré-Carregamento Seedance 2.5")

    # Importa e roda o pipeline modular do Seedance 2.5
    sys.path.insert(0, os.path.abspath("Scripts"))
    from stage1_seed_audio import run_stage_seed_audio
    from stage2_audio_enhance import run_stage_audio_enhance
    from stage3_character_sheets import run_stage_character_sheets
    from stage4_audio_driven_video import run_stage_audio_driven_video
    from stage5_upscale_project import run_stage_upscale

    start_time = time.time()
    
    # 1. Áudio Multi-Voz
    print("\n -> [1/5] Gerando Diálogo Multi-Personagens...")
    raw_audio, timeline = run_stage_seed_audio()

    # 2. Restauração Acústica
    print("\n -> [2/5] Restaurando Áudio com Studio DSP...")
    enhanced_audio = run_stage_audio_enhance(raw_audio)

    # 3. Composição Cênica
    print("\n -> [3/5] Compondo Character Sheets...")
    base_shot, climax_shot = run_stage_character_sheets()

    # 4. Difusão de Vídeo Guiada pela Voz
    print("\n -> [4/5] Renderizando Vídeo 480p Draft Audio-Driven...")
    draft_mp4 = run_stage_audio_driven_video(base_shot, climax_shot, enhanced_audio, timeline)

    # 5. Reconstrução 1080p
    print("\n -> [5/5] Reconstruindo Vídeo para 1080p Full HD...")
    final_1080p = run_stage_upscale(draft_mp4)

    out_file = os.path.join(OUTPUT_DIR, "test_7_video_seedance_1080p.mp4")
    import shutil
    shutil.copy2(final_1080p, out_file)

    elapsed = round(time.time() - start_time, 2)
    print(f"\n✅ TESTE 7 CONCLUÍDO COM SUCESSO EM {elapsed}s!")
    print(f"💾 Vídeo Final Seedance salvo em: {out_file} ({os.path.getsize(out_file)} bytes)")

    VRAMManager.purge()
    return out_file

if __name__ == "__main__":
    run_test()
