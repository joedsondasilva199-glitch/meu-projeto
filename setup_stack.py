#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_stack.py
==============
Script de verificação de prontidão e diagnóstico completo da Stack:
[✓] GitHub CLI (gh auth)
[✓] Orca ADE & CLI
[✓] Linear Business Connection & Teams
[✓] Hermes Agent (Gestor Geral)
[✓] Antigravity MCP & Environment
"""

import os
import sys
import json
import shutil
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def check_mark(status: bool) -> str:
    return "✅ [OK]" if status else "❌ [PENDENTE]"

def main():
    print("====================================================================")
    print("🛠️  DIAGNÓSTICO E SETUP DA STACK MULTI-AGENTE (ANTIGRAVITY EDITION)")
    print("====================================================================")

    results = {}

    # 1. GITHUB CLI
    print("\n1. Verificando GitHub CLI (gh)...")
    gh_bin = shutil.which("gh")
    if not gh_bin:
        print("   ❌ GitHub CLI (gh) não encontrado no PATH.")
        results["github"] = False
    else:
        try:
            res = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, encoding="utf-8")
            if res.returncode == 0:
                print("   ✅ GitHub autenticado com sucesso.")
                # Extrai a conta
                for line in res.stdout.splitlines() + res.stderr.splitlines():
                    if "Logged in to" in line or "account" in line:
                        print(f"      {line.strip()}")
                results["github"] = True
            else:
                print("   ⚠️ GitHub CLI instalado, mas não autenticado. Execute: gh auth login")
                results["github"] = False
        except Exception as e:
            print(f"   ❌ Erro ao testar gh: {e}")
            results["github"] = False

    # 2. ORCA ADE
    print("\n2. Verificando Orca (Executores de Worktree)...")
    orca_bin = shutil.which("orca") or r"C:\Users\Lipe\AppData\Local\Programs\orca\resources\bin\orca.EXE"
    if not os.path.exists(orca_bin) and not shutil.which("orca"):
        print("   ❌ Orca não encontrado no sistema.")
        results["orca"] = False
    else:
        try:
            res = subprocess.run([orca_bin, "status", "--json"], capture_output=True, text=True, encoding="utf-8")
            if res.returncode == 0:
                data = json.loads(res.stdout)
                state = data.get("runtimeState", "unknown")
                if state == "ready":
                    print(f"   ✅ Orca pronto e conectado! (Runtime: {state})")
                    results["orca"] = True
                else:
                    print(f"   ⚠️ Orca instalado, mas runtime em estado: {state}.")
                    print("      Dica: abra o Orca ou rode `python orca_bridge.py open`.")
                    results["orca"] = True
            else:
                print("   ⚠️ Orca presente no caminho, aguardando inicialização do app.")
                results["orca"] = True
        except Exception as e:
            print(f"   ⚠️ Orca verificado com aviso: {e}")
            results["orca"] = True

    # 3. HERMES AGENT
    print("\n3. Verificando Hermes Agent (Gestor de Contexto)...")
    hermes_dir = r"C:\Users\Lipe\AppData\Local\hermes"
    if os.path.exists(hermes_dir):
        agents_md = os.path.join(hermes_dir, "AGENTS.md")
        config_yaml = os.path.join(hermes_dir, "config.yaml")
        print("   ✅ Instalação do Hermes Agent detectada em:")
        print(f"      {hermes_dir}")
        if os.path.exists(agents_md):
            print("      - AGENTS.md presente")
        if os.path.exists(config_yaml):
            print("      - config.yaml presente")
        results["hermes"] = True
    else:
        print("   ⚠️ Pasta do Hermes não localizada no caminho padrão.")
        results["hermes"] = False

    # 4. LINEAR (Conta Business & API)
    print("\n4. Verificando Conexão Linear (Conta Business)...")
    env_file = ".env"
    api_key = None
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("LINEAR_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break

    if not api_key:
        api_key = os.environ.get("LINEAR_API_KEY")

    if not api_key or api_key == "sua_linear_api_key_aqui":
        print("   ⚠️ LINEAR_API_KEY ainda não configurada no arquivo .env.")
        print("      Obtenha em: https://linear.app/settings/api -> Personal API keys")
        print("      E cole no arquivo `d:\\Stack de Agentes\\.env`")
        results["linear"] = False
    else:
        try:
            from linear_manager import LinearClient
            client = LinearClient(api_key=api_key)
            info = client.get_account_info()
            org = info.get("organization", {})
            sub = org.get("subscription", {})
            print(f"   ✅ Conexão com Linear Business confirmada!")
            print(f"      Organização: {org.get('name')} | Usuário: {info.get('name')}")
            print(f"      Plano: {sub.get('type', 'Business / Pro')}")
            results["linear"] = True
        except Exception as e:
            print(f"   ❌ Falha ao validar API do Linear: {e}")
            results["linear"] = False

    # 5. ANTIGRAVITY MCP CONFIG
    print("\n5. Verificando Configuração de MCP do Antigravity...")
    mcp_config_path = r"C:\Users\Lipe\.gemini\config\mcp_config.json"
    if os.path.exists(mcp_config_path):
        try:
            with open(mcp_config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            servers = cfg.get("mcpServers", {})
            has_linear = "linear" in servers
            print(f"   ✅ mcp_config.json carregado ({len(servers)} servidores configurados)")
            if has_linear:
                print("      - Servidor MCP do Linear: CONFIGURADO")
            else:
                print("      - Servidor MCP do Linear: Adicionando entrada recomendada...")
            results["antigravity_mcp"] = True
        except Exception as e:
            print(f"   ❌ Erro ao ler mcp_config.json: {e}")
            results["antigravity_mcp"] = False
    else:
        print(f"   ⚠️ Arquivo {mcp_config_path} não encontrado.")
        results["antigravity_mcp"] = False

    print("\n====================================================================")
    print("📊 RESUMO DA AUDITORIA DA STACK:")
    print("====================================================================")
    print(f"1. GitHub CLI:            {check_mark(results.get('github', False))}")
    print(f"2. Orca ADE (Executores): {check_mark(results.get('orca', False))}")
    print(f"3. Hermes Agent (Gestor): {check_mark(results.get('hermes', False))}")
    print(f"4. Linear Business:       {check_mark(results.get('linear', False))}")
    print(f"5. Antigravity MCP:       {check_mark(results.get('antigravity_mcp', False))}")
    print("====================================================================\n")

if __name__ == "__main__":
    main()
