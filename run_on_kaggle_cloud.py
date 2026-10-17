#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
KAGGLE CLOUD RUNNER: DISPACHO E SINCRONIZAÇÃO AUTÔNOMA DE JOBS GPU
Vinculado ao Notebook: joedsonsilva199/notebook1889a22142
Hardware Remoto: 2x NVIDIA Tesla T4 (32 GB VRAM Total)
================================================================================
"""

import os
import sys
import time
import json
import shutil
import argparse
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

KERNEL_ID = "joedsonsilva199/notebook1889a22142"
LOCAL_OUTPUT_DIR = r"D:\Kaggles\Outputs"
GDRIVE_OUTPUT_DIR = r"G:\Meu Drive\Kaggles\Outputs"
NOTEBOOK_SOURCE = r"D:\Kaggles\KAGGLE_TESTE_MODELOS_32GB.ipynb"
STAGING_DIR = os.path.abspath(".kaggle_staging")

def ensure_kaggle_auth():
    """Garante credenciais da API do Kaggle no local correto."""
    kaggle_dir = os.path.expanduser("~/.kaggle")
    kaggle_json = os.path.join(kaggle_dir, "kaggle.json")
    
    # 1. Se já existir o arquivo ~/.kaggle/kaggle.json
    if os.path.exists(kaggle_json):
        return True
        
    # 2. Se variáveis de ambiente estiverem configuradas
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        return True

    # 3. Se arquivo kaggle.json estiver na pasta do projeto ou Google Drive
    search_locations = [
        "kaggle.json",
        os.path.join("D:\\Kaggles", "kaggle.json"),
        os.path.join("G:\\Meu Drive\\Kaggles", "kaggle.json"),
        os.path.join("C:\\Users\\Lipe", "kaggle.json")
    ]
    for loc in search_locations:
        if os.path.exists(loc):
            os.makedirs(kaggle_dir, exist_ok=True)
            shutil.copy2(loc, kaggle_json)
            print(f"✅ Credencial Kaggle copiada de {loc} para {kaggle_json}")
            return True

    print("\n" + "!" * 70)
    print("⚠️ ATENÇÃO: Credencial 'kaggle.json' não encontrada!")
    print("Para disparar o notebook automaticamente nas 2x T4 pela API do Kaggle:")
    print("1. Acesse https://www.kaggle.com/settings")
    print("2. Clique em 'Create New Token' para baixar o arquivo 'kaggle.json'")
    print(f"3. Coloque o arquivo em: {kaggle_json}")
    print("!" * 70 + "\n")
    return False

def prepare_kernel_metadata():
    """Gera o arquivo kernel-metadata.json obrigatório para o kaggle kernels push."""
    os.makedirs(STAGING_DIR, exist_ok=True)
    
    # Copia o notebook atualizado para a pasta de staging
    shutil.copy2(NOTEBOOK_SOURCE, os.path.join(STAGING_DIR, "KAGGLE_TESTE_MODELOS_32GB.ipynb"))
    
    meta = {
        "id": KERNEL_ID,
        "title": "notebook1889a22142",
        "code_file": "KAGGLE_TESTE_MODELOS_32GB.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": "true",
        "enable_gpu": "true",
        "enable_tpu": "false",
        "enable_internet": "true",
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": []
    }
    
    meta_path = os.path.join(STAGING_DIR, "kernel-metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"📄 Metadados do Kaggle Kernel gerados em: {meta_path}")
    return STAGING_DIR

def push_and_run():
    print("=" * 70)
    print(f"🚀 ENVIANDO JOB PARA AS 2x TESLA T4 (32GB VRAM) NO KAGGLE CLOUD")
    print(f"🎯 Kernel Alvo: {KERNEL_ID}")
    print("=" * 70)

    if not ensure_kaggle_auth():
        return False

    staging = prepare_kernel_metadata()

    # 1. Envia o notebook via CLI
    print("\n⏳ Enviando notebook via 'kaggle kernels push'...")
    cmd_push = ["kaggle", "kernels", "push", "-p", staging]
    res_push = subprocess.run(cmd_push, capture_output=True, text=True)
    print(res_push.stdout)
    if res_push.returncode != 0:
        print(f"❌ Erro ao enviar kernel: {res_push.stderr}")
        return False

    print("✅ Notebook enviado e execução em GPU Dual T4 iniciada no Kaggle!")

    # 2. Monitoramento contínuo do status
    print("\n📡 Monitorando progresso da inferência neural nas GPUs da nuvem...")
    while True:
        cmd_status = ["kaggle", "kernels", "status", KERNEL_ID]
        res_status = subprocess.run(cmd_status, capture_output=True, text=True)
        status_line = res_status.stdout.strip()
        print(f" -> Status: {status_line}")

        if "complete" in status_line.lower():
            print("\n🎉 EXECUÇÃO NAS GPUS CONCLUÍDA COM SUCESSO!")
            break
        elif "error" in status_line.lower() or "failed" in status_line.lower():
            print(f"\n❌ Falha na execução remota do Kaggle: {status_line}")
            return False

        time.sleep(30)

    # 3. Baixa os arquivos renderizados
    print(f"\n📥 Baixando outputs e vídeos finais para: {LOCAL_OUTPUT_DIR}")
    os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)
    cmd_output = ["kaggle", "kernels", "output", KERNEL_ID, "-p", LOCAL_OUTPUT_DIR]
    subprocess.run(cmd_output, check=True)

    # 4. Sincroniza com Google Drive
    if os.path.exists(r"G:\Meu Drive"):
        os.makedirs(GDRIVE_OUTPUT_DIR, exist_ok=True)
        for item in os.listdir(LOCAL_OUTPUT_DIR):
            s = os.path.join(LOCAL_OUTPUT_DIR, item)
            d = os.path.join(GDRIVE_OUTPUT_DIR, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
            elif os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
        print("✅ Arquivos sincronizados com Google Drive com sucesso!")

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true", help="Apenas checa o status do kernel")
    args = parser.parse_args()

    if args.status:
        cmd_status = ["kaggle", "kernels", "status", KERNEL_ID]
        res = subprocess.run(cmd_status, capture_output=True, text=True)
        print(res.stdout)
    else:
        push_and_run()
