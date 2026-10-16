#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
TESTE 5: STABLE VIDEO DIFFUSION (SVD-XT) - GERAÇÃO DE VÍDEO REALISTA
Gera vídeo com movimento neural real (não é foto estática nem zoom digital).
Usa difusão temporal de 25 quadros em alta resolução no Kaggle Dual T4 (32GB VRAM).
================================================================================
"""

import os
import sys
import time
import subprocess
import torch
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_locator import find_model_path
from vram_manager import VRAMManager

OUTPUT_DIR = os.path.abspath("outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_test():
    print("=" * 65)
    print("🎬 INICIANDO TESTE 5: GERAÇÃO DE VÍDEO REALISTA COM IA (SVD-XT)")
    print("🎯 Objetivo: Difusão Temporal de 25 Quadros com Movimento e Física Real")
    print("=" * 65)

    VRAMManager.audit("Pré-Carregamento SVD-XT")
    model_path = find_model_path("svd")
    print(f"📦 Caminho do Modelo de Vídeo: {model_path}")

    # Seleciona imagem de entrada (frame chave gerado pelo SDXL)
    candidate_images = [
        os.path.join(OUTPUT_DIR, "test_3_cena_sdxl.png"),
        "D:/Kaggles/Outputs/miniserie_ia/cenas/cena_01.jpg",
        "cenas/cena_01.jpg"
    ]
    input_image_path = None
    for cand in candidate_images:
        if os.path.exists(cand):
            input_image_path = os.path.abspath(cand)
            break

    if not input_image_path:
        # Se não houver imagem gerada ainda, cria uma tela base para o teste
        print("Criando frame base para o teste de vídeo...")
        base_img = Image.new("RGB", (1024, 576), color=(15, 25, 45))
        input_image_path = os.path.join(OUTPUT_DIR, "frame_base_teste.png")
        base_img.save(input_image_path)

    print(f"🖼️ Imagem Âncora (Keyframe): {input_image_path}")
    image = Image.open(input_image_path).convert("RGB")
    image = image.resize((1024, 576))  # Resolução padrão do SVD-XT

    try:
        from diffusers import StableVideoDiffusionPipeline
        from diffusers.utils import export_to_video
    except ImportError:
        print("⚠️ Instalando bibliotecas diffusers e accelerate...")
        os.system(f"{sys.executable} -m pip install -q --no-warn-script-location diffusers accelerate")
        from diffusers import StableVideoDiffusionPipeline
        from diffusers.utils import export_to_video

    start_load = time.time()
    print("⏳ Carregando Pipeline Stable Video Diffusion XT em FP16...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    pipe = StableVideoDiffusionPipeline.from_pretrained(
        model_path,
        torch_dtype=torch_dtype,
        variant="fp16" if torch.cuda.is_available() else None
    )
    if torch.cuda.is_available():
        pipe.enable_model_cpu_offload()  # Otimiza o uso de VRAM dividindo com a RAM do sistema
    else:
        pipe = pipe.to(device)

    load_time = round(time.time() - start_load, 2)
    print(f"✅ SVD-XT Carregado em {load_time}s!")
    VRAMManager.audit("SVD-XT em VRAM")

    print("\n🌪️ Gerando Difusão Temporal de Vídeo (25 Quadros de Movimento Fluido)...")
    print("Configurações: motion_bucket_id=127 (movimento dinâmico), decode_chunk_size=8, fps=7")
    start_infer = time.time()

    with torch.inference_mode():
        frames = pipe(
            image,
            decode_chunk_size=8,
            motion_bucket_id=127,
            fps=7,
            noise_aug_strength=0.02
        ).frames[0]

    infer_time = round(time.time() - start_infer, 2)
    print(f"✅ {len(frames)} Quadros de Vídeo Gerados com Sucesso em {infer_time}s!")

    # Exporta os frames brutos para MP4
    raw_video = os.path.join(OUTPUT_DIR, "test_5_video_bruto_svd.mp4")
    export_to_video(frames, raw_video, fps=7)
    print(f"🎥 Vídeo bruto salvo em: {raw_video}")

    # Interpolação de movimento cinematográfico a 24 FPS
    smooth_video = os.path.join(OUTPUT_DIR, "test_5_video_realista_24fps.mp4")
    cmd_smooth = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-vf", "minterpolate='fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1'",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        smooth_video
    ]
    try:
        subprocess.run(cmd_smooth, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        final_video_path = smooth_video
        print(f"✨ Vídeo interpolado a 24 FPS (movimento ultra suave): {smooth_video}")
    except Exception:
        final_video_path = raw_video

    # Liberação cirúrgica de memória
    print("\n🧹 Descarregando pipeline de vídeo SVD-XT da VRAM...")
    del pipe
    del frames
    VRAMManager.purge()

    print(f"💾 VÍDEO REALISTA CONCLUÍDO: {final_video_path} ({os.path.getsize(final_video_path)} bytes)")
    print("🎉 TESTE 5 (VÍDEO REALISTA IA) FINALIZADO COM SUCESSO!\n")
    return final_video_path

if __name__ == "__main__":
    run_test()
