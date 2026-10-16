#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tunnel.py
=========
Inicia um Cloudflare Tunnel seguro e gratuito para expor a Stack de Agentes
(API, The Sims e Super Mario) para a internet com SSL automático (HTTPS).
"""

import os
import sys
import re
import subprocess
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CLOUDFLARED_BIN = os.path.join(os.path.dirname(__file__), "cloudflared.exe")

def start_tunnel(port: int = 8000):
    if not os.path.exists(CLOUDFLARED_BIN):
        print("❌ cloudflared.exe não encontrado!")
        sys.exit(1)

    print(f"🚀 Iniciando túnel seguro Cloudflare para a porta {port}...")
    cmd = [CLOUDFLARED_BIN, "tunnel", "--url", f"http://127.0.0.1:{port}"]

    # Cloudflare emite a URL no stderr
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    tunnel_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    start_time = time.time()
    while time.time() - start_time < 25:
        line = proc.stderr.readline()
        if not line:
            time.sleep(0.1)
            continue
        
        match = url_pattern.search(line)
        if match:
            tunnel_url = match.group(0)
            break

    if tunnel_url:
        print("\n==================================================================")
        print("🎉 TÚNEL PÚBLICO HTTPS ATIVO COM SUCESSO!")
        print("==================================================================")
        print(f"🌍 URL Principal:     {tunnel_url}")
        print(f"🎮 The Sims HQ:       {tunnel_url}/office")
        print(f"🍄 Super Mario:       {tunnel_url}/mario")
        print(f"📑 API Swagger:       {tunnel_url}/docs")
        print(f"🩺 Healthcheck:       {tunnel_url}/api/health")
        print("==================================================================\n")

        # Salva para referência
        with open("tunnel_url.txt", "w", encoding="utf-8") as f:
            f.write(tunnel_url)

        # Mantém processo rodando
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("Encerrando túnel...")
            proc.terminate()
    else:
        print("⚠️ Não foi possível capturar a URL do túnel em tempo hábil.")

if __name__ == "__main__":
    start_tunnel(8000)
