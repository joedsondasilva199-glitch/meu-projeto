#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
orchestrator_monitor.py
=======================
Monitor central das "4 Janelas" do Orquestrador (Antigravity):
1. LINEAR: Tickets em progresso e comentários de diálogo.
2. DISCO: Worktrees do Orca, novos commits e detecção de .orchestrator-question.
3. GITHUB: PRs abertos pelos executores aguardando revisão.
4. PRODUÇÃO: Status de deploy e saúde (Railway/servidor).

Pode rodar em modo instantâneo (--once) ou contínuo (--watch).
"""

import os
import sys
import time
import json
import subprocess
import argparse
from typing import Dict, Any, List

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()
    return env_vars

ENV_VARS = load_env_file()

def get_config_var(key: str, default: str = "") -> str:
    return os.environ.get(key) or ENV_VARS.get(key) or default

ORCA_WORKSPACE_BASE = get_config_var("ORCA_WORKSPACE_BASE", r"C:\Users\Lipe\orca\workspaces")
GITHUB_REPO = get_config_var("GITHUB_REPO", "")
LINEAR_PROJECT_NAME = get_config_var("LINEAR_PROJECT_NAME", "")

def check_disk_worktrees(base_dir: str) -> Dict[str, Any]:
    """Varre o disco buscando worktrees, últimos commits e perguntas pendentes."""
    info = {
        "worktrees": [],
        "pending_questions": []
    }
    if not os.path.exists(base_dir):
        return info

    try:
        entries = os.listdir(base_dir)
        for entry in entries:
            full_path = os.path.join(base_dir, entry)
            if os.path.isdir(full_path):
                # Checa se é worktree / git repo
                git_marker = os.path.exists(os.path.join(full_path, ".git"))
                last_commit = "Sem commit"
                if git_marker:
                    try:
                        res = subprocess.run(
                            ["git", "-C", full_path, "log", "-1", "--format=%h - %s (%cr)"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace"
                        )
                        if res.returncode == 0 and res.stdout.strip():
                            last_commit = res.stdout.strip()
                    except Exception:
                        pass

                # Checa .orchestrator-question
                q_path = os.path.join(full_path, ".orchestrator-question")
                q_text = None
                if os.path.exists(q_path):
                    try:
                        with open(q_path, "r", encoding="utf-8", errors="replace") as f:
                            q_text = f.read().strip()
                        info["pending_questions"].append({
                            "worktree": entry,
                            "file": q_path,
                            "question": q_text
                        })
                    except Exception as e:
                        info["pending_questions"].append({
                            "worktree": entry,
                            "file": q_path,
                            "question": f"Erro de leitura: {e}"
                        })

                info["worktrees"].append({
                    "name": entry,
                    "path": full_path,
                    "last_commit": last_commit,
                    "has_question": q_text is not None
                })
    except Exception as e:
        info["error"] = str(e)

    return info

def check_github_prs(repo_name: str) -> List[Dict[str, Any]]:
    """Consulta PRs abertos no GitHub via GitHub CLI."""
    prs = []
    try:
        cmd = ["gh", "pr", "list", "--json", "number,title,author,headRefName,url,updatedAt"]
        if repo_name:
            cmd.extend(["-R", repo_name])
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode == 0:
            prs = json.loads(res.stdout)
    except Exception:
        pass
    return prs

def check_linear_status() -> Dict[str, Any]:
    """Consulta tickets e status do Linear via linear_manager."""
    try:
        from linear_manager import LinearClient
        client = LinearClient()
        issues = client.list_issues(team_key=get_config_var("LINEAR_TEAM_KEY"))
        in_progress = [i for i in issues if i.get("state", {}).get("type") in ["started", "unstarted"]]
        return {"total": len(issues), "active": in_progress}
    except Exception as e:
        return {"error": str(e), "active": []}

def run_inspection(show_details: bool = True):
    print("\n=======================================================")
    print("🔍 AUDITORIA DAS 4 JANELAS — ORQUESTRADOR ANTIGRAVITY")
    print("=======================================================")

    # 1. DISCO / WORKTREES
    print("\n[JANELA 1] DISCO — Worktrees do Orca:")
    disk = check_disk_worktrees(ORCA_WORKSPACE_BASE)
    wts = disk.get("worktrees", [])
    if not wts:
        print("  ℹ️ Nenhuma worktree criada ainda em:", ORCA_WORKSPACE_BASE)
    else:
        for w in wts:
            flag = " ⚠️ [DÚVIDA PENDENTE]" if w["has_question"] else " ✅"
            print(f"  • {w['name']}{flag}")
            print(f"    Último commit: {w['last_commit']}")

    # 2. DÚVIDAS PENDENTES (.orchestrator-question)
    qs = disk.get("pending_questions", [])
    if qs:
        print("\n🚨 PERGUNTAS DE EXECUTORES BLOQUEADOS:")
        for q in qs:
            print(f"  🔸 Worktree: {q['worktree']}")
            print(f"     Dúvida: {q['question']}")
            print(f"     Ação recomendada: responda no ticket Linear e remova {q['file']}")
    else:
        print("\n  ✅ Nenhum executor bloqueado por dúvidas no momento.")

    # 3. GITHUB PRs
    print("\n[JANELA 2] GITHUB — Pull Requests Abertos:")
    prs = check_github_prs(GITHUB_REPO)
    if not prs:
        print("  ℹ️ Nenhum PR aberto aguardando revisão.")
    else:
        for pr in prs:
            print(f"  • PR #{pr['number']}: {pr['title']} (Branch: {pr['headRefName']})")
            print(f"    URL: {pr['url']}")

    # 4. LINEAR (Tarefas ativas)
    print("\n[JANELA 3] LINEAR — Quadro de Tarefas:")
    lin = check_linear_status()
    if "error" in lin:
        print(f"  ⚠️ Linear status: {lin['error']}")
    else:
        actives = lin.get("active", [])
        print(f"  Total de tarefas monitoradas: {lin.get('total', 0)}")
        for a in actives[:5]:
            state = a.get("state", {}).get("name", "N/A")
            print(f"  • [{a['identifier']}] {a['title']} ({state})")

    print("\n=======================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Monitor das 4 Janelas do Orquestrador")
    parser.add_argument("--once", action="store_true", help="Executa apenas uma verificação instantânea")
    parser.add_argument("--interval", type=int, default=30, help="Intervalo em segundos para o modo contínuo (padrão: 30s)")

    args = parser.parse_args()

    if args.once:
        run_inspection()
    else:
        print(f"👁️ Monitor ativo. Verificando a cada {args.interval} segundos... (Pressione Ctrl+C para encerrar)")
        try:
            while True:
                run_inspection()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nMonitor encerrado pelo usuário.")

if __name__ == "__main__":
    main()
