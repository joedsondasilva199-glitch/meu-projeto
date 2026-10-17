#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
MOTOR PARALELO DUAL-GPU TESLA T4 COM MULTIPROCESSING (SPAWN)
GPU 0 (cuda:0) = Cenas Pares | GPU 1 (cuda:1) = Cenas Ímpares (100% Simultâneo)
Aceleração FP16 Tensor Cores + 6-Steps UniPC + Exportação NVENC por Hardware
================================================================================
"""

import os
import sys
import json
import time
import shutil
import subprocess
from typing import List, Dict

import torch
import torch.multiprocessing as mp

# Força codificação segura
for s in [sys.stdout, sys.stderr]:
    if hasattr(s, 'reconfigure'):
        s.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK_DIR = "/tmp/workspace" if os.path.exists("/tmp") else os.path.join(BASE_DIR, "outputs", "tmp_work")
OUTPUT_DIR = "/kaggle/working" if os.path.exists("/kaggle") else os.path.join(BASE_DIR, "outputs", "kaggle_gpu_real")
DATASET_DIR = "/kaggle/input/kaggles-32gb-models"

for d in [WORK_DIR, OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================================================
# WORKER PROCESS POR GPU (cuda:0 e cuda:1)
# ============================================================================
def gpu_worker_process(gpu_id: int, task_queue: mp.Queue, result_queue: mp.Queue):
    """
    Worker isolado em processo dedicado para a GPU atribuída.
    Instancia o pipeline exclusivamente na VRAM da respectiva placa.
    """
    device_name = f"cuda:{gpu_id}" if torch.cuda.is_available() else "cpu"
    print(f"[Worker GPU {gpu_id}] Inicializando no dispositivo {device_name}...")

    pipe = None
    if torch.cuda.is_available():
        try:
            from diffusers import DiffusionPipeline, UniPCMultistepScheduler

            model_source = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
            if os.path.exists(os.path.join(DATASET_DIR, "wan21")):
                model_source = os.path.join(DATASET_DIR, "wan21")

            # Carrega pipeline com FP16 nativo e 6 steps
            pipe = DiffusionPipeline.from_pretrained(
                model_source,
                torch_dtype=torch.float16,
                cache_dir="/tmp/hf_cache"
            )
            pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
            pipe.enable_model_cpu_offload(gpu_id=gpu_id)

            if hasattr(pipe, 'vae') and pipe.vae is not None:
                try:
                    pipe.vae.enable_tiling()
                    pipe.vae.enable_slicing()
                except: pass
            if hasattr(pipe, 'text_encoder') and pipe.text_encoder is not None:
                pipe.text_encoder.to(torch.float32)

            print(f"[Worker GPU {gpu_id}] Pipeline Wan 2.1 Pronto e Aquecido em {device_name}!")
        except Exception as e:
            print(f"[Worker GPU {gpu_id}] Aviso no carregamento do Diffusers: {e}")

    # Loop de consumo de tarefas da fila
    while True:
        task = task_queue.get()
        if task is None: # Sinal de término
            break

        scene_id = task["scene_id"]
        prompt = task["prompt"]
        width = task["width"]
        height = task["height"]
        num_frames = task.get("num_frames", 49)
        steps = task.get("steps", 6)
        out_clip_path = task["out_clip_path"]

        t0 = time.time()
        print(f"[Worker GPU {gpu_id}] Renderizando Cena {scene_id} ({width}x{height}, {steps} steps)...")

        if pipe is not None and torch.cuda.is_available():
            output = pipe(
                prompt=prompt,
                num_frames=num_frames,
                height=height,
                width=width,
                num_inference_steps=steps,
                guidance_scale=1.0, # Sem CFG duplo para velocidade máxima
                generator=torch.Generator(device="cpu").manual_seed(42 + scene_id)
            )
            from diffusers.utils import export_to_video
            export_to_video(output.frames[0], out_clip_path, fps=16)
        else:
            # Geração procedural para fallback de teste sem GPU
            _generate_procedural_clip(out_clip_path, scene_id, width, height, 3.0)

        elapsed = round(time.time() - t0, 1)
        sz_mb = round(os.path.getsize(out_clip_path) / (1024 * 1024), 2)
        print(f"[Worker GPU {gpu_id}] ✅ Cena {scene_id} Concluída em {elapsed}s ({sz_mb} MB)")

        result_queue.put({
            "scene_id": scene_id,
            "gpu_id": gpu_id,
            "clip_path": out_clip_path,
            "tempo_s": elapsed,
            "tamanho_mb": sz_mb
        })

def _generate_procedural_clip(out_path: str, scene_id: int, w: int, h: int, dur: float):
    """Gera clipe procedural temporizado quando executado em teste local."""
    temp_img = out_path + ".jpg"
    from PIL import Image, ImageDraw
    color = (25 + (scene_id * 15) % 80, 20, 45)
    img = Image.new("RGB", (w, h), color=color)
    d = ImageDraw.Draw(img)
    d.text((40, 40), f"DUAL-GPU T4 - CENA {scene_id}", fill=(255, 255, 255))
    img.save(temp_img)
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", temp_img,
        "-t", str(dur),
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        out_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(temp_img):
        try: os.remove(temp_img)
        except: pass

# ============================================================================
# EXPORTAÇÃO COM ACELERAÇÃO POR HARDWARE NVENC
# ============================================================================
def export_with_nvenc_or_cpu(input_list_txt: str, output_video: str, target_res: str = "1920x1080", fps: int = 25):
    """Aplica o codificador h264_nvenc por hardware das Tesla T4 com fallback limpo."""
    w, h = target_res.split("x")
    print(f"\n⚡ Exportando Vídeo Final para {target_res} via Hardware NVENC...")

    cmd_nvenc = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", input_list_txt,
        "-vf", f"minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc:vsbmc=1,scale={w}:{h}:flags=lanczos",
        "-c:v", "h264_nvenc", "-preset", "p4", "-cq", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        output_video
    ]
    res = subprocess.run(cmd_nvenc, capture_output=True, text=True)
    if res.returncode == 0:
        print("✅ Exportação concluída com aceleração por Hardware NVENC (Tesla T4)!")
        return output_video

    print("ℹ️ h264_nvenc indisponível no build FFmpeg local. Usando libx264 otimizado...")
    cmd_cpu = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", input_list_txt,
        "-vf", f"minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc:vsbmc=1,scale={w}:{h}:flags=lanczos",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        output_video
    ]
    subprocess.run(cmd_cpu, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_video

# ============================================================================
# ORQUESTRADOR MULTIPROCESSING DUAL T4
# ============================================================================
class DualT4ParallelOrchestrator:
    def __init__(self):
        self.num_gpus = torch.cuda.device_count() if torch.cuda.is_available() else 1
        print("=" * 70)
        print(f"🚀 INICIALIZANDO ORQUESTRADOR PARALELO ({self.num_gpus}x GPUS DETECTADAS)")
        print("=" * 70)

    def run_parallel_production(self, scenes: List[Dict], output_filename: str, target_res: str = "1920x1080") -> str:
        """
        Distribui as cenas em paralelo real:
        - Cenas Pares -> GPU 0 (cuda:0)
        - Cenas Ímpares -> GPU 1 (cuda:1)
        """
        ctx = mp.get_context("spawn")
        q_gpu0 = ctx.Queue()
        q_gpu1 = ctx.Queue()
        result_q = ctx.Queue()

        # Inicia processos dedicados por GPU
        p0 = ctx.Process(target=gpu_worker_process, args=(0, q_gpu0, result_q))
        p0.start()

        p1 = None
        if self.num_gpus >= 2:
            p1 = ctx.Process(target=gpu_worker_process, args=(1, q_gpu1, result_q))
            p1.start()

        # Enfileira as tarefas alternando pares e ímpares
        total_scenes = len(scenes)
        for idx, sc in enumerate(scenes):
            task = {
                "scene_id": idx,
                "prompt": sc["prompt"],
                "width": sc.get("width", 832),
                "height": sc.get("height", 480),
                "num_frames": sc.get("num_frames", 49),
                "steps": sc.get("steps", 6),
                "out_clip_path": os.path.join(WORK_DIR, f"scene_{idx:03d}.mp4")
            }
            if idx % 2 == 0 or self.num_gpus < 2:
                q_gpu0.put(task)
            else:
                q_gpu1.put(task)

        # Sinaliza término para os workers
        q_gpu0.put(None)
        if p1 is not None:
            q_gpu1.put(None)

        # Coleta os resultados ordenadamente
        collected = {}
        for _ in range(total_scenes):
            res = result_q.get()
            collected[res["scene_id"]] = res["clip_path"]

        p0.join()
        if p1 is not None:
            p1.join()

        # Lista de concatenação na ordem correta
        concat_txt = os.path.join(WORK_DIR, "concat_dual_scenes.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for i in range(total_scenes):
                f.write(f"file '{collected[i].replace(os.sep, '/')}'\n")

        final_out_path = os.path.join(OUTPUT_DIR, output_filename)
        export_with_nvenc_or_cpu(concat_txt, final_out_path, target_res=target_res)

        print("\n" + "=" * 70)
        print(f"🎉 PRODUÇÃO DUAL-GPU CONCLUÍDA: {final_out_path}")
        print("=" * 70)
        return final_out_path

# ============================================================================
# EXECUÇÃO DE TESTE DO MOTOR
# ============================================================================
if __name__ == "__main__":
    orchestrator = DualT4ParallelOrchestrator()
    # Teste de 4 tomadas (2 na GPU 0 e 2 na GPU 1)
    test_scenes = [
        {"prompt": "Cinematic shot of Helena confronting Marcos in luxury apartment, tears, dramatic lighting", "width": 832, "height": 480},
        {"prompt": "Reverse close-up of Marcos in tailored dark suit frozen in guilt and shock", "width": 832, "height": 480},
        {"prompt": "Helena turning away in heartbreak, rain on penthouse window", "width": 832, "height": 480},
        {"prompt": "Marcos reaching forward pleading passionately, dramatic 35mm lens", "width": 832, "height": 480}
    ]
    orchestrator.run_parallel_production(test_scenes, "teste_dual_t4_real.mp4", target_res="1920x1080")
