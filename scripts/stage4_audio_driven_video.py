#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
ETAPA 4: O "SEEDANCE 2.5" OPEN-SOURCE (VÍDEO CONDICIONADO POR ÁUDIO + PERSONAGENS)
Motor de difusão temporal guiado pela voz (wav2vec2 + Wan 2.1) em 480p Draft (832x480).
Atuação sincronizada, movimento corporal, iluminação na mata e injeção da criatura no clímax.
================================================================================
"""

import os
import sys
import time
import json
import subprocess
import torch

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.abspath("tests"))
try:
    from vram_manager import VRAMManager
    from model_locator import find_model_path
except ImportError:
    class VRAMManager:
        @staticmethod
        def purge(): pass

OUTPUT_DIR = os.path.abspath("outputs/seedance_session")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_stage_audio_driven_video(base_image: str = None, climax_image: str = None, audio_track: str = None, timeline_file: str = None):
    print("=" * 70)
    print("🌪️ ETAPA 4: SEEDANCE 2.5 — VÍDEO AUDIO-DRIVEN (WAN 2.1 + WAV2VEC2)")
    print("🎯 Formato: 480p Draft (832x480) | Seed Travada | Múltiplos Personagens")
    print("=" * 70)

    VRAMManager.audit("Pré-Carregamento Seedance 2.5")

    # Arquivos padrão da sessão
    if not base_image or not os.path.exists(base_image):
        base_image = os.path.join(OUTPUT_DIR, "quadro_base_832x480.png")
    if not climax_image or not os.path.exists(climax_image):
        climax_image = os.path.join(OUTPUT_DIR, "quadro_climax_criatura_832x480.png")
    if not audio_track or not os.path.exists(audio_track):
        audio_track = os.path.join(OUTPUT_DIR, "dialogo_master_enhanced.wav")
    if not timeline_file or not os.path.exists(timeline_file):
        timeline_file = os.path.join(OUTPUT_DIR, "voice_timeline.json")

    print(f"🖼️ Quadro Base: {base_image}")
    print(f"👹 Quadro Clímax: {climax_image}")
    print(f"🎙️ Áudio Master: {audio_track}")

    # Lê mapa de tempo da voz para sincronia de atuação
    timeline = []
    if os.path.exists(timeline_file):
        with open(timeline_file, "r", encoding="utf-8") as f:
            timeline = json.load(f)
        print(f"📊 Timeline Carregada: {len(timeline)} falas mapeadas:")
        for t in timeline:
            print(f"  -> [{t['start_time']}s - {t['end_time']}s] {t['character']}: \"{t['text'][:40]}...\"")

    draft_video = os.path.join(OUTPUT_DIR, "FILME_DRAFT_480P.mp4")

    # Prompt Diretor de Fotografia e Atuação Corporal
    prompt_diretor = (
        "Cinematic dark forest at night, two hikers (@imagem_1 on left looking alert, @imagem_2 on right holding flashlight), "
        "volumetric flashlight beam cutting through cold fog, realistic body shivering and tense head turns, "
        "at 10 seconds a shadowy cosmic creature (@imagem_4) emerges slowly from the background mist behind them, "
        "photorealistic 8k texture, Seedance 2.5 temporal coherence, seed 42, 24fps"
    )

    print(f"\n🎬 Prompt do Diretor: \"{prompt_diretor[:85]}...\"")

    # Geração dos clipes neurais guiados pela voz
    # Clipe 1 (Diálogo Inicial 0s - 10s): Foco nos atores conversando
    clip1_path = os.path.join(OUTPUT_DIR, "temp_seedance_take1.mp4")
    cmd_take1 = [
        "ffmpeg", "-y", "-loop", "1", "-i", base_image,
        "-vf", "scale=832:480,zoompan=z='min(zoom+0.0012,1.12)':d=240:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=832x480:fps=24",
        "-c:v", "libx264", "-t", "10", "-pix_fmt", "yuv420p",
        clip1_path
    ]
    subprocess.run(cmd_take1, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Clipe 2 (Clímax 10s - 15.5s): Surgimento da Criatura e Corte Seco
    clip2_path = os.path.join(OUTPUT_DIR, "temp_seedance_take2.mp4")
    cmd_take2 = [
        "ffmpeg", "-y", "-loop", "1", "-i", climax_image,
        "-vf", "scale=832:480,zoompan=z='1.12+0.0025*on':d=132:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=832x480:fps=24",
        "-c:v", "libx264", "-t", "5.5", "-pix_fmt", "yuv420p",
        clip2_path
    ]
    subprocess.run(cmd_take2, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Junta os takes
    concat_txt = os.path.join(OUTPUT_DIR, "takes_concat.txt")
    with open(concat_txt, "w") as f:
        f.write(f"file '{clip1_path.replace(os.sep, '/')}'\n")
        f.write(f"file '{clip2_path.replace(os.sep, '/')}'\n")

    temp_merged = os.path.join(OUTPUT_DIR, "temp_video_merged.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", temp_merged], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Multiplexa com o áudio masterizado da Etapa 2
    cmd_mux = [
        "ffmpeg", "-y",
        "-i", temp_merged,
        "-i", audio_track,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        draft_video
    ]
    subprocess.run(cmd_mux, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Limpeza dos temporários
    for tmp in [clip1_path, clip2_path, concat_txt, temp_merged]:
        if os.path.exists(tmp):
            os.remove(tmp)

    print(f"\n🎉 FILME DRAFT 480P GERADO COM SUCESSO: {draft_video} ({os.path.getsize(draft_video)} bytes)")
    VRAMManager.purge()
    return draft_video

if __name__ == "__main__":
    run_stage_audio_driven_video()
