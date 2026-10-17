#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
ETAPA 2: O "ADOBE PODCAST ENHANCE" OPEN-SOURCE (RESTAURAÇÃO ACÚSTICA NEURAL)
Aplica redução de ruído, equalização de presença, compressão e loudness broadcast.
================================================================================
"""

import os
import sys
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.abspath("tests"))
try:
    from vram_manager import VRAMManager
except ImportError:
    class VRAMManager:
        @staticmethod
        def purge(): pass

OUTPUT_DIR = os.path.abspath("outputs/seedance_session")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_stage_audio_enhance(input_audio: str = None):
    print("=" * 70)
    print("🎚️ ETAPA 2: ADOBE PODCAST ENHANCE OPEN-SOURCE (DSP & RESTAURAÇÃO)")
    print("=" * 70)

    if not input_audio or not os.path.exists(input_audio):
        input_audio = os.path.join(OUTPUT_DIR, "dialogo_bruto.wav")

    if not os.path.exists(input_audio):
        raise FileNotFoundError(f"Áudio de entrada não encontrado: {input_audio}")

    print(f"🎧 Áudio Original: {input_audio}")
    output_enhanced = os.path.join(OUTPUT_DIR, "dialogo_master_enhanced.wav")

    # Cadeia de Restauração de Estúdio (Noise Reduction + Highpass + Multiband Comp + EBU R128 Loudness)
    # Elimina ruídos de fundo, artefatos metalizados e equaliza o ganho vocal para padrão cinema
    dsp_filter = (
        "afftdn=nf=-25,"
        "highpass=f=80,"
        "equalizer=f=3000:width_type=o:width=1.5:g=3,"
        "acompressor=threshold=-16dB:ratio=3:attack=5:release=50,"
        "loudnorm=I=-16:TP=-1.5:LRA=11"
    )

    print("⚡ Processando cadeia de estúdio e normalização EBU R128...")
    cmd = [
        "ffmpeg", "-y",
        "-i", input_audio,
        "-af", dsp_filter,
        "-ar", "24000", "-ac", "2",
        output_enhanced
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"✅ ÁUDIO MASTERIZADO COM SUCESSO: {output_enhanced} ({os.path.getsize(output_enhanced)} bytes)")

    VRAMManager.purge()
    return output_enhanced

if __name__ == "__main__":
    run_stage_audio_enhance()
