#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
TESTE 3: SDXL TURBO - DIRETOR DE IMAGEM & FOTOGRAFIA CINEMATOGRÁFICA
Testa o modelo SDXL Turbo gerando imagem fotorrealista 1024x1024 em alta resolução.
================================================================================
"""

import os
import sys
import time
import torch
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_locator import find_model_path
from vram_manager import VRAMManager

OUTPUT_DIR = os.path.abspath("outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_test():
    print("=" * 65)
    print("🧪 INICIANDO TESTE 3: SDXL TURBO (STABILITY AI)")
    print("🎯 Objetivo: Geração de Imagem Cinematográfica 1024x1024 em Alta Definição")
    print("=" * 65)

    VRAMManager.audit("Pré-Carregamento SDXL Turbo")
    model_path = find_model_path("sdxl")
    print(f"📦 Caminho do Modelo: {model_path}")

    try:
        from diffusers import AutoPipelineForText2Image
    except ImportError:
        print("⚠️ Instalando biblioteca diffusers e accelerate...")
        os.system(f"{sys.executable} -m pip install -q --no-warn-script-location diffusers accelerate")
        from diffusers import AutoPipelineForText2Image

    start_load = time.time()
    print("⏳ Carregando Pipeline SDXL Turbo em FP16...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    # Carrega pipeline oficial
    pipe = AutoPipelineForText2Image.from_pretrained(
        model_path,
        torch_dtype=torch_dtype,
        variant="fp16" if torch.cuda.is_available() else None
    ).to(device)

    load_time = round(time.time() - start_load, 2)
    print(f"✅ SDXL Turbo Carregado em {load_time}s!")
    VRAMManager.audit("SDXL Turbo em VRAM")

    prompt = (
        "Cinematic 8k photorealistic sci-fi masterpiece, futuristic quantum datacenter interior, "
        "towering holographic server monoliths, intense cyan and electric amber fiber optic cables, "
        "atmospheric volumetric dust particles, anamorphic lens flare, Unreal Engine 5 render, award winning photography"
    )
    print("\n🎨 Gerando Imagem Cinematográfica em 1024x1024...")
    print(f"Prompt: \"{prompt[:90]}...\"")
    start_infer = time.time()

    with torch.inference_mode():
        image = pipe(
            prompt=prompt,
            num_inference_steps=2,
            guidance_scale=0.0,
            width=1024,
            height=1024
        ).images[0]

    infer_time = round(time.time() - start_infer, 2)
    print(f"✅ Imagem Gerada em {infer_time}s!")

    out_png = os.path.join(OUTPUT_DIR, "test_3_cena_sdxl.png")
    image.save(out_png)

    # Verificação de qualidade do arquivo
    if os.path.exists(out_png):
        w, h = image.size
        size_kb = os.path.getsize(out_png) / 1024
        print(f"📊 Métricas da Imagem: Resolução: {w}x{h} | Tamanho: {size_kb:.1f} KB")
        print(f"💾 Evidência salva em: {out_png}")
    else:
        raise RuntimeError("Arquivo de imagem SDXL não foi gerado!")

    # Liberação cirúrgica de memória
    print("\n🧹 Descarregando pipeline SDXL Turbo da VRAM...")
    del pipe
    VRAMManager.purge()
    print("🎉 TESTE 3 (SDXL TURBO) FINALIZADO COM SUCESSO!\n")
    return out_png

if __name__ == "__main__":
    run_test()
