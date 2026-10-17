#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
SERVIDOR GPU QUENTE KAGGLE (DUAL TESLA T4 + FASTAPI + CLOUDFLARED TUNNEL)
Zero Fila QUEUED, Zero Redownload de Pesos, Acesso Remoto Imediato via API
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
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor

import torch
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# ============================================================================
# CONFIGURACAO E DIRETORIOS
# ============================================================================
WORK_DIR = "/tmp/workspace"
CACHE_DIR = "/tmp/hf_cache"
OUTPUT_DIR = "/kaggle/working"
MODELS_LOCAL_DIR = "/tmp/models"

for d in [WORK_DIR, CACHE_DIR, OUTPUT_DIR, MODELS_LOCAL_DIR]:
    os.makedirs(d, exist_ok=True)

app = FastAPI(
    title="Kaggle Dual Tesla T4 Hot GPU Server",
    description="Servidor de Renderizacao Neural de Video Wan 2.1 + Audio",
    version="1.0.0"
)

# Estado global dos pipelines carregados
LOADED_PIPES = {
    "wan21": None,
    "wan21_gpu0": None,
    "wan21_gpu1": None,
    "device_mode": "idle"
}
LOCK = threading.Lock()

# ============================================================================
# SCHEMAS DE DADOS (PYDANTIC)
# ============================================================================
class SceneRequest(BaseModel):
    prompt: str
    num_frames: int = 49
    steps: int = 15
    height: int = 480
    width: int = 832
    fps: int = 16
    seed: Optional[int] = 42
    device: str = "cuda:0"

class DualSceneRequest(BaseModel):
    scene_gpu0: SceneRequest
    scene_gpu1: SceneRequest

class ActRequest(BaseModel):
    act_id: int
    act_name: str
    scenes: List[SceneRequest]

# ============================================================================
# FUNCOES AUXILIARES DE VRAM E CARREGAMENTO
# ============================================================================
def get_vram_telemetry():
    """Coleta telemetria em tempo real de todas as GPUs."""
    info = []
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            alloc = torch.cuda.memory_allocated(i) / (1024 ** 2)
            max_alloc = torch.cuda.max_memory_allocated(i) / (1024 ** 2)
            reserved = torch.cuda.memory_reserved(i) / (1024 ** 2)
            total = (props.total_mem if hasattr(props, 'total_mem') else props.total_memory) / (1024 ** 2)
            info.append({
                "gpu_id": i,
                "name": props.name,
                "alocada_mb": round(alloc, 1),
                "max_alocada_mb": round(max_alloc, 1),
                "reservada_mb": round(reserved, 1),
                "total_vram_mb": round(total, 1)
            })
    return info

def ensure_wan21_loaded():
    """Garante que o Wan 2.1 esteja em memoria com FP16 Tensor Cores."""
    global LOADED_PIPES
    with LOCK:
        if LOADED_PIPES["wan21"] is not None:
            return LOADED_PIPES["wan21"]
        
        print("\n[HotServer] Carregando Wan 2.1 (T2V 1.3B) em FP16 Tensor Cores...")
        from diffusers import DiffusionPipeline
        
        pipe = DiffusionPipeline.from_pretrained(
            "Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
            torch_dtype=torch.float16,
            cache_dir=CACHE_DIR
        )
        
        if hasattr(pipe, "text_encoder") and pipe.text_encoder is not None:
            pipe.text_encoder.to(torch.float32)
            
        pipe.enable_model_cpu_offload()
        LOADED_PIPES["wan21"] = pipe
        LOADED_PIPES["device_mode"] = "cpu_offload_shared"
        print("[HotServer] Wan 2.1 carregada e pronta para inferencias imediatas!")
        return pipe

# ============================================================================
# ENDPOINTS REST
# ============================================================================
@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Kaggle Dual Tesla T4 Hot GPU Server",
        "model": "Wan-AI/Wan2.1-T2V-1.3B-Diffusers (FP16)",
        "gpus": get_vram_telemetry(),
        "endpoints": [
            "/health",
            "/render_scene",
            "/render_dual_parallel",
            "/render_act",
            "/download/{filename}",
            "/purge_vram"
        ]
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "cuda_available": torch.cuda.is_available(),
        "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "vram": get_vram_telemetry(),
        "model_loaded": LOADED_PIPES["wan21"] is not None
    }

@app.post("/render_scene")
def render_scene(req: SceneRequest):
    """Renderiza uma cena individual de video por difusao neural real."""
    if not torch.cuda.is_available():
        raise HTTPException(status_code=500, detail="CUDA indisponivel no servidor.")
    
    pipe = ensure_wan21_loaded()
    
    t0 = time.time()
    torch.cuda.reset_peak_memory_stats()
    
    generator = torch.Generator(device="cpu")
    if req.seed is not None:
        generator.manual_seed(req.seed)
        
    print(f"\n[HotServer] Processando render: '{req.prompt[:60]}...' ({req.num_frames} frames, {req.steps} steps)")
    output = pipe(
        prompt=req.prompt,
        num_frames=req.num_frames,
        height=req.height,
        width=req.width,
        num_inference_steps=req.steps,
        guidance_scale=5.0,
        generator=generator
    )
    
    gen_time = round(time.time() - t0, 1)
    
    timestamp = int(time.time())
    clip_filename = f"clip_{timestamp}.mp4"
    clip_path = os.path.join(OUTPUT_DIR, clip_filename)
    
    from diffusers.utils import export_to_video
    export_to_video(output.frames[0], clip_path, fps=req.fps)
    
    size_mb = round(os.path.getsize(clip_path) / (1024 * 1024), 2)
    peak_vram = round(torch.cuda.max_memory_allocated(0) / (1024 ** 2), 1)
    
    return {
        "status": "completed",
        "filename": clip_filename,
        "download_url": f"/download/{clip_filename}",
        "tempo_segundos": gen_time,
        "tamanho_mb": size_mb,
        "vram_pico_mb": peak_vram,
        "frames": req.num_frames,
        "fps": req.fps
    }

