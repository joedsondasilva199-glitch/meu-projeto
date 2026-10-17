#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
CLIENTE REMOTO WINDOWS -> SERVIDOR GPU QUENTE KAGGLE
Dispara renderizações via HTTP POST direto para as 2x Tesla T4 já quentes,
sem fila QUEUED e sem baixar modelos de novo!
================================================================================
"""

import os
import sys
import time
import requests
import argparse

LOCAL_OUT = r"D:\Kaggles\Outputs\kaggle_gpu_real"
GDRIVE_OUT = r"G:\Meu Drive\Kaggles\Outputs"
ENDPOINT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "active_gpu_endpoint.txt")
GDRIVE_ENDPOINT = r"G:\Meu Drive\Kaggles\active_gpu_endpoint.txt"

os.makedirs(LOCAL_OUT, exist_ok=True)
os.makedirs(GDRIVE_OUT, exist_ok=True)

def get_active_endpoint(cli_url: str = None) -> str:
    if cli_url:
        return cli_url.strip().rstrip("/")
    for path in [ENDPOINT_FILE, GDRIVE_ENDPOINT]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    url = f.read().strip().rstrip("/")
                    if url.startswith("http"):
                        return url
            except: pass
    raise ValueError("Nenhum endpoint ativo encontrado. Forneça com --url ou grave em active_gpu_endpoint.txt.")

def check_server(base_url: str):
    print(f"\n📡 Conectando ao Servidor GPU em: {base_url}...")
    res = requests.get(f"{base_url}/health", timeout=15)
    if res.status_code == 200:
        data = res.json()
        print("✅ SERVIDOR ONLINE E SAUDÁVEL!")
        print(f"🔹 GPUs: {data.get('gpu_count')} aceleradores detectados")
        for g in data.get("vram", []):
            print(f"   - GPU [{g['gpu_id']}] ({g['name']}): VRAM Alocada: {g['alocada_mb']} MB / {g['total_vram_mb']} MB")
        return True
    else:
        print(f"❌ Resposta inesperada do servidor: {res.status_code}")
        return False

def render_prompt(base_url: str, prompt: str, num_frames: int = 49, steps: int = 15):
    print(f"\n🎬 Enviando solicitação de renderização neural (15 steps, {num_frames} frames)...")
    print(f"   Prompt: '{prompt[:70]}...'")
    
    payload = {
        "prompt": prompt,
        "num_frames": num_frames,
        "steps": steps,
        "height": 480,
        "width": 832,
        "fps": 16,
        "seed": 42
    }
    
    t0 = time.time()
    res = requests.post(f"{base_url}/render_scene", json=payload, timeout=600)
    
    if res.status_code == 200:
        data = res.json()
        filename = data["filename"]
        tempo_s = data["tempo_segundos"]
        vram_mb = data["vram_pico_mb"]
        print(f"🎉 Renderização concluída na GPU em {tempo_s}s (VRAM Pico: {vram_mb} MB)!")
        
        # Faz download direto do arquivo
        download_url = f"{base_url}/download/{filename}"
        print(f"📥 Baixando {filename} diretamente da nuvem...")
        
        dl_res = requests.get(download_url, stream=True)
        local_path = os.path.join(LOCAL_OUT, filename)
        with open(local_path, "wb") as f:
            for chunk in dl_res.iter_content(chunk_size=1024*1024):
                f.write(chunk)
                
        sz_mb = round(os.path.getsize(local_path)/(1024*1024), 2)
        print(f"✅ Vídeo salvo localmente: {local_path} ({sz_mb} MB)")
        
        # Espelha para Google Drive
        gdrive_path = os.path.join(GDRIVE_OUT, filename)
        if os.path.exists(GDRIVE_OUT):
            try:
                import shutil
                shutil.copy2(local_path, gdrive_path)
                print(f"☁️ Espelho sincronizado no Google Drive: {gdrive_path}")
            except Exception as e:
                print(f"Nota na cópia para Drive: {e}")
                
        return local_path
    else:
        print(f"❌ Erro na renderização: {res.status_code} - {res.text}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente GPU Quente Kaggle")
    parser.add_argument("--url", help="URL do Cloudflared (ex: https://xxx.trycloudflare.com)")
    parser.add_argument("--prompt", help="Prompt da cena", default="Dramatic telenovela confrontation between Helena and Marcos, tears, cinematic lighting, 1080p")
    parser.add_argument("--check-only", action="store_true", help="Apenas checa saúde do servidor")
    
    args = parser.parse_args()
    try:
        url = get_active_endpoint(args.url)
        is_ok = check_server(url)
        if is_ok and not args.check_only:
            render_prompt(url, args.prompt)
    except Exception as e:
        print(f"Erro: {e}")
