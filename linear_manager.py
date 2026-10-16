#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
linear_manager.py
=================
Cliente completo e CLI para integração com o Linear (GraphQL API).
Projetado especificamente para a Stack de Múltiplos Agentes:
Hermes (Gestor) + Antigravity (Orquestrador) + Orca (Executores).

Suporte completo a recursos da Conta Business:
- Multi-teams, Projects, Ciclos e Workflows avançados
- Personal API Key autenticada 24/7
- Criação e monitoramento de tickets das Fases
- Leitura e postagem de comentários para desbloqueio de agentes
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Carrega variáveis do arquivo .env local se existir
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

LINEAR_API_KEY = get_config_var("LINEAR_API_KEY")
LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"

class LinearClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or LINEAR_API_KEY
        if not self.api_key:
            raise ValueError(
                "LINEAR_API_KEY não encontrada! Configure no arquivo .env ou como variável de ambiente.\n"
                "Obtenha sua chave em: https://linear.app/settings/api (Personal API keys)"
            )

    def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key
        }
        payload = {"query": query, "variables": variables or {}}
        data_bytes = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(LINEAR_GRAPHQL_URL, data=data_bytes, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                res_body = resp.read().decode("utf-8")
                res_json = json.loads(res_body)
                if "errors" in res_json:
                    err_msg = json.dumps(res_json["errors"], indent=2, ensure_ascii=False)
                    raise RuntimeError(f"Erro na API do Linear GraphQL:\n{err_msg}")
                return res_json.get("data", {})
        except urllib.error.HTTPError as e:
            err_content = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTPError {e.code}: {e.reason}\nDetalhes: {err_content}")
        except Exception as e:
            raise RuntimeError(f"Falha de conexão com Linear: {str(e)}")

    def get_account_info(self) -> Dict[str, Any]:
        """Obtém detalhes da conta, organização e plano do Linear (ex: Business)."""
        query = """
        query {
            viewer {
                id
                name
                email
                admin
                organization {
                    id
                    name
                    urlKey
                    subscription {
                        type
                    }
                }
            }
        }
        """
        data = self._execute_query(query)
        return data.get("viewer", {})

    def list_teams(self) -> List[Dict[str, Any]]:
        """Lista equipes com seus identificadores e estados de workflow."""
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                    key
                    states {
                        nodes {
                            id
                            name
                            type
                            color
                        }
                    }
                }
            }
        }
        """
        data = self._execute_query(query)
        return data.get("teams", {}).get("nodes", [])

    def list_projects(self) -> List[Dict[str, Any]]:
        """Lista todos os projetos cadastrados."""
        query = """
        query {
            projects {
                nodes {
                    id
                    name
                    state
                    progress
                    description
                    teams {
                        nodes {
                            id
                            key
                            name
                        }
                    }
                }
            }
        }
        """
        data = self._execute_query(query)
        return data.get("projects", {}).get("nodes", [])

    def create_project(self, name: str, team_ids: List[str], description: str = "") -> Dict[str, Any]:
        """Cria um novo projeto vinculado a uma ou mais equipes."""
        mutation = """
        mutation CreateProject($name: String!, $teamIds: [String!]!, $description: String) {
            projectCreate(input: {
                name: $name,
                teamIds: $teamIds,
                description: $description
            }) {
                success
                project {
                    id
                    name
                    url
                }
            }
        }
        """
        data = self._execute_query(mutation, {
            "name": name,
            "teamIds": team_ids,
            "description": description
        })
        return data.get("projectCreate", {})

    def list_issues(self, project_id: Optional[str] = None, team_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista issues filtradas por projeto ou time."""
        query = """
        query GetIssues($filter: IssueFilter) {
            issues(filter: $filter, first: 50, orderBy: createdAt) {
                nodes {
                    id
                    identifier
                    title
                    description
                    priority
                    priorityLabel
                    state {
                        id
                        name
                        type
                    }
                    project {
                        id
                        name
                    }
                    comments {
                        nodes {
                            id
                            body
                            createdAt
                            user {
                                name
                            }
                        }
                    }
                }
            }
        }
        """
        issue_filter: Dict[str, Any] = {}
        if project_id:
            issue_filter["project"] = {"id": {"eq": project_id}}
        if team_key:
            issue_filter["team"] = {"key": {"eq": team_key}}

        data = self._execute_query(query, {"filter": issue_filter if issue_filter else None})
        return data.get("issues", {}).get("nodes", [])

    def create_issue(
        self,
        team_id: str,
        title: str,
        description: str = "",
        project_id: Optional[str] = None,
        priority: int = 1
    ) -> Dict[str, Any]:
        """Cria uma nova issue no Linear."""
        mutation = """
        mutation CreateIssue($teamId: String!, $title: String!, $description: String, $projectId: String, $priority: Int) {
            issueCreate(input: {
                teamId: $teamId,
                title: $title,
                description: $description,
                projectId: $projectId,
                priority: $priority
            }) {
                success
                issue {
                    id
                    identifier
                    url
                    title
                }
            }
        }
        """
        data = self._execute_query(mutation, {
            "teamId": team_id,
            "title": title,
            "description": description,
            "projectId": project_id,
            "priority": priority
        })
        return data.get("issueCreate", {})

    def add_comment(self, issue_id: str, body: str) -> Dict[str, Any]:
        """Adiciona comentário a um ticket (resposta/desbloqueio do orquestrador)."""
        mutation = """
        mutation AddComment($issueId: String!, $body: String!) {
            commentCreate(input: {
                issueId: $issueId,
                body: $body
            }) {
                success
                comment {
                    id
                    body
                    createdAt
                }
            }
        }
        """
        data = self._execute_query(mutation, {"issueId": issue_id, "body": body})
        return data.get("commentCreate", {})

    def update_issue_state(self, issue_id: str, state_id: str) -> Dict[str, Any]:
        """Altera o estado do ticket (ex: Backlog, Todo, In Progress, In Review, Done)."""
        mutation = """
        mutation UpdateIssueState($issueId: String!, $stateId: String!) {
            issueUpdate(id: $issueId, input: { stateId: $stateId }) {
                success
                issue {
                    id
                    identifier
                    state {
                        name
                        type
                    }
                }
            }
        }
        """
        data = self._execute_query(mutation, {"issueId": issue_id, "stateId": state_id})
        return data.get("issueUpdate", {})

