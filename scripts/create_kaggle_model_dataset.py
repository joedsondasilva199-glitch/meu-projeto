#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
PUBLICADOR DE KAGGLE DATASET COMPARTILHADO (ZERO DOWNLOAD ENTRE CONTAS)
Registra os Modelos Principais em `joedsonsilva199/kaggles-32gb-models`
Configura montagem automática em `/kaggle/input/kaggles-32gb-models`
================================================================================
"""

import os
import sys
import json
import shutil
import subprocess

for s in [sys.stdout, sys.stderr]:
    if hasattr(s, 'reconfigure'):
        s.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_STAGING = os.path.join(BASE_DIR, "dataset_staging")
KERNEL_META_PATH = os.path.join(BASE_DIR, "kaggle_push", "kernel-metadata.json")

os.makedirs(DATASET_STAGING, exist_ok=True)

# 1. Configura metadata do Dataset
DATASET_NAME = "kaggles-32gb-models"
DATASET_ID = f"joedsonsilva199/{DATASET_NAME}"

metadata = {
    "title": "Kaggles 32GB Fast Models",
    "id": DATASET_ID,
    "licenses": [{"name": "CC0-1.0"}]
}

meta_file = os.path.join(DATASET_STAGING, "dataset-metadata.json")
with open(meta_file, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print("=" * 70)
print(f"📦 CONFIGURAÇÃO DO KAGGLE DATASET: {DATASET_ID}")
print(f"📁 Pasta de Staging: {DATASET_STAGING}")
print("=" * 70)

# 2. Cria arquivo de índice dos modelos suportados
readme_path = os.path.join(DATASET_STAGING, "README.md")
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(f"""# Kaggle 32GB Shared AI Models

Pesos neurais otimizados para montagem instantânea no `/kaggle/input/{DATASET_NAME}`:
- **Wan 2.1 (T2V 1.3B Diffusers)**: Geração de vídeo neural temporal em FP16.
- **SDXL Turbo**: Geração de quadros fotorrealistas em 1 passo.
- **XTTS-v2**: Clonagem de voz prosódica dramática.
- **Wav2Lip-GAN**: Sincronia labial multi-personagem.
""")

print("✅ Metadados do dataset gerados com sucesso!")

KERNEL_META_PATHS = [
    os.path.join(BASE_DIR, "kaggle_push", "kernel-metadata.json"),
    r"D:\Kaggles\kaggle_push\kernel-metadata.json"
]

# 3. Atualiza o kernel-metadata.json para vincular o dataset
for km_path in KERNEL_META_PATHS:
    if os.path.exists(km_path):
        try:
            with open(km_path, "r", encoding="utf-8") as f:
                kmeta = json.load(f)

            sources = kmeta.get("dataset_sources", [])
            if DATASET_ID not in sources:
                sources.append(DATASET_ID)
                kmeta["dataset_sources"] = sources
                with open(km_path, "w", encoding="utf-8") as f:
                    json.dump(kmeta, f, indent=2)
                print(f"🔗 {km_path} atualizado: vinculado a {DATASET_ID}")
            else:
                print(f"ℹ️ {DATASET_ID} já vinculado em {km_path}.")
        except Exception as e:
            print(f"Nota na atualização de {km_path}: {e}")

# 4. Instruções e disparo da criação via API
print("\n" + "=" * 70)
print("COMO PUBLICAR NO KAGGLE DATASETS:")
print("=" * 70)
print(f"1. Para publicar os arquivos de modelo na sua conta oficial:")
print(f"   kaggle datasets create -p \"{DATASET_STAGING}\"")
print(f"2. Para criar nova versão quando atualizar os pesos:")
print(f"   kaggle datasets version -p \"{DATASET_STAGING}\" -m \"Atualização de pesos neurais\"")
print("=" * 70)

def publish_dataset():
    """Tenta publicar automaticamente se credenciais do Kaggle estiverem ativas."""
    print("\nExecutando verificação de existência do dataset no Kaggle...")
    chk = subprocess.run(["kaggle", "datasets", "status", DATASET_ID], capture_output=True, text=True)
    if "ready" in chk.stdout.lower():
        print(f"✅ Dataset {DATASET_ID} já existe e está ativo na nuvem do Kaggle!")
    else:
        print(f"Criando dataset {DATASET_ID} via Kaggle API...")
        res = subprocess.run(["kaggle", "datasets", "create", "-p", DATASET_STAGING], capture_output=True, text=True)
        print(res.stdout)
        if res.stderr:
            print(res.stderr)

if __name__ == "__main__":
    publish_dataset()
