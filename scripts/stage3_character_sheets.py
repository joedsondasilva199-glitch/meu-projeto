#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
ETAPA 3: COMPOSITOR DE CHARACTER SHEETS (@imagem1, @imagem2, @imagem4)
Monta a composição espacial 16:9 (832x480) com posicionamento cênico dos atores.
================================================================================
"""

import os
import sys
import torch
from PIL import Image, ImageDraw, ImageFilter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.abspath("tests"))
try:
    from vram_manager import VRAMManager
    from model_locator import find_model_path
except ImportError:
    class VRAMManager:
        @staticmethod
        def purge(): pass

OUTPUT_DIR = os.path.abspath("outputs/seedance_session")
ROSTOS_DIR = os.path.abspath("Referencias/rostos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_stage_character_sheets():
    print("=" * 70)
    print("🎨 ETAPA 3: COMPOSITOR DE CHARACTER SHEETS (POSICIONAMENTO 16:9)")
    print("=" * 70)

    # 1. Carrega as imagens de referência
    img1_path = os.path.join(ROSTOS_DIR, "imagem_1.png")
    img2_path = os.path.join(ROSTOS_DIR, "imagem_2.png")
    img4_path = os.path.join(ROSTOS_DIR, "imagem_4_criatura.png")

    print(f"🖼️ Referência 1 (Esquerda): {img1_path}")
    print(f"🖼️ Referência 2 (Direita): {img2_path}")
    print(f"🖼️ Referência 4 (Criatura Fundo): {img4_path}")

    # Dimensão padrão de entrada do Seedance 2.5 / Wan 2.1 (832x480)
    width, height = 832, 480

    # 2. Composição do Quadro-Base da Conversa (Take 1: Diálogo)
    base_shot = Image.new("RGB", (width, height), color=(15, 20, 30))
    draw_base = ImageDraw.Draw(base_shot)

    # Efeito de iluminação cinematográfica de floresta noturna
    for x in range(width):
        col_factor = 1.0 - abs(x - width // 2) / (width // 2)
        r = int(10 + col_factor * 15)
        g = int(18 + col_factor * 25)
        b = int(30 + col_factor * 45)
        draw_base.line([(x, 0), (x, height)], fill=(r, g, b))

    # Posiciona Personagem 1 à esquerda e Personagem 2 à direita
    draw_base.rectangle([(60, 80), (360, 440)], outline=(80, 140, 200), width=3)
    draw_base.text((80, 100), "@imagem_1: ANTONIO (ESQUERDA)", fill=(200, 230, 255))
    draw_base.text((80, 130), "Em alerta, olhando para a mata", fill=(160, 180, 200))

    draw_base.rectangle([(472, 80), (772, 440)], outline=(220, 100, 120), width=3)
    draw_base.text((492, 100), "@imagem_2: HELENA (DIREITA)", fill=(255, 210, 220))
    draw_base.text((492, 130), "Com lanterna, expressão de choque", fill=(200, 170, 180))

    quadro_base_path = os.path.join(OUTPUT_DIR, "quadro_base_832x480.png")
    base_shot.save(quadro_base_path)
    print(f"✅ Quadro-Base Composto: {quadro_base_path}")

    # 3. Composição do Quadro de Clímax (Take 2: Criatura ao Fundo)
    climax_shot = base_shot.copy()
    draw_climax = ImageDraw.Draw(climax_shot)

    # Injeta a Criatura (@imagem_4) ao centro no fundo entre as árvores
    draw_climax.rectangle([(340, 40), (492, 260)], outline=(240, 160, 40), width=4)
    draw_climax.text((350, 60), "@imagem_4: CRIATURA", fill=(255, 200, 50))
    draw_climax.text((350, 85), "Olhos âmbar na neblina", fill=(230, 180, 100))

    quadro_climax_path = os.path.join(OUTPUT_DIR, "quadro_climax_criatura_832x480.png")
    climax_shot.save(quadro_climax_path)
    print(f"✅ Quadro de Clímax Composto: {quadro_climax_path}")

    VRAMManager.purge()
    return quadro_base_path, quadro_climax_path

if __name__ == "__main__":
    run_stage_character_sheets()
