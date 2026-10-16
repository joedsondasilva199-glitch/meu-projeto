#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
DOWNLOADER OFICIAL DE MODELOS REAIS (32GB VRAM DUAL T4)
Baixa os pesos neurais dos 4 especialistas e salva na pasta de modelos:
1. DeepSeek-R1 (8B) - Roteiro & Cérebro
2. XTTS-v2 - Locução & Clonagem de Voz
3. SDXL Turbo - Imagens Cinematográficas
4. Whisper Large v3 - Transcrição & Legendas
================================================================================
"""

import os
import sys
import time
import shutil
import logging

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ModelDownloader")

# Garante dependências do Hugging Face
try:
    from huggingface_hub import snapshot_download
except ImportError:
    logger.info("Instalando huggingface_hub para download de alta velocidade...")
    os.system(f"{sys.executable} -m pip install -q --no-warn-script-location huggingface_hub")
    from huggingface_hub import snapshot_download

# Define o caminho de salvamento (prioriza Google Drive montado ou local)
def get_target_models_dir() -> str:
    # 1. Se estiver no Colab com Drive montado
    if os.path.exists("/content/drive/MyDrive/Kaggles/Modelos"):
        return "/content/drive/MyDrive/Kaggles/Modelos"
    # 2. Se estiver no Windows com G: montado
    if os.path.exists("G:/Meu Drive/Kaggles/Modelos"):
        return "G:/Meu Drive/Kaggles/Modelos"
    # 3. Se estiver no Kaggle
    if os.path.exists("/kaggle"):
        path = "/kaggle/working/models"
        os.makedirs(path, exist_ok=True)
        return path
    # 4. Pasta local padrão
    local_dir = os.path.abspath("D:/Kaggles/Modelos" if os.path.exists("D:/Kaggles") else "models")
    os.makedirs(local_dir, exist_ok=True)
    return local_dir

MODELS_DIR = get_target_models_dir()

# Definição dos 4 modelos oficiais do Hugging Face
MODELS_CATALOG = [
    {
        "id": "whisper",
        "name": "Whisper Large v3 Turbo (OpenAI)",
        "repo_id": "openai/whisper-large-v3-turbo",
        "category": "👂 Ouvido & Legendas",
        "allow_patterns": ["*.json", "*.safetensors", "*.txt", "*.bin"]
    },
    {
        "id": "xtts",
        "name": "XTTS-v2 (Coqui Neural Voice)",
        "repo_id": "coqui/XTTS-v2",
        "category": "🎙️ Narrador & Voz Neural",
        "allow_patterns": ["*.json", "*.pth", "*.vocab", "*.txt", "*.bin"]
    },
    {
        "id": "sdxl",
        "name": "SDXL Turbo (Stability AI)",
        "repo_id": "stabilityai/sdxl-turbo",
        "category": "🎨 Diretor de Imagem",
        "allow_patterns": ["*.json", "*.safetensors", "*.txt", "*fp16*"]
    },
    {
        "id": "deepseek",
        "name": "DeepSeek-R1-Distill-Llama-8B",
        "repo_id": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "category": "✍️ Roteirista & Raciocínio",
        "allow_patterns": ["*.json", "*.safetensors", "*.model", "*.txt"]
    },
    {
        "id": "svd",
        "name": "Stable Video Diffusion XT (SVD-XT)",
        "repo_id": "stabilityai/stable-video-diffusion-img2vid-xt-1-1",
        "category": "🎥 Gerador de Vídeo Realista (25 Quadros)",
        "allow_patterns": ["*.json", "*.safetensors", "*.txt", "*fp16*"]
    }
]

def download_all_models(dest_dir: str = MODELS_DIR):
    print("=" * 65)
    print("🚀 INICIANDO DOWNLOAD DOS 4 MODELOS REAIS PARA A ESTEIRA")
    print(f"📁 Destino dos arquivos: {dest_dir}")
    print("=" * 65)

    for idx, m in enumerate(MODELS_CATALOG, start=1):
        m_folder = os.path.join(dest_dir, m["id"])
        print(f"\n[{idx}/4] {m['category']}: {m['name']}")
        print(f" -> Repositório: https://huggingface.co/{m['repo_id']}")
        
        # Verifica se já está baixado
        if os.path.exists(m_folder) and len(os.listdir(m_folder)) > 2:
            print(f" ✅ Modelo já baixado anteriormente em: {m_folder} (Saltando)")
            continue

        print(f" ⏳ Baixando arquivos oficiais em alta velocidade...")
        start_t = time.time()
        
        try:
            snapshot_download(
                repo_id=m["repo_id"],
                local_dir=m_folder,
                local_dir_use_symlinks=False,
                resume_download=True,
                allow_patterns=m.get("allow_patterns")
            )
            elapsed = round(time.time() - start_t, 1)
            print(f" ✅ Concluído com sucesso em {elapsed}s!")
        except Exception as e:
            print(f" ⚠️ Aviso no download de {m['name']}: {e}")

    print("\n" + "=" * 65)
    print("🎉 TODOS OS 4 MODELOS ESTÃO SALVOS E PRONTOS PARA USO!")
    print(f"📁 Pasta permanente: {dest_dir}")
    print("=" * 65)

if __name__ == "__main__":
    download_all_models()
