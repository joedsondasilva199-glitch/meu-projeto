#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Localizador Inteligente de Modelos para Kaggle / Local / Drive.
Garante que os testes sempre encontrem os modelos baixados ou façam o carregamento correto.
"""

import os
import sys
import logging

logger = logging.getLogger("ModelLocator")

MODEL_CONFIGS = {
    "deepseek": {
        "repo_id": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "folder_name": "deepseek",
        "description": "DeepSeek-R1 (8B) - Raciocínio & Roteiro"
    },
    "xtts": {
        "repo_id": "coqui/XTTS-v2",
        "folder_name": "xtts",
        "description": "XTTS-v2 - Voz Neural com Emoção e Clonagem"
    },
    "sdxl": {
        "repo_id": "stabilityai/sdxl-turbo",
        "folder_name": "sdxl",
        "description": "SDXL Turbo - Imagens Cinematográficas 1024x1024"
    },
    "whisper": {
        "repo_id": "openai/whisper-large-v3-turbo",
        "folder_name": "whisper",
        "description": "Whisper Large v3 Turbo - Transcrição & Legendas"
    },
    "svd": {
        "repo_id": "stabilityai/stable-video-diffusion-img2vid-xt-1-1",
        "folder_name": "svd",
        "description": "Stable Video Diffusion XT - Geração de Vídeo Realista 25 Quadros"
    },
    "wan21": {
        "repo_id": "Wan-AI/Wan2.1-T2V-1.3B",
        "folder_name": "wan21",
        "description": "Wan 2.1 (1.3B) - Geração de Vídeo Realista Estilo Seedance/Kling"
    },
    "wav2vec2": {
        "repo_id": "facebook/wav2vec2-base-960h",
        "folder_name": "wav2vec2",
        "description": "Wav2Vec2 - Codificador de Áudio Neural para Vídeo Audio-Driven"
    },
    "realesrgan": {
        "repo_id": "ai-forever/Real-ESRGAN",
        "folder_name": "realesrgan",
        "description": "Real-ESRGAN - Super-Resolução e Upscale Neural 480p para 1080p"
    },
    "lipsync": {
        "repo_id": "camenduru/Wav2Lip",
        "folder_name": "lipsync",
        "description": "Wav2Lip-GAN - Sincronização Labial de Atores"
    }
}

def find_model_path(model_key: str) -> str:
    cfg = MODEL_CONFIGS.get(model_key)
    if not cfg:
        raise ValueError(f"Modelo desconhecido: {model_key}")
        
    folder = cfg["folder_name"]
    repo = cfg["repo_id"]

    # Possíveis locais onde o modelo pode estar no Kaggle, Google Drive ou Máquina Local
    search_paths = [
        # 1. Entrada de Dataset do Kaggle
        f"/kaggle/input/{folder}",
        f"/kaggle/input/modelos/{folder}",
        f"/kaggle/input/kaggles-modelos/{folder}",
        f"/kaggle/input/meu-projeto/models/{folder}",
        # 2. Diretório local de trabalho no Kaggle
        f"/kaggle/working/models/{folder}",
        f"/kaggle/working/{folder}",
        # 3. Google Drive no Colab ou Linux
        f"/content/drive/MyDrive/Kaggles/Modelos/{folder}",
        # 4. Google Drive no Windows (G:)
        f"G:/Meu Drive/Kaggles/Modelos/{folder}",
        # 5. Disco D: local
        f"D:/Kaggles/Modelos/{folder}",
        # 6. Pasta local no diretório atual
        f"models/{folder}"
    ]

    for p in search_paths:
        if os.path.exists(p) and len(os.listdir(p)) > 1:
            print(f"[ModelLocator] ✅ Modelo '{model_key}' localizado em disco: {p}")
            return os.path.abspath(p)

    # Se não encontrado localmente e estiver no Kaggle, faz download de alta velocidade (2.5 Gbps)
    if os.path.exists("/kaggle"):
        print(f"[ModelLocator] ⚡ Baixando '{model_key}' do Hugging Face Hub para /kaggle/working/models/{folder}...")
        try:
            from huggingface_hub import snapshot_download
            target_dir = f"/kaggle/working/models/{folder}"
            os.makedirs(target_dir, exist_ok=True)
            snapshot_download(repo_id=repo, local_dir=target_dir, resume_download=True)
            return target_dir
        except Exception as e:
            print(f"[ModelLocator] Aviso no download: {e}. Retornando repo_id direto.")

    # Retorna o repo_id oficial para carregamento via Hugging Face direto
    print(f"[ModelLocator] ℹ️ Utilizando identificador Hugging Face: {repo}")
    return repo
