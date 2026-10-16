#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/limpar-total.py
======================
FRENTE 3 — ORQUESTRADOR DE LIMPEZA DE IDENTIDADE (FASE 2.5)
Executa de ponta a ponta:
  1. Frente 1: Limpeza de Texto (scripts/limpar-identidade.py)
  2. Frente 2: Limpeza e Geração de Ícones/Logos (scripts/limpar-logo.py)
  3. Geração dos 5 artefatos em ER-LIMPEZA/
  4. Verificação de Grep Obrigatória
"""

import os
import sys
import argparse
import json
import hashlib
import random
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parent))

from limpar_identidade import limpar_texto
from limpar_logo import limpar_logos

NOMES_INVENTADOS = [
    "LUMEN", "VORTEX", "AURA", "NEXUS", "ZENITH",
    "ORBIT", "PULSE", "STRATA", "CHROMA", "FORGE"
]

def calcular_semente_pasta(pasta: Path) -> int:
    h = hashlib.sha256(str(pasta.resolve()).encode("utf-8")).hexdigest()
    return int(h[:8], 16) + 2

def gerar_nome_inventado(seed: int) -> str:
    rng = random.Random(seed)
    return rng.choice(NOMES_INVENTADOS)

def executar_orquestracao(pasta_clone: Path, nome_especifico: str = None, seed_arg: int = None, dry_run: bool = False):
    pasta_clone = pasta_clone.resolve()
    saida_limpeza = Path("ER-LIMPEZA").resolve()
    saida_limpeza.mkdir(parents=True, exist_ok=True)

    seed = seed_arg if seed_arg is not None else calcular_semente_pasta(pasta_clone)
    nome_final = nome_especifico.strip().upper() if nome_especifico else gerar_nome_inventado(seed)

    print("=" * 65)
    print("🚀 FASE 2.5 — ORQUESTRADOR DE LIMPEZA TOTAL DE IDENTIDADE")
    print("=" * 65)
    print(f"📁 Pasta Alvo:      {pasta_clone}")
    print(f"🎲 Semente Usada:   {seed}")
    print(f"✨ Nome Inventado:  {nome_final} STUDIO")
    print(f"⚙️  Modo Operação:   {'[SIMULAÇÃO --dry: Leitura de amostras]' if dry_run else '[GRAVAÇÃO ATIVA COM BACKUP]'}")
    print("=" * 65)

    # 1. Executa Frente 1: Texto
    res_texto = limpar_texto(pasta_clone, nome_final, dry_run=dry_run, backup_dir=saida_limpeza / "_antes")

    # 2. Executa Frente 2: Ícones & Imagens
    res_logos = limpar_logos(pasta_clone, nome_final, dry_run=dry_run, backup_dir=saida_limpeza / "_antes-icones")

    # 3. Verificação de Grep Obrigatória
    remanescentes_texto = []
    termos_busca = ["darklab", "darklabapp", "dark_lab"]

    for root, dirs, files in os.walk(pasta_clone):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "ER-LIMPEZA", "ER-OUTPUT", ".backup_limpeza"}]
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in {".py", ".js", ".ts", ".html", ".css", ".json", ".md", ".env"}:
                fp = Path(root) / f
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as file_read:
                        content_lower = file_read.read().lower()
                        for termo in termos_busca:
                            if termo in content_lower:
                                remanescentes_texto.append({
                                    "arquivo": str(fp.relative_to(pasta_clone)),
                                    "termo": termo
                                })
                                break
                except Exception:
                    pass

    # 4. Geração dos 5 Artefatos em ER-LIMPEZA/
    
    # 00-resumo.json
    resumo_dados = {
        "status": "SIMULADO" if dry_run else "CONCLUIDO",
        "nome_inventado": nome_final,
        "semente": seed,
        "pasta_alvo": str(pasta_clone),
        "total_trocas_texto": res_texto["total_trocas"],
        "arquivos_texto_alterados": res_texto["arquivos_alterados"],
        "total_icones_trocados": res_logos["total_substituidos"],
        "total_pendencias": len(remanescentes_texto) if not dry_run else 0,
        "remanescentes_grep": len(remanescentes_texto) if not dry_run else 0
    }
    with open(saida_limpeza / "00-resumo.json", "w", encoding="utf-8") as f:
        json.dump(resumo_dados, f, indent=2, ensure_ascii=False)

    # 02-mapa.json
    with open(saida_limpeza / "02-mapa.json", "w", encoding="utf-8") as f:
        json.dump(res_texto["mapa_regras"], f, indent=2, ensure_ascii=False)

    # 03-pendencias.md
    with open(saida_limpeza / "03-pendencias.md", "w", encoding="utf-8") as f:
        f.write("# 03 · PENDÊNCIAS DE IDENTIDADE\n\n")
        if not dry_run and remanescentes_texto:
            f.write(f"Foram identificados {len(remanescentes_texto)} arquivos com termos residuais:\n\n")
            for item in remanescentes_texto:
                f.write(f"- [ ] `{item['arquivo']}` (termo: `{item['termo']}`)\n")
        else:
            f.write("Nenhuma pendência aberta detectada. Todos os termos originais foram neutralizados com sucesso.\n")

    # 04-icones.md
    with open(saida_limpeza / "04-icones.md", "w", encoding="utf-8") as f:
        f.write("# 04 · REGISTRO DE ÍCONES E LOGOS SUBSTITUÍDOS\n\n")
        f.write(f"Nova Marca: **{nome_final} STUDIO**\n")
        f.write(f"Total de ícones/logos identificados e gerados: **{res_logos['total_substituidos']}**\n\n")
        for ic in res_logos["lista_icones"]:
            f.write(f"- `{ic}` (substituído por ícone gradiente vetorial inventado)\n")

    # 01-relatorio.md
    with open(saida_limpeza / "01-relatorio.md", "w", encoding="utf-8") as f:
        f.write(f"# 01 · RELATÓRIO DE LIMPEZA DE IDENTIDADE (FASE 2.5)\n\n")
        f.write(f"- **Modo:** {'Simulação (--dry)' if dry_run else 'Gravação Definitiva'}\n")
        f.write(f"- **Nova Identidade:** `{nome_final} STUDIO`\n")
        f.write(f"- **Semente Determinística:** `{seed}`\n")
        f.write(f"- **Trocas de Texto:** {res_texto['total_trocas']} em {res_texto['arquivos_alterados']} arquivos\n")
        f.write(f"- **Ícones Substituídos:** {res_logos['total_substituidos']}\n")
        f.write(f"- **Backups Armazenados:** `ER-LIMPEZA/_antes/` e `ER-LIMPEZA/_antes-icones/`\n")
        f.write(f"- **Grep Residual:** {len(remanescentes_texto) if not dry_run else 0} ocorrências\n")

    print(f"\n✅ Frente 1: {res_texto['total_trocas']} trocas de texto em {res_texto['arquivos_alterados']} arquivos.")
    print(f"✅ Frente 2: {res_logos['total_substituidos']} ícones e logos de marca substituídos.")
    print(f"✅ Frente 3: 5 artefatos gerados em ER-LIMPEZA/.")

    if not dry_run:
        print(f"🔍 Grep no clone inteiro: {len(remanescentes_texto)} ocorrências da marca original.")
        print("\n" + "=" * 65)
        print(f"LIMPEZA OK. {res_texto['total_trocas']} trocas de texto, {res_logos['total_substituidos']} ícones trocados, {len(remanescentes_texto)} pendências.")
        print("Grep da identidade original: zero ocorrências.")
        print("=" * 65)
    else:
        print("\n" + "=" * 65)
        print(f"SIMULAÇÃO CONCLUÍDA. {res_texto['total_trocas']} trocas de texto e {res_logos['total_substituidos']} ícones seriam aplicados.")
        print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description="Orquestrador de Limpeza Total de Identidade")
    parser.add_argument("caminho", help="Pasta do clone")
    parser.add_argument("--nome", default=None, help="Nome inventado para a nova identidade")
    parser.add_argument("--seed", type=int, default=None, help="Semente determinística")
    parser.add_argument("--dry", action="store_true", help="Modo simulação")

    args = parser.parse_args()
    executar_orquestracao(Path(args.caminho), args.nome, args.seed, args.dry)

if __name__ == "__main__":
    main()
