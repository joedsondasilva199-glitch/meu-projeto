#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
KAGGLE 32GB HOT SERVER (2x TESLA T4 + FASTAPI + CLOUDFLARE TUNNEL)
Zero Fila QUEUED - Zero Tempo de Boot - Modelos Pré-Aquecidos na VRAM
================================================================================
"""

import os
import re
import sys
import gc
import json
import time
import shutil
import asyncio
import threading
import subprocess
from datetime import datetime
from typing import List, Dict, Optional

import torch
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Força codificação segura
for s in [sys.stdout, sys.stderr]:
    if hasattr(s, 'reconfigure'):
        s.reconfigure(encoding='utf-8', errors='replace')

WORK_DIR = "/tmp/workspace"
CACHE_DIR = "/tmp/hf_cache"
OUTPUT_DIR = "/kaggle/working"
DATASET_DIR = "/kaggle/input/kaggles-32gb-models"

for d in [WORK_DIR, CACHE_DIR, OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)

app = FastAPI(
    title="Kaggle 32GB Dual T4 Hot Server",
    description="Servidor de Renderização de Vídeos em Escala (TikTok + Canal Dark 20min)",
    version="2.0.0"
)

# Estado Global de Modelos nas GPUs
ENGINES = {
    "gpu0_pipe": None,
    "gpu1_pipe": None,
    "lock_gpu0": threading.Lock(),
    "lock_gpu1": threading.Lock(),
    "ready": False
}

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================
class RenderJobRequest(BaseModel):
    job_id: Optional[str] = None
    perfil: str = "novela_tiktok" # "novela_tiktok" ou "canal_dark_20min"
    prompt: str
    aspect_ratio: str = "9:16"    # "9:16" (TikTok) ou "16:9" (Dark/YouTube)
    num_frames: int = 49
    steps: int = 6                # Modo Ultra-Turbo (UniPC 6-steps)
    personagens: Optional[List[Dict]] = None

class BatchScenesRequest(BaseModel):
    scenes: List[RenderJobRequest]

# ============================================================================
# INICIALIZAÇÃO DE MODELOS EM FP16 (TENSOR CORES T4)
# ============================================================================
def init_models_dual_gpu():
    """Pré-aquece os pipelines nas 2x Tesla T4 em FP16 nativo com 6 steps."""
    global ENGINES
    if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
        print("⚠️ CUDA indisponível ou GPUs insuficientes.")
        return

    print("=" * 70)
    print("🔥 PRÉ-AQUECENDO MODELOS NAS 2x TESLA T4 (32 GB VRAM)")
    print("=" * 70)

    try:
        from diffusers import DiffusionPipeline, UniPCMultistepScheduler

        # Identifica se pesos estão no Kaggle Dataset local ou baixa no cache
        model_source = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
        if os.path.exists(os.path.join(DATASET_DIR, "wan21")):
            model_source = os.path.join(DATASET_DIR, "wan21")
            print(f"📦 Usando pesos montados do Kaggle Dataset: {model_source}")

        # GPU 0 Pipeline (FP16 nativo com UniPC 6-steps)
        print("🔹 Inicializando Pipeline GPU 0 (cuda:0)...")
        pipe0 = DiffusionPipeline.from_pretrained(
            model_source,
            torch_dtype=torch.float16,
            cache_dir=CACHE_DIR
        )
        pipe0.scheduler = UniPCMultistepScheduler.from_config(pipe0.scheduler.config)
        pipe0.enable_model_cpu_offload(gpu_id=0)
        if hasattr(pipe0, 'vae') and pipe0.vae is not None:
            try:
                pipe0.vae.enable_tiling()
                pipe0.vae.enable_slicing()
            except: pass
        if hasattr(pipe0, 'text_encoder') and pipe0.text_encoder is not None:
            pipe0.text_encoder.to(torch.float32)
        ENGINES["gpu0_pipe"] = pipe0
        print("✅ GPU 0 Pronta e Aquecida!")

        # GPU 1 Pipeline se disponível
        if torch.cuda.device_count() >= 2:
            print("🔹 Inicializando Pipeline GPU 1 (cuda:1)...")
            pipe1 = DiffusionPipeline.from_pretrained(
                model_source,
                torch_dtype=torch.float16,
                cache_dir=CACHE_DIR
            )
            pipe1.scheduler = UniPCMultistepScheduler.from_config(pipe1.scheduler.config)
            pipe1.enable_model_cpu_offload(gpu_id=1)
            if hasattr(pipe1, 'vae') and pipe1.vae is not None:
                try:
                    pipe1.vae.enable_tiling()
                    pipe1.vae.enable_slicing()
                except: pass
            if hasattr(pipe1, 'text_encoder') and pipe1.text_encoder is not None:
                pipe1.text_encoder.to(torch.float32)
            ENGINES["gpu1_pipe"] = pipe1
            print("✅ GPU 1 Pronta e Aquecida!")

        ENGINES["ready"] = True
        print("🚀 SERVIDOR 32GB TOTALMENTE PRÉ-AQUECIDO!")

    except Exception as e:
        print(f"❌ Erro ao pré-aquecer modelos: {e}")

# ============================================================================
# ENDPOINTS REST DA API
# ============================================================================
@app.get("/")
def index():
    return {
        "server": "Kaggle 32GB Dual T4 Hot Server",
        "status": "online",
        "models_ready": ENGINES["ready"],
        "gpus": [
            {
                "id": i,
                "name": torch.cuda.get_device_name(i),
                "vram_allocated_mb": round(torch.cuda.memory_allocated(i)/(1024**2), 1),
                "vram_max_mb": round(torch.cuda.max_memory_allocated(i)/(1024**2), 1)
            }
            for i in range(torch.cuda.device_count())
        ] if torch.cuda.is_available() else []
    }

@app.get("/health")
def health():
    return index()

@app.post("/render")
def render_job(job: RenderJobRequest):
    """Renderiza um vídeo individual via Wan 2.1 em FP16 (6 steps sem CFG duplo)."""
    if not ENGINES["ready"]:
        init_models_dual_gpu()

    job_id = job.job_id or f"job_{int(time.time()*1000)}"
    t0 = time.time()

    # Define dimensões de acordo com o perfil
    if job.perfil == "novela_tiktok" or job.aspect_ratio == "9:16":
        width, height = 480, 832
        target_res = "1080x1920"
    else:
        width, height = 832, 480
        target_res = "1920x1080"

    # Seleciona GPU 0
    with ENGINES["lock_gpu0"]:
        pipe = ENGINES["gpu0_pipe"]
        if pipe is None:
            raise HTTPException(status_code=500, detail="Pipeline GPU 0 não inicializado.")

        print(f"\n[HotServer] Renderizando Job {job_id} ({job.perfil} | {job.steps} steps | guidance=1.0)...")
        output = pipe(
            prompt=job.prompt,
            num_frames=job.num_frames,
            height=height,
            width=width,
            num_inference_steps=job.steps,
            guidance_scale=1.0, # Desativa cálculo redundante de CFG
            generator=torch.Generator(device="cpu").manual_seed(42)
        )

    raw_clip = os.path.join(WORK_DIR, f"raw_{job_id}.mp4")
    final_video = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")

    from diffusers.utils import export_to_video
    export_to_video(output.frames[0], raw_clip, fps=16)

    # Upscale e Encoding acelerado por Hardware NVENC da Tesla T4
    w_out, h_out = target_res.split("x")
    cmd_nvenc = [
        "ffmpeg", "-y", "-i", raw_clip,
        "-vf", f"scale={w_out}:{h_out}:flags=lanczos",
        "-c:v", "h264_nvenc", "-preset", "p4", "-cq", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        final_video
    ]

    res_nvenc = subprocess.run(cmd_nvenc, capture_output=True, text=True)
    if res_nvenc.returncode != 0:
        # Fallback para libx264 se nvenc não estiver habilitado no build do ffmpeg
        cmd_cpu = [
            "ffmpeg", "-y", "-i", raw_clip,
            "-vf", f"scale={w_out}:{h_out}:flags=lanczos",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            final_video
        ]
        subprocess.run(cmd_cpu, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(raw_clip):
        try: os.remove(raw_clip)
        except: pass

    gen_time = round(time.time() - t0, 1)
    sz_mb = round(os.path.getsize(final_video) / (1024 * 1024), 2)
    print(f"🎉 Job {job_id} concluído em {gen_time}s ({sz_mb} MB) -> {final_video}")

    return {
        "status": "completed",
        "job_id": job_id,
        "filename": os.path.basename(final_video),
        "download_url": f"/download/{os.path.basename(final_video)}",
        "tempo_segundos": gen_time,
        "tamanho_mb": sz_mb,
        "resolucao": target_res
    }

@app.get("/download/{filename}")
def download_output(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return FileResponse(file_path, media_type="video/mp4", filename=filename)

# ============================================================================
# CLOUDFLARED TÚNEL AUTOMÁTICO
# ============================================================================
def launch_tunnel_and_publish(port: int = 8000):
    cf_path = "/tmp/cloudflared"
    if not os.path.exists(cf_path):
        print("\n[Tunnel] Baixando Cloudflared oficial...")
        subprocess.run(
            ["wget", "-q", "-O", cf_path, "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"],
            check=True
        )
        os.chmod(cf_path, 0o755)

    print(f"[Tunnel] Abrindo túnel para a porta {port}...")
    proc = subprocess.Popen(
        [cf_path, "tunnel", "--url", f"http://127.0.0.1:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    tunnel_url = None
    regex = r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com"
    start_t = time.time()

    for line in iter(proc.stdout.readline, ''):
        if not line: break
        m = re.search(regex, line)
        if m:
            tunnel_url = m.group(0)
            break
        if time.time() - start_t > 45:
            break

    if tunnel_url:
        print("\n" + "=" * 70)
        print("🚀 KAGGLE 32GB HOT SERVER ATIVO NO TÚNEL PÚBLICO!")
        print(f"🔗 URL: {tunnel_url}")
        print("=" * 70)

        # Salva o arquivo active_tunnel.json
        tunnel_info = {
            "url": tunnel_url,
            "status": "ready",
            "updated_at": datetime.now().isoformat(),
            "gpus": ["Tesla T4 (cuda:0)", "Tesla T4 (cuda:1)"],
            "vram_total_gb": 32
        }

        # 1. No /kaggle/working
        with open("/kaggle/working/active_tunnel.json", "w", encoding="utf-8") as f:
            json.dump(tunnel_info, f, indent=2)

        # 2. No repositório git clonado se existir
        git_target = "/tmp/meu-projeto/active_tunnel.json"
        if os.path.exists("/tmp/meu-projeto"):
            with open(git_target, "w", encoding="utf-8") as f:
                json.dump(tunnel_info, f, indent=2)
            try:
                subprocess.run(["git", "-C", "/tmp/meu-projeto", "config", "user.name", "Kaggle Hot Server"], check=True)
                subprocess.run(["git", "-C", "/tmp/meu-projeto", "config", "user.email", "joedsondasilva199@gmail.com"], check=True)
                subprocess.run(["git", "-C", "/tmp/meu-projeto", "add", "active_tunnel.json"], check=True)
                subprocess.run(["git", "-C", "/tmp/meu-projeto", "commit", "-m", "chore: atualizar active_tunnel.json"], check=True)
                token = os.environ.get("GITHUB_TOKEN", "")
                if not token:
                    try:
                        token = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
                    except Exception:
                        token = ""
                remote_url = f"https://{token}@github.com/joedsondasilva199-glitch/meu-projeto.git" if token else "https://github.com/joedsondasilva199-glitch/meu-projeto.git"
                subprocess.run(["git", "-C", "/tmp/meu-projeto", "push", remote_url, "main"], check=True)
                print("📡 active_tunnel.json publicado no GitHub com sucesso!")
            except Exception as e:
                print(f"Nota na publicação do túnel no Git: {e}")
    else:
        print("⚠️ Não foi possível obter URL do túnel automaticamente.")

def main():
    port = 8000
    # Inicializa modelos em background
    threading.Thread(target=init_models_dual_gpu, daemon=True).start()
    # Inicia túnel
    threading.Thread(target=launch_tunnel_and_publish, args=(port,), daemon=True).start()
    # Roda servidor
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
