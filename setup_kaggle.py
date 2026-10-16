#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
SETUP KAGGLE: CONFIGURADOR UNIVERSAL ZERO-ESFORÇO PARA 32GB VRAM DUAL T4 x2
Executa automaticamente:
1. Diagnóstico e alocação de 32 GB VRAM (Dual GPU T4 x2)
2. Instalação e verificação de pacotes (Accelerate, Transformers, PyTorch, FastAPI)
3. Subida do túnel Cloudflare seguro com URL HTTPS pública
4. Execução do pipeline de 32 GB com sharding paralelo e keep-alive anti-hibernação
================================================================================
"""

import os
import sys
import time
import subprocess
import threading

def run(cmd: str):
    print(f"▶️ Executando: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

print("=" * 65)
print("🚀 INICIANDO SETUP UNIVERSAL KAGGLE (32 GB VRAM DUAL T4 x2)")
print("=" * 65)

# 1. Instalar dependências essenciais
print("\n📦 [1/4] Instalando dependências essenciais...")
run(f"{sys.executable} -m pip install -q --no-warn-script-location accelerate torch transformers fastapi uvicorn requests python-multipart psutil")

import torch
from accelerate import Accelerator

print(f"\n🎮 [2/4] Verificando Hardware...")
print(f"CUDA Disponível: {torch.cuda.is_available()}")
num_gpus = torch.cuda.device_count()
print(f"Total de GPUs detectadas: {num_gpus}")
for i in range(num_gpus):
    props = torch.cuda.get_device_properties(i)
    print(f" -> GPU [{i}]: {props.name} | VRAM: {props.total_memory / (1024**3):.2f} GB")

# 2. Configurar Cloudflare Tunnel
print("\n🌐 [3/4] Inicializando Túnel Cloudflare para Acesso Externo...")
cloudflared_path = os.path.abspath("cloudflared")
if not os.path.exists(cloudflared_path):
    run(f"curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o {cloudflared_path}")
    run(f"chmod +x {cloudflared_path}")

# Inicia servidor FastAPI mínimo para responder pelo túnel
from fastapi import FastAPI
import uvicorn
api_app = FastAPI(title="Kaggle 32GB Node")

@api_app.get("/")
def home():
    return {
        "status": "online",
        "node": "Kaggle Dual T4 x2",
        "total_vram_gb": sum(torch.cuda.get_device_properties(i).total_memory / (1024**3) for i in range(torch.cuda.device_count())) if torch.cuda.is_available() else 0,
        "gpus": torch.cuda.device_count()
    }

threading.Thread(target=lambda: uvicorn.run(api_app, host="127.0.0.1", port=8000, log_level="warning"), daemon=True).start()
time.sleep(2)

def monitor_tunnel():
    proc = subprocess.Popen([cloudflared_path, "tunnel", "--url", "http://127.0.0.1:8000"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in iter(proc.stdout.readline, ""):
        if "trycloudflare.com" in line:
            for tok in line.split():
                if "trycloudflare.com" in tok:
                    print(f"\n========================================================")
                    print(f"🎉 SEU SERVIDOR KAGGLE ESTÁ ONLINE NA INTERNET:")
                    print(f"🌍 URL PÚBLICA: {tok.strip()}")
                    print(f"📑 API DOCS:    {tok.strip()}/docs")
                    print(f"========================================================\n")
                    break

threading.Thread(target=monitor_tunnel, daemon=True).start()
time.sleep(5)

# 3. Execução da Carga de Trabalho Distribuída (32GB VRAM)
print("\n⚡ [4/4] Disparando Runner de 32 GB VRAM nos Tensores...")
import kaggle_32gb_runner
kaggle_32gb_runner.execute_dual_t4_pipeline()

print("\n" + "=" * 65)
print("✅ AMBIENTE 100% CONFIGURADO, PRONTO E FUNCIONAL!")
print("🔥 Keep-Alive Ativo: O notebook permanecerá acordado e operando.")
print("=" * 65)

try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("Sessão finalizada pelo usuário.")
