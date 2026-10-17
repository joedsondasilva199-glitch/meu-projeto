#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download oficial dos novos modelos de vídeo e áudio condicional:
1. Wan 2.1 (T2V 1.3B Diffusers) -> Modelos/wan21/
2. Wav2Lip-GAN -> Modelos/lipsync/
3. Wav2Vec2 Base (Audio Encoder) -> Modelos/wav2vec2/
4. Real-ESRGAN (Super-Resolução 1080p) -> Modelos/realesrgan/
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
logger = logging.getLogger("DownloaderExpansao")

from huggingface_hub import snapshot_download

BASE_DRIVE = r"G:\Meu Drive\Kaggles\Modelos"
WAN_DIR = os.path.join(BASE_DRIVE, "wan21")
LIP_DIR = os.path.join(BASE_DRIVE, "lipsync")
WAV2VEC_DIR = os.path.join(BASE_DRIVE, "wav2vec2")
ESRGAN_DIR = os.path.join(BASE_DRIVE, "realesrgan")

for d in [WAN_DIR, LIP_DIR, WAV2VEC_DIR, ESRGAN_DIR]:
    os.makedirs(d, exist_ok=True)

print("=" * 70)
print("🚀 INICIANDO DOWNLOAD DOS NOVOS MODELOS DE VÍDEO E ÁUDIO NO GOOGLE DRIVE")
print(f"📁 Pasta Raiz: {BASE_DRIVE}")
print("=" * 70)

# 1. Download da Wan 2.1 (1.3B Diffusers)
print("\n[1/4] 👑 Baixando Wan 2.1 (Wan-AI/Wan2.1-T2V-1.3B-Diffusers)...")
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
print("\n[2/4] 👄 Baixando Wav2Lip-GAN (camenduru/Wav2Lip)...")
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

# 3. Download do Wav2Vec2 Base (Codificador de Áudio)
print("\n[3/4] 🎙️ Baixando Wav2Vec2 Base (facebook/wav2vec2-base-960h)...")
t2 = time.time()
try:
    snapshot_download(
        repo_id="facebook/wav2vec2-base-960h",
        local_dir=WAV2VEC_DIR,
        local_dir_use_symlinks=False,
        resume_download=True,
        allow_patterns=["*.json", "*.safetensors", "*.bin", "*.txt"]
    )
    print(f"✅ Wav2Vec2 baixado com sucesso em {round(time.time() - t2, 1)}s!")
except Exception as e:
    print(f"❌ Erro no download do Wav2Vec2: {e}")

# 4. Download do Real-ESRGAN (Super-Resolução 1080p)
print("\n[4/4] 💎 Baixando Real-ESRGAN (ai-forever/Real-ESRGAN)...")
t3 = time.time()
try:
    snapshot_download(
        repo_id="ai-forever/Real-ESRGAN",
        local_dir=ESRGAN_DIR,
        local_dir_use_symlinks=False,
        resume_download=True,
        allow_patterns=["*.pth", "*.bin", "*.json"]
    )
    print(f"✅ Real-ESRGAN baixado com sucesso em {round(time.time() - t3, 1)}s!")
except Exception as e:
    print(f"❌ Erro no download do Real-ESRGAN: {e}")

print("\n" + "=" * 70)
print("🎉 TODOS OS DOWNLOADS CONCLUÍDOS NO GOOGLE DRIVE!")
print("=" * 70)