def main():
    parser = argparse.ArgumentParser(description="Linear Manager CLI para a Stack de Agentes")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # verify
    subparsers.add_parser("verify", help="Verifica a conexão com a API do Linear e a conta Business")

    # list-teams
    subparsers.add_parser("list-teams", help="Lista as equipes disponíveis e seus fluxos")

    # list-projects
    subparsers.add_parser("list-projects", help="Lista os projetos cadastrados")

    # create-project
    p_proj = subparsers.add_parser("create-project", help="Cria um novo projeto")
    p_proj.add_argument("--name", required=True, help="Nome do projeto")
    p_proj.add_argument("--team-id", required=True, help="ID da equipe")
    p_proj.add_argument("--description", default="", help="Descrição do projeto")

    # list-issues
    p_issues = subparsers.add_parser("list-issues", help="Lista issues de um projeto ou time")
    p_issues.add_argument("--project-id", help="ID do projeto")
    p_issues.add_argument("--team-key", help="Chave da equipe (ex: ENG)")

    # create-issue
    p_ci = subparsers.add_parser("create-issue", help="Cria uma nova issue/tarefa")
    p_ci.add_argument("--team-id", required=True, help="ID da equipe")
    p_ci.add_argument("--title", required=True, help="Título da tarefa")
    p_ci.add_argument("--desc", default="", help="Descrição com critérios de aceite")
    p_ci.add_argument("--project-id", help="ID do projeto associado")
    p_ci.add_argument("--priority", type=int, default=1, help="Prioridade (0=None, 1=Urgent, 2=High, 3=Medium, 4=Low)")

    # comment
    p_comm = subparsers.add_parser("comment", help="Adiciona comentário ao ticket")
    p_comm.add_argument("--issue-id", required=True, help="ID da issue (ex: UUID ou identificador)")
    p_comm.add_argument("--body", required=True, help="Texto da resposta/orientação")

    # set-state
    p_st = subparsers.add_parser("set-state", help="Atualiza status de uma issue")
    p_st.add_argument("--issue-id", required=True, help="ID da issue")
    p_st.add_argument("--state-id", required=True, help="ID do estado alvo")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        client = LinearClient()
    except Exception as e:
        print(f"❌ Erro de configuração: {e}")
        sys.exit(1)

    try:
        if args.command == "verify":
            info = client.get_account_info()
            org = info.get("organization", {})
            sub = org.get("subscription", {})
            plan = sub.get("type", "Standard / Free")
            print("==================================================")
            print("✅ CONEXÃO COM O LINEAR ESTABELECIDA COM SUCESSO!")
            print("==================================================")
            print(f"👤 Usuário:      {info.get('name')} ({info.get('email')})")
            print(f"🏢 Organização:  {org.get('name')} ({org.get('urlKey')})")
            print(f"💎 Plano/Conta:  {plan}")
            print(f"🔑 Admin:        {'Sim' if info.get('admin') else 'Não'}")
            print("==================================================")

        elif args.command == "list-teams":
            teams = client.list_teams()
            print(f"📋 Encontradas {len(teams)} equipe(s):")
            for t in teams:
                print(f"\n🔹 Equipe: {t['name']} (Key: [{t['key']}], ID: {t['id']})")
                print("   Estados do Workflow:")
                for s in t.get("states", {}).get("nodes", []):
                    print(f"     - {s['name']} (Tipo: {s['type']}, ID: {s['id']})")

        elif args.command == "list-projects":
            projects = client.list_projects()
            print(f"📁 Encontrados {len(projects)} projeto(s):")
            for p in projects:
                teams = [t["name"] for t in p.get("teams", {}).get("nodes", [])]
                print(f"  - [{p['id']}] {p['name']} | Estado: {p['state']} | Progresso: {p.get('progress', 0)}% | Equipes: {', '.join(teams)}")

        elif args.command == "create-project":
            res = client.create_project(args.name, [args.team_id], args.description)
            if res.get("success"):
                proj = res["project"]
                print(f"✅ Projeto criado com sucesso!\nNome: {proj['name']}\nID: {proj['id']}\nURL: {proj.get('url')}")
            else:
                print("❌ Falha ao criar projeto.")

        elif args.command == "list-issues":
            issues = client.list_issues(args.project_id, args.team_key)
            print(f"📌 Encontradas {len(issues)} tarefa(s):")
            for iss in issues:
                state_name = iss.get("state", {}).get("name", "N/A")
                comments_count = len(iss.get("comments", {}).get("nodes", []))
                print(f"  - [{iss['identifier']}] {iss['title']} (Status: {state_name}, Comentários: {comments_count})")

        elif args.command == "create-issue":
            res = client.create_issue(args.team_id, args.title, args.desc, args.project_id, args.priority)
            if res.get("success"):
                iss = res["issue"]
                print(f"✅ Tarefa criada!\nIdentificador: {iss['identifier']}\nTítulo: {iss['title']}\nURL: {iss.get('url')}\nID: {iss['id']}")
            else:
                print("❌ Falha ao criar tarefa.")

        elif args.command == "comment":
            res = client.add_comment(args.issue_id, args.body)
            if res.get("success"):
                print("✅ Comentário publicado com sucesso no ticket do Linear!")
            else:
                print("❌ Falha ao publicar comentário.")

        elif args.command == "set-state":
            res = client.update_issue_state(args.issue_id, args.state_id)
            if res.get("success"):
                iss = res["issue"]
                print(f"✅ Estado da issue {iss['identifier']} atualizado para: {iss.get('state', {}).get('name')}")
            else:
                print("❌ Falha ao atualizar estado.")

    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
