#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/limpar-logo.py
======================
FRENTE 2 — LOGO, ÍCONE E NOME VISÍVEL
Localiza ativos de imagem de marca originais e os substitui por um ícone
novo, gerado via código (sem dependências de imagens locais do operador).
Gera backups em ER-LIMPEZA/_antes-icones/.
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Any
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

EXTENSOES_IMAGEM = {".ico", ".icns", ".png", ".svg", ".jpg", ".jpeg", ".webp"}

TERMOS_MARCA = {"icon", "logo", "brand", "favicon", "splash", "apple-touch-icon"}

IGNORAR_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".cache", "ER-LIMPEZA", "ER-OUTPUT"
}

def gerar_icone_inventado(nome_marca: str, tamanho: int = 256) -> Image.Image:
    """Gera um ícone moderno com gradiente geométrico e inicial da nova marca."""
    img = Image.new("RGBA", (tamanho, tamanho), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fundo circular com gradiente simulado
    raio = tamanho // 2
    centro = (raio, raio)
    for r in range(raio, 0, -1):
        # Gradiente do violeta (#6366F1) para o roxo profundo (#3B0764)
        t = (raio - r) / raio
        r_c = int(99 + (59 - 99) * t)
        g_c = int(102 + (7 - 102) * t)
        b_c = int(241 + (100 - 241) * t)
        draw.ellipse([raio - r, raio - r, raio + r, raio + r], fill=(r_c, g_c, b_c, 255))

    # Letra Inicial da Marca
    inicial = nome_marca.strip()[0].upper() if nome_marca else "K"
    try:
        # Tenta fonte padrão ou desenha glifo geométrico
        font_size = int(tamanho * 0.55)
        # Cria máscara para a letra
        draw.text((tamanho // 2, tamanho // 2), inicial, fill=(255, 255, 255, 255), anchor="mm")
    except Exception:
        # Fallback de desenho geométrico de diamante/losango se fonte falhar
        draw.polygon([
            (tamanho // 2, tamanho // 4),
            (3 * tamanho // 4, tamanho // 2),
            (tamanho // 2, 3 * tamanho // 4),
            (tamanho // 4, tamanho // 2)
        ], fill=(255, 255, 255, 255))

    return img

def salvar_multi_ico(img_base: Image.Image, destino_ico: Path):
    """Salva arquivo .ico contendo resoluções padrão do Windows."""
    tamanhos = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img_base.save(destino_ico, format="ICO", sizes=tamanhos)

def limpar_logos(caminho_clone: Path, nome_marca: str, dry_run: bool = False, backup_dir: Path = None) -> Dict[str, Any]:
    if not backup_dir:
        backup_dir = Path("ER-LIMPEZA/_antes-icones").resolve()
    if not dry_run:
        backup_dir.mkdir(parents=True, exist_ok=True)

    img_nova = gerar_icone_inventado(nome_marca, 256)
    
    icones_encontrados = []
    icones_substituidos = 0

    for root, dirs, files in os.walk(caminho_clone):
        dirs[:] = [d for d in dirs if d not in IGNORAR_DIRS and not d.startswith("ER-")]

        for file in files:
            ext = Path(file).suffix.lower()
            stem = Path(file).stem.lower()

            if ext in EXTENSOES_IMAGEM:
                # Verifica se é ícone de marca
                pasta_nome = Path(root).name.lower()
                eh_marca = (
                    any(t in stem for t in TERMOS_MARCA) or
                    any(t in pasta_nome for t in TERMOS_MARCA)
                )

                if eh_marca:
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(caminho_clone)
                    icones_encontrados.append(str(rel_path))

                    if not dry_run:
                        # Backup
                        bkp_path = backup_dir / rel_path
                        bkp_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, bkp_path)

                        # Substituição adequada por extensão
                        if ext == ".ico":
                            salvar_multi_ico(img_nova, file_path)
                        elif ext in {".png", ".webp", ".jpg", ".jpeg"}:
                            try:
                                with Image.open(file_path) as orig_im:
                                    w, h = orig_im.size
                            except Exception:
                                w, h = (256, 256)
                            res = img_nova.resize((w, h), Image.Resampling.LANCZOS)
                            if ext == ".jpg" or ext == ".jpeg":
                                res.convert("RGB").save(file_path, "JPEG")
                            else:
                                res.save(file_path, "PNG")

                        icones_substituidos += 1

    return {
        "marca": nome_marca,
        "total_encontrados": len(icones_encontrados),
        "total_substituidos": icones_substituidos if not dry_run else len(icones_encontrados),
        "lista_icones": icones_encontrados
    }

def main():
    parser = argparse.ArgumentParser(description="Frente 2: Limpeza e Geração de Ícones e Logos")
    parser.add_argument("caminho", help="Pasta do clone")
    parser.add_argument("--nome", default="PROJETO", help="Nome da nova marca")
    parser.add_argument("--dry", action="store_true", help="Modo simulação")

    args = parser.parse_args()
    pasta = Path(args.caminho).resolve()
    res = limpar_logos(pasta, args.nome, args.dry)
    print(f"Logos processados: {res['total_substituidos']} ícones/logos de marca gerados e substituídos.")

if __name__ == "__main__":
    main()
