#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/limpar-identidade.py
===========================
FRENTE 1 — IDENTIDADE DE TEXTO
Higienização de referências textuais, marcas, URLs, telemetrias e autores.
Gera backups em ER-LIMPEZA/_antes/.
"""

import os
import sys
import argparse
import re
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

EXTENSOES_TEXTO = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".html",
    ".css", ".json", ".md", ".txt", ".yaml", ".yml", ".env"
}

IGNORAR_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".cache", "ER-LIMPEZA", "ER-OUTPUT"
}

def construir_regras(nome_novo: str) -> Dict[str, str]:
    nome_title = nome_novo.strip().title()
    nome_upper = nome_novo.strip().upper()
    nome_lower = nome_novo.strip().lower()

    return {
        # Domínios e URLs completas
        "https://darklabapp.com": f"https://{nome_lower}.local",
        "http://darklabapp.com": f"http://{nome_lower}.local",
        "darklabapp.com": f"{nome_lower}.local",
        "darklabapp": nome_lower,
        # Marcas do Produto
        "DarkLAB AI Studio": f"{nome_title} Studio",
        "DarkLAB Studio": f"{nome_title} Studio",
        "DarkLAB": f"{nome_title}",
        "DarkLab": f"{nome_title}",
        "DARKLAB": f"{nome_upper}",
        "darklab": f"{nome_lower}",
        # App ID e Banco
        "com.nousresearch.hermes": f"com.{nome_lower}.app",
        "darklab.db": f"{nome_lower}.db",
        # Telemetria & Autores
        "dlab_theme": f"{nome_lower}_theme",
        "darklab-provider": f"{nome_lower}-provider"
    }

def limpar_texto(caminho_clone: Path, nome_novo: str, dry_run: bool = False, backup_dir: Path = None) -> Dict[str, Any]:
    regras = construir_regras(nome_novo)
    chaves_ordenadas = sorted(regras.keys(), key=len, reverse=True)
    regex = re.compile("|".join(re.escape(k) for k in chaves_ordenadas))

    total_trocas = 0
    arquivos_alterados = 0
    detalhes_arquivos = []
    pendencias = []

    if not backup_dir:
        backup_dir = Path("ER-LIMPEZA/_antes").resolve()
    if not dry_run:
        backup_dir.mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk(caminho_clone):
        dirs[:] = [d for d in dirs if d not in IGNORAR_DIRS and not d.startswith("ER-")]

        for file in files:
            ext = Path(file).suffix.lower()
            if ext not in EXTENSOES_TEXTO:
                continue

            file_path = Path(root) / file
            rel_path = file_path.relative_to(caminho_clone)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    conteudo = f.read()
            except Exception as e:
                pendencias.append(f"Erro ao ler {rel_path}: {e}")
                continue

            novo_conteudo, n = regex.subn(lambda m: regras.get(m.group(0), m.group(0)), conteudo)

            if n > 0:
                total_trocas += n
                arquivos_alterados += 1
                detalhes_arquivos.append({
                    "arquivo": str(rel_path),
                    "trocas": n
                })

                if not dry_run:
                    # Salva backup
                    bkp_path = backup_dir / rel_path
                    bkp_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, bkp_path)

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(novo_conteudo)

    return {
        "nome_novo": nome_novo,
        "total_trocas": total_trocas,
        "arquivos_alterados": arquivos_alterados,
        "detalhes": detalhes_arquivos,
        "mapa_regras": regras,
        "pendencias": pendencias
    }

def main():
    parser = argparse.ArgumentParser(description="Frente 1: Limpeza de Identidade de Texto")
    parser.add_argument("caminho", help="Pasta do clone")
    parser.add_argument("--nome", default="PROJETO", help="Nome inventado para a nova identidade")
    parser.add_argument("--dry", action="store_true", help="Modo simulação")

    args = parser.parse_args()
    pasta = Path(args.caminho).resolve()
    res = limpar_texto(pasta, args.nome, args.dry)
    print(f"Texto processado: {res['total_trocas']} trocas em {res['arquivos_alterados']} arquivos.")

if __name__ == "__main__":
    main()
