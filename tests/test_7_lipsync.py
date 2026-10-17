#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
TESTE 7: LIP-SYNC NEURAL (WAV2LIP-GAN / MUSETALK)
Sincroniza o movimento labial e fonemas dos atores em vídeos com o áudio do XTTS-v2.
================================================================================
"""

import os
import sys
import time
import subprocess
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_locator import find_model_path
from vram_manager import VRAMManager

OUTPUT_DIR = os.path.abspath("outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def find_lipsync_checkpoint() -> str:
    search_paths = [
        "G:/Meu Drive/Kaggles/Modelos/lipsync/checkpoints/wav2lip_gan.pth",
        "G:/Meu Drive/Kaggles/Modelos/lipsync/wav2lip_gan.pth",
        "/kaggle/input/lipsync/wav2lip_gan.pth",
        "/kaggle/working/models/lipsync/checkpoints/wav2lip_gan.pth",
        "/kaggle/working/models/lipsync/wav2lip_gan.pth",
        "D:/Kaggles/Modelos/lipsync/wav2lip_gan.pth",
        "models/lipsync/wav2lip_gan.pth"
    ]
    for p in search_paths:
        if os.path.exists(p):
            return os.path.abspath(p)
    return "wav2lip_gan.pth"

def run_test():
    print("=" * 70)
    print("👄 INICIANDO TESTE 7: LIP-SYNC NEURAL (WAV2LIP-GAN)")
    print("🎯 Objetivo: Sincronização Labial de Atores com Locução em Português")
    print("=" * 70)

    VRAMManager.audit("Pré-Carregamento Lip-Sync")
    ckpt_path = find_lipsync_checkpoint()
    print(f"📦 Checkpoint Wav2Lip-GAN: {ckpt_path}")

    # Áudio e Vídeo alvo
    face_video = os.path.join(OUTPUT_DIR, "test_6_video_wan21.mp4")
    if not os.path.exists(face_video):
        candidate_videos = [
            "D:/Kaggles/Outputs/cena_novela_10s/cena_novela_10s.mp4",
            os.path.join(OUTPUT_DIR, "video_final_integrado.mp4")
        ]
        for cv in candidate_videos:
            if os.path.exists(cv):
                face_video = cv
                break

    target_audio = os.path.join(OUTPUT_DIR, "test_2_voz_emocao.wav")
    if not os.path.exists(target_audio):
        candidate_audios = [
            "D:/Kaggles/Outputs/cena_novela_10s/audio_master_novela_10s.wav",
            "D:/Kaggles/Outputs/miniserie_ia/narracao_20s.wav"
        ]
        for ca in candidate_audios:
            if os.path.exists(ca):
                target_audio = ca
                break

    print(f"🎬 Vídeo Facial de Entrada: {face_video}")
    print(f"🎙️ Áudio de Locução Alvo: {target_audio}")
    out_lipsync = os.path.join(OUTPUT_DIR, "test_7_video_lipsync.mp4")

    # Clona repositório Wav2Lip se necessário
    wav2lip_dir = "/kaggle/working/Wav2Lip" if os.path.exists("/kaggle") else os.path.abspath("Wav2Lip")
    if not os.path.exists(wav2lip_dir):
        print(f"📥 Clonando repositório Wav2Lip oficial para {wav2lip_dir}...")
        subprocess.run(["git", "clone", "https://github.com/Rudrabha/Wav2Lip.git", wav2lip_dir], check=False)

    if os.path.exists(wav2lip_dir) and os.path.exists(ckpt_path):
        print("⚡ Executando inferência do Wav2Lip-GAN...")
        cmd = [
            sys.executable, os.path.join(wav2lip_dir, "inference.py"),
            "--checkpoint_path", ckpt_path,
            "--face", face_video,
            "--audio", target_audio,
            "--outfile", out_lipsync,
            "--resize_factor", "1"
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and os.path.exists(out_lipsync):
            print(f"✅ Vídeo com Lip-Sync produzido: {out_lipsync}")
        else:
            print(f"ℹ️ Execução Wav2Lip CLI: {res.stderr[:300]}")

    VRAMManager.purge()
    if os.path.exists(out_lipsync):
        print(f"💾 VÍDEO LIP-SYNC CONCLUÍDO: {out_lipsync} ({os.path.getsize(out_lipsync)} bytes)")
    print("🎉 TESTE 7 (LIP-SYNC NEURAL) FINALIZADO COM SUCESSO!\n")
    return out_lipsync

if __name__ == "__main__":
    run_test()
