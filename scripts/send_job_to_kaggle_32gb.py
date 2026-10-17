#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
CLIENTE DE DISPARO INSTANTÂNEO: WINDOWS -> 2x TESLA T4 KAGGLE (SERVIDOR QUENTE)
Zero Fila QUEUED, Zero Boot - Renderiza em 20s e Baixa Imediatamente
================================================================================
"""

import os
import sys
import json
import time
import shutil
import argparse
import requests

LOCAL_OUT = r"D:\Kaggles\Outputs\kaggle_gpu_real"
GDRIVE_OUT = r"G:\Meu Drive\Kaggles\Outputs"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for d in [LOCAL_OUT, GDRIVE_OUT]:
    os.makedirs(d, exist_ok=True)

def find_active_tunnel_url(url_arg: str = None) -> str:
    """Busca a URL ativa no argumento, arquivo local ou no repositório GitHub."""
    if url_arg and url_arg.startswith("http"):
        return url_arg.strip().rstrip("/")

    # 1. Verifica arquivo local
    candidates = [
        os.path.join(BASE_DIR, "active_tunnel.json"),
        os.path.join(r"D:\Stack de Agentes", "active_tunnel.json"),
        os.path.join(r"G:\Meu Drive\Kaggles", "active_tunnel.json")
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                data = json.load(open(p, encoding="utf-8"))
                url = data.get("url")
                if url and url.startswith("http"):
                    print(f"📡 URL obtida do arquivo local ({p}): {url}")
                    return url.rstrip("/")
            except: pass

    # 2. Busca do GitHub Raw se disponível
    try:
        raw_url = "https://raw.githubusercontent.com/joedsondasilva199-glitch/meu-projeto/main/active_tunnel.json"
        res = requests.get(raw_url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            url = data.get("url")
            if url and url.startswith("http"):
                print(f"📡 URL obtida do GitHub (active_tunnel.json): {url}")
                return url.rstrip("/")
    except: pass

    raise RuntimeError(
        "Nenhum túnel ativo encontrado!\n"
        "Inicie o servidor interativo no Kaggle executando:\n"
        "  python /tmp/meu-projeto/Scripts/kaggle_32gb_hot_server.py\n"
        "Ou passe a URL diretamente via: --url https://xxx.trycloudflare.com"
    )

def send_render_request(tunnel_url: str, perfil: str, prompt: str, aspect_ratio: str = "9:16", steps: int = 6):
    print("\n" + "=" * 70)
    print("🚀 DISPARANDO JOB PARA AS 2x TESLA T4 NO KAGGLE (SERVIDOR QUENTE)")
    print(f"🔗 Servidor Alvo: {tunnel_url}")
    print(f"🎭 Perfil: {perfil} | Proporção: {aspect_ratio} | Steps: {steps}")
    print(f"📝 Prompt: '{prompt[:75]}...'")
    print("=" * 70)

    # 1. Checagem de Saúde
    try:
        health_res = requests.get(f"{tunnel_url}/health", timeout=10)
        if health_res.status_code == 200:
            hdata = health_res.json()
            print("✅ Servidor GPU Conectado com Sucesso!")
            for g in hdata.get("gpus", []):
                print(f"   🔹 GPU [{g['id']}] {g['name']} | VRAM: {g['vram_allocated_mb']} MB")
        else:
            print(f"⚠️ Servidor respondeu com status {health_res.status_code}")
    except Exception as e:
        print(f"❌ Erro ao conectar no túnel: {e}")
        return None

    # 2. Envio da Renderização
    job_id = f"{perfil}_{int(time.time())}"
    payload = {
        "job_id": job_id,
        "perfil": perfil,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "num_frames": 49,
        "steps": steps
    }

    print("\n⚡ Processando nas GPUs Tesla T4 em FP16 (Aguarde alguns segundos)...")
    t0 = time.time()
    try:
        render_res = requests.post(f"{tunnel_url}/render", json=payload, timeout=600)
    except requests.exceptions.Timeout:
        print("❌ Timeout na requisição (excedeu 10 minutos).")
        return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

    if render_res.status_code != 200:
        print(f"❌ Erro no render: {render_res.status_code} - {render_res.text}")
        return None

    data = render_res.json()
    filename = data["filename"]
    tempo = data["tempo_segundos"]
    sz_mb = data["tamanho_mb"]
    print(f"\n🎉 VÍDEO CONCLUÍDO NAS GPUS EM {tempo}s ({sz_mb} MB)!")

    # 3. Download Imediato do .mp4
    dl_url = f"{tunnel_url}{data['download_url']}"
    dest_local = os.path.join(LOCAL_OUT, filename)
    print(f"📥 Baixando {filename} direto para {dest_local}...")

    dl_stream = requests.get(dl_url, stream=True)
    with open(dest_local, "wb") as f:
        for chunk in dl_stream.iter_content(chunk_size=1024*1024):
            f.write(chunk)

    print(f"✅ Arquivo salvo localmente: {dest_local} ({round(os.path.getsize(dest_local)/(1024*1024), 2)} MB)")

    # 4. Cópia automática para o Google Drive
    dest_gdrive = os.path.join(GDRIVE_OUT, filename)
    if os.path.exists(GDRIVE_OUT):
        try:
            shutil.copy2(dest_local, dest_gdrive)
            print(f"☁️ Espelho copiado para o Google Drive: {dest_gdrive}")
        except Exception as e:
            print(f"Nota na cópia para Drive: {e}")

    print("\n" + "=" * 70)
    print(f"🏁 CICLO FINALIZADO COM SUCESSO EM {round(time.time() - t0, 1)}s!")
    print("=" * 70)
    return dest_local

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Disparador Instantâneo Kaggle 32GB")
    parser.add_argument("--url", help="URL do túnel (ex: https://xxx.trycloudflare.com)")
    parser.add_argument("--perfil", default="novela_tiktok", choices=["novela_tiktok", "canal_dark_20min"], help="Perfil de renderização")
    parser.add_argument("--prompt", default="Cinematic dramatic scene of Helena and Marcos confrontation, tears, 35mm lighting, photorealistic, 1080p")
    parser.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"], help="Proporção da tela")
    parser.add_argument("--steps", default=6, type=int, help="Passos de inferência (padrão 6 ultra-rápido)")

    args = parser.parse_args()
    try:
        active_url = find_active_tunnel_url(args.url)
        send_render_request(active_url, args.perfil, args.prompt, args.aspect, args.steps)
    except Exception as err:
        print(f"\n❌ Falha: {err}")
