#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
api_server.py
=============
API REST de Orquestração da Stack de Múltiplos Agentes.
Desenvolvida com FastAPI + Uvicorn.

Fornece endpoints para:
- Healthcheck (/api/health)
- Diagnóstico da Stack (/api/stack/status)
- Operações no Linear Business (/api/linear/*)
- Dispatch e Auditoria no Orca (/api/orca/*)
- Monitoramento das 4 Janelas (/api/monitor)
"""

import os
import sys
import subprocess
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    from fastapi import FastAPI, HTTPException, Query, Body
    from fastapi.responses import HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("❌ FastAPI ou Uvicorn não instalados.")
    sys.exit(1)

from linear_manager import LinearClient, get_config_var
from orca_bridge import OrcaBridge
import orchestrator_monitor

app = FastAPI(
    title="Stack de Agentes Orquestradora API",
    description="API de controle da Stack Multi-Agente: Antigravity + Linear Business + Orca + Hermes.",
    version="1.0.0"
)

# Habilita CORS para permitir conexão com interfaces locais ou web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# MODELOS DE DADOS (Pydantic)
# -------------------------------------------------------------
class IssueCreateRequest(BaseModel):
    team_id: str = Field(..., description="ID da equipe no Linear")
    title: str = Field(..., description="Título da tarefa/fatia vertical")
    description: str = Field("", description="Critérios de aceite e contexto")
    project_id: Optional[str] = Field(None, description="ID do projeto associado")
    priority: int = Field(1, description="Prioridade (1=Urgente, 2=Alta, 3=Média, 4=Baixa)")

class CommentRequest(BaseModel):
    issue_id: str = Field(..., description="ID ou identificador da tarefa no Linear")
    body: str = Field(..., description="Texto da resposta ou orientação do Tech Lead")

class StateUpdateRequest(BaseModel):
    issue_id: str = Field(..., description="ID da tarefa no Linear")
    state_id: str = Field(..., description="ID do novo estado do workflow")

class DispatchRequest(BaseModel):
    slug: str = Field(..., description="Slug identificador da branch/worktree (ex: feat-auth)")
    linear_issue: str = Field(..., description="Identificador da tarefa no Linear (ex: ENG-12)")
    prompt: str = Field(..., description="Instruções para o executor")
    repo: Optional[str] = Field(None, description="Nome do repositório no GitHub")
    agent: str = Field("claude", description="Agente executor (claude ou codex)")

class ApiKeyUpdateRequest(BaseModel):
    linear_api_key: str = Field(..., description="Personal API Key do Linear")

# -------------------------------------------------------------
# 1. ESQUELETO & HEALTHCHECK (Fase 1 do Blueprint)
# -------------------------------------------------------------
@app.get("/api/health", summary="Healthcheck do Servidor")
def healthcheck():
    """Retorna o status do servidor da API da Stack de Agentes."""
    return {
        "status": "healthy",
        "service": "Stack de Agentes Orquestradora API",
        "version": "1.0.0",
        "timestamp": "2026-10-15T14:55:00Z"
    }

# -------------------------------------------------------------
# 2. STATUS E DIAGNÓSTICO DA STACK
# -------------------------------------------------------------
@app.get("/api/stack/status", summary="Diagnóstico Completo da Stack")
def get_stack_status():
    """Verifica e retorna o estado de prontidão de todos os nós da stack."""
    # GitHub
    gh_ok = False
    gh_account = "Não autenticado"
    try:
        res = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, encoding="utf-8")
        if res.returncode == 0:
            gh_ok = True
            for l in (res.stdout + res.stderr).splitlines():
                if "account" in l.lower():
                    gh_account = l.strip()
                    break
    except Exception:
        pass

    # Orca
    orca_bridge = OrcaBridge()
    orca_st = orca_bridge.status()

    # Linear
    linear_ok = False
    linear_info = {}
    try:
        l_client = LinearClient()
        linear_info = l_client.get_account_info()
        linear_ok = bool(linear_info.get("id"))
    except Exception as e:
        linear_info = {"error": str(e)}

    # Hermes
    hermes_path = r"C:\Users\Lipe\AppData\Local\hermes"
    hermes_ok = os.path.exists(hermes_path)

    return {
        "github": {"ok": gh_ok, "details": gh_account},
        "orca": {"ok": True, "runtime": orca_st},
        "linear": {"ok": linear_ok, "account": linear_info},
        "hermes": {"ok": hermes_ok, "path": hermes_path}
    }

# -------------------------------------------------------------
# 3. ROTAS DO LINEAR (Conta Business)
# -------------------------------------------------------------
@app.get("/api/linear/teams", summary="Listar Equipes do Linear")
def list_linear_teams():
    try:
        client = LinearClient()
        return {"teams": client.list_teams()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/linear/projects", summary="Listar Projetos do Linear")
def list_linear_projects():
    try:
        client = LinearClient()
        return {"projects": client.list_projects()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/linear/issues", summary="Listar Tarefas do Linear")
def list_linear_issues(project_id: Optional[str] = None, team_key: Optional[str] = None):
    try:
        client = LinearClient()
        key = team_key or get_config_var("LINEAR_TEAM_KEY")
        return {"issues": client.list_issues(project_id=project_id, team_key=key)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/linear/issues", summary="Criar Nova Tarefa no Linear")
def create_linear_issue(body: IssueCreateRequest):
    try:
        client = LinearClient()
        res = client.create_issue(
            team_id=body.team_id,
            title=body.title,
            description=body.description,
            project_id=body.project_id,
            priority=body.priority
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/linear/comment", summary="Responder Dúvida / Comentar no Ticket")
def add_linear_comment(body: CommentRequest):
    try:
        client = LinearClient()
        res = client.add_comment(issue_id=body.issue_id, body=body.body)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/linear/state", summary="Atualizar Status do Ticket")
def update_linear_state(body: StateUpdateRequest):
    try:
        client = LinearClient()
        res = client.update_issue_state(issue_id=body.issue_id, state_id=body.state_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------------------------------------------------------------
# 4. ROTAS DO ORCA (Executores de Worktree)
# -------------------------------------------------------------
@app.get("/api/orca/questions", summary="Listar Dúvidas Pendentes (.orchestrator-question)")
def list_orca_questions():
    bridge = OrcaBridge()
    questions = bridge.scan_for_questions()
    return {"pending_questions": questions, "count": len(questions)}

@app.post("/api/orca/dispatch", summary="Despachar Tarefa no Orca")
def dispatch_orca_task(body: DispatchRequest):
    bridge = OrcaBridge()
    res = bridge.dispatch_task(
        slug=body.slug,
        linear_issue_id=body.linear_issue,
        task_prompt=body.prompt,
        repo_name=body.repo,
        agent=body.agent
    )
    return {"result": res}

# -------------------------------------------------------------
# 5. ROTAS DAS 4 JANELAS
# -------------------------------------------------------------
@app.get("/api/monitor", summary="Inspeção das 4 Janelas de Auditoria")
def get_monitor_data():
    base_dir = get_config_var("ORCA_WORKSPACE_BASE", r"C:\Users\Lipe\orca\workspaces")
    repo = get_config_var("GITHUB_REPO", "")

    disk = orchestrator_monitor.check_disk_worktrees(base_dir)
    prs = orchestrator_monitor.check_github_prs(repo)
    linear_st = orchestrator_monitor.check_linear_status()

    return {
        "janela_1_disco": disk,
        "janela_2_github_prs": prs,
        "janela_3_linear": linear_st
    }

# -------------------------------------------------------------
# 6. CONFIGURAÇÃO DINÂMICA
# -------------------------------------------------------------
@app.post("/api/config/linear-key", summary="Salvar Chave do Linear no .env")
def update_linear_key(body: ApiKeyUpdateRequest):
    env_path = ".env"
    key = body.linear_api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="Chave inválida.")

    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.startswith("LINEAR_API_KEY="):
            new_lines.append(f"LINEAR_API_KEY={key}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"\nLINEAR_API_KEY={key}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    return {"success": True, "message": "LINEAR_API_KEY atualizada com sucesso no .env!"}

# -------------------------------------------------------------
# 7. ESPAÇO THE SIMS (ESCRITÓRIO VIRTUAL)
# -------------------------------------------------------------
@app.get("/office", response_class=HTMLResponse, summary="Escritório Virtual The Sims")
@app.get("/sims", response_class=HTMLResponse, summary="Escritório Virtual The Sims")
def get_sims_office():
    office_file = os.path.join(os.path.dirname(__file__), "dashboard", "office.html")
    if os.path.exists(office_file):
        with open(office_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Escritório Virtual em construção</h1>"

if __name__ == "__main__":
    print("Iniciando API da Stack de Agentes em http://127.0.0.1:8000...")
    print("Documentação Swagger disponível em: http://127.0.0.1:8000/docs")
    uvicorn.run("api_server:app", host="127.0.0.1", port=8000, reload=True)
