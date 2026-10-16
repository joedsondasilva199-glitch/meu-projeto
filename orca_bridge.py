#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
orca_bridge.py
==============
Ponte de integração entre o Antigravity (Orquestrador) e o Orca (Executores CLI).
Permite despachar tarefas em worktrees git isoladas vinculadas diretamente
aos tickets do Linear, ler perguntas dos executores e vigiar as branches.
"""

import os
import sys
import json
import subprocess
import argparse
from typing import Dict, Any, List, Optional

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

ORCA_BIN = r"C:\Users\Lipe\AppData\Local\Programs\orca\resources\bin\orca.EXE"
ORCA_WORKSPACE_BASE = get_config_var("ORCA_WORKSPACE_BASE", r"C:\Users\Lipe\orca\workspaces")
DEFAULT_AGENT = get_config_var("ORCA_DEFAULT_AGENT", "claude")
GITHUB_REPO = get_config_var("GITHUB_REPO", "")

class OrcaBridge:
    def __init__(self, orca_bin: str = ORCA_BIN):
        self.orca_bin = orca_bin if os.path.exists(orca_bin) else "orca"

    def run_cmd(self, args: List[str], capture_json: bool = False) -> Any:
        cmd = [self.orca_bin] + args
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if capture_json:
                try:
                    return json.loads(res.stdout)
                except Exception:
                    return {"stdout": res.stdout, "stderr": res.stderr, "exit_code": res.returncode}
            return res.stdout
        except Exception as e:
            return {"error": str(e)}

    def status(self) -> Dict[str, Any]:
        """Verifica o status atual do runtime do Orca."""
        out = self.run_cmd(["status", "--json"], capture_json=True)
        return out if isinstance(out, dict) else {"raw": out}

    def open_app(self):
        """Abre o aplicativo Orca caso o runtime esteja offline."""
        subprocess.Popen([self.orca_bin, "open"], shell=True)
        print("🚀 Solicitada abertura do Orca...")

    def list_worktrees(self, repo_name: Optional[str] = None) -> Any:
        """Lista worktrees ativas no Orca."""
        args = ["worktree", "ps", "--json"]
        return self.run_cmd(args, capture_json=True)

    def dispatch_task(
        self,
        slug: str,
        linear_issue_id: str,
        task_prompt: str,
        repo_name: Optional[str] = None,
        agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispara um executor em worktree isolada vinculado à issue do Linear.
        Injeta o protocolo de orquestração padrão no prompt.
        """
        target_repo = repo_name or GITHUB_REPO
        target_agent = agent or DEFAULT_AGENT

        full_prompt = (
            f"{task_prompt}\n\n"
            f"PROTOCOLO DE ORQUESTRAÇÃO OBRIGATÓRIO (AGENTS.md):\n"
            f"- Espelhe todo o andamento no ticket {linear_issue_id} do Linear (Início, Progresso, Dúvida e Conclusão).\n"
            f"- Dúvidas ou bloqueios: comente no ticket Linear E crie o arquivo .orchestrator-question na raiz.\n"
            f"- O orquestrador (Antigravity) responderá diretamente no ticket e removerá o bloqueio.\n"
            f"- NÃO realize deploy direto em produção. Abra Pull Request no GitHub ao concluir com evidência real."
        )

        args = [
            "worktree", "create",
            "--name", slug,
            "--agent", target_agent,
            "--prompt", full_prompt,
            "--linear-issue", linear_issue_id,
            "--activate",
            "--json"
        ]
        if target_repo:
            args.extend(["--repo", f"name:{target_repo}"])

        print(f"📦 Disparando worktree no Orca: [{slug}] para a tarefa {linear_issue_id}...")
        return self.run_cmd(args, capture_json=True)

    def scan_for_questions(self, repo_name: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Escaneia as pastas de worktree no disco em busca do arquivo .orchestrator-question.
        Retorna a lista de perguntas pendentes com o caminho e conteúdo.
        """
        repo = repo_name or GITHUB_REPO
        target_dir = os.path.join(ORCA_WORKSPACE_BASE, repo) if repo else ORCA_WORKSPACE_BASE
        questions = []

        if not os.path.exists(target_dir):
            return questions

        for root, dirs, files in os.walk(target_dir):
            if ".orchestrator-question" in files:
                q_file = os.path.join(root, ".orchestrator-question")
                try:
                    with open(q_file, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read().strip()
                    worktree_name = os.path.basename(root)
                    questions.append({
                        "worktree": worktree_name,
                        "path": q_file,
                        "question": content
                    })
                except Exception as e:
                    questions.append({
                        "worktree": os.path.basename(root),
                        "path": q_file,
                        "question": f"Erro lendo arquivo: {e}"
                    })
        return questions

def main():
    parser = argparse.ArgumentParser(description="Orca Bridge CLI para Antigravity")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Verifica o estado do runtime do Orca")
    sub.add_parser("open", help="Abre o aplicativo Orca")
    sub.add_parser("check-questions", help="Verifica se há perguntas pendentes em .orchestrator-question")

    p_disp = sub.add_parser("dispatch", help="Dispara uma tarefa no Orca vinculada ao Linear")
    p_disp.add_argument("--slug", required=True, help="Nome do slug da branch/worktree (ex: feat-auth)")
    p_disp.add_argument("--issue", required=True, help="Identificador do ticket no Linear (ex: ENG-15)")
    p_disp.add_argument("--prompt", required=True, help="Instrução da tarefa")
    p_disp.add_argument("--repo", help="Nome do repositório")
    p_disp.add_argument("--agent", default="claude", help="Agente executor (claude, codex)")

    args = parser.parse_args()

    bridge = OrcaBridge()

    if args.command == "status":
        st = bridge.status()
        print("=== STATUS DO ORCA RUNTIME ===")
        print(json.dumps(st, indent=2))

    elif args.command == "open":
        bridge.open_app()

    elif args.command == "check-questions":
        qs = bridge.scan_for_questions()
        if not qs:
            print("✅ Nenhuma pergunta pendente (.orchestrator-question) encontrada.")
        else:
            print(f"⚠️ Atenção: {len(qs)} pergunta(s) encontrada(s) nos executores:")
            for q in qs:
                print(f"\nWorktree: {q['worktree']}")
                print(f"Arquivo:  {q['path']}")
                print(f"Dúvida:\n{q['question']}")

    elif args.command == "dispatch":
        res = bridge.dispatch_task(args.slug, args.issue, args.prompt, args.repo, args.agent)
        print(json.dumps(res, indent=2))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