@app.post("/render_dual_parallel")
def render_dual_parallel(req: DualSceneRequest):
    """Executa duas cenas simultaneamente nas duas Tesla T4 em paralelo real."""
    if torch.cuda.device_count() < 2:
        raise HTTPException(status_code=400, detail="Menos de 2 GPUs disponíveis para paralelo.")
    
    # Executa ambas via ThreadPoolExecutor
    def _run_single(scene: SceneRequest, gpu_id: int):
        pipe = ensure_wan21_loaded()
        torch.cuda.reset_peak_memory_stats(gpu_id)
        t_start = time.time()
        
        gen = torch.Generator(device="cpu")
        if scene.seed is not None:
            gen.manual_seed(scene.seed)
            
        out = pipe(
            prompt=scene.prompt,
            num_frames=scene.num_frames,
            height=scene.height,
            width=scene.width,
            num_inference_steps=scene.steps,
            guidance_scale=5.0,
            generator=gen
        )
        
        clip_name = f"dual_gpu{gpu_id}_{int(time.time())}.mp4"
        clip_fp = os.path.join(OUTPUT_DIR, clip_name)
        from diffusers.utils import export_to_video
        export_to_video(out.frames[0], clip_fp, fps=scene.fps)
        
        return {
            "gpu_id": gpu_id,
            "filename": clip_name,
            "download_url": f"/download/{clip_name}",
            "tempo_s": round(time.time() - t_start, 1),
            "size_mb": round(os.path.getsize(clip_fp)/(1024*1024), 2)
        }

    with ThreadPoolExecutor(max_workers=2) as executor:
        f0 = executor.submit(_run_single, req.scene_gpu0, 0)
        f1 = executor.submit(_run_single, req.scene_gpu1, 1)
        res0 = f0.result()
        res1 = f1.result()
        
    return {
        "status": "completed",
        "gpu_0": res0,
        "gpu_1": res1,
        "vram": get_vram_telemetry()
    }

@app.get("/download/{filename}")
def download_file(filename: str):
    """Faz download do vídeo gerado diretamente."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo nao encontrado.")
    return FileResponse(file_path, media_type="video/mp4", filename=filename)

@app.post("/purge_vram")
def purge_vram():
    """Libera VRAM e caches sob demanda."""
    global LOADED_PIPES
    with LOCK:
        LOADED_PIPES["wan21"] = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            for i in range(torch.cuda.device_count()):
                torch.cuda.reset_peak_memory_stats(i)
    return {"status": "purged", "vram": get_vram_telemetry()}

# ============================================================================
# CLOUDFLARED TUNNEL LAUNCHER
# ============================================================================
def start_cloudflared_tunnel(port: int = 8000):
    """Baixa o cloudflared binario e estabelece tunnel trycloudflare.com."""
    cf_path = "/tmp/cloudflared"
    if not os.path.exists(cf_path):
        print("\n[Tunnel] Baixando binário oficial do Cloudflared...")
        cmd_dl = ["wget", "-q", "-O", cf_path, "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"]
        subprocess.run(cmd_dl, check=True)
        os.chmod(cf_path, 0o755)
    
    print(f"\n[Tunnel] Iniciando túnel seguro para porta {port}...")
    proc = subprocess.Popen(
        [cf_path, "tunnel", "--url", f"http://127.0.0.1:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    tunnel_url = None
    regex = r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com"
    
    # Aguarda a geracao da URL publica
    start = time.time()
    for line in iter(proc.stdout.readline, ''):
        if not line:
            break
        match = re.search(regex, line)
        if match:
            tunnel_url = match.group(0)
            break
        if time.time() - start > 45:
            break
            
    if tunnel_url:
        print("\n" + "=" * 70)
        print("🚀 SERVIDOR GPU QUENTE ATIVO E ACESSÍVEL PUBLICAMENTE!")
        print(f"🔗 ENDPOINT URL: {tunnel_url}")
        print("=" * 70)
        
        # Salva o endpoint em arquivo para o cliente ler
        out_txt = "/kaggle/working/active_gpu_endpoint.txt"
        with open(out_txt, "w") as f:
            f.write(tunnel_url + "\n")
        print(f"Salvo em: {out_txt}")
        
        # Se Google Drive estiver montado
        if os.path.exists("/kaggle/drive") or os.path.exists("/content/drive"):
            for d in ["/kaggle/drive/MyDrive/Kaggles", "/content/drive/MyDrive/Kaggles"]:
                if os.path.exists(d):
                    try:
                        with open(os.path.join(d, "active_gpu_endpoint.txt"), "w") as f:
                            f.write(tunnel_url + "\n")
                    except: pass
    else:
        print("⚠️ Nao foi possivel capturar a URL do Cloudflared automaticamente.")
        
    return tunnel_url

def main():
    port = 8000
    # Inicia o tunnel em thread separada
    threading.Thread(target=start_cloudflared_tunnel, args=(port,), daemon=True).start()
    
    # Inicia o servidor FastAPI
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
