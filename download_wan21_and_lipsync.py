#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download oficial dos pesos da Wan 2.1 (T2V 1.3B Diffusers) e Wav2Lip-GAN
Direto para o Google Drive: G:\Meu Drive\Kaggles\Modelos\
"""

import os
import sys
import time
import logging

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DownloaderWanLip")

from huggingface_hub import snapshot_download

BASE_DRIVE = r"G:\Meu Drive\Kaggles\Modelos"
WAN_DIR = os.path.join(BASE_DRIVE, "wan21")
LIP_DIR = os.path.join(BASE_DRIVE, "lipsync")

os.makedirs(WAN_DIR, exist_ok=True)
os.makedirs(LIP_DIR, exist_ok=True)

print("=" * 70)
print("🚀 INICIANDO DOWNLOAD DOS PESOS DA WAN 2.1 E LIP-SYNC NO GOOGLE DRIVE")
print(f"📁 Destino Wan 2.1: {WAN_DIR}")
print(f"📁 Destino Lip-Sync: {LIP_DIR}")
print("=" * 70)

# 1. Download da Wan 2.1 (1.3B Diffusers)
print("\n[1/2] 👑 Baixando Wan 2.1 (Wan-AI/Wan2.1-T2V-1.3B-Diffusers)...")
t0 = time.time()
try:
    snapshot_download(
        repo_id="Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
        local_dir=WAN_DIR,
        local_dir_use_symlinks=False,
        resume_download=True,
        allow_patterns=["*.json", "*.safetensors", "*.txt", "*.model"]
    )
    print(f"✅ Wan 2.1 baixada com sucesso em {round(time.time() - t0, 1)}s!")
except Exception as e:
    print(f"❌ Erro no download da Wan 2.1: {e}")

# 2. Download do Wav2Lip-GAN (Lip-Sync Neural)
print("\n[2/2] 👄 Baixando Wav2Lip-GAN (camenduru/Wav2Lip)...")
t1 = time.time()
try:
    snapshot_download(
        repo_id="camenduru/Wav2Lip",
        local_dir=LIP_DIR,
        local_dir_use_symlinks=False,
        resume_download=True,
        allow_patterns=["*.pth", "*.json", "*.txt"]
    )
    print(f"✅ Wav2Lip-GAN baixado com sucesso em {round(time.time() - t1, 1)}s!")
except Exception as e:
    print(f"❌ Erro no download do Wav2Lip: {e}")

print("\n" + "=" * 70)
print("🎉 DOWNLOADS CONCLUÍDOS!")
print("=" * 70)
