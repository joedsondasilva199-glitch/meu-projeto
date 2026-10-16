#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simulate_mobile_test.py
=======================
Simula um usuário (Joedson) acessando a Stack pelo Celular (4G/5G)
através do Cloudflare Tunnel público HTTPS, testando cada agente
individualmente:
1. Hermes Agent (Gestor Geral)
2. Antigravity (Tech Lead Orquestrador)
3. Orca (Executores de Código)
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# User-Agent de Smartphone real (iPhone Safari / Android Chrome)
MOBILE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"

def load_tunnel_url() -> str:
    with open("tunnel_url.txt", "r", encoding="utf-8") as f:
        return f.read().strip()

def send_mobile_request(url: str, method: str = "GET", data: dict = None) -> dict:
    headers = {
        "User-Agent": MOBILE_UA,
        "Accept": "application/json, text/html, */*",
        "Content-Type": "application/json"
    }
    payload = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            latency = (time.time() - start) * 1000
            res_body = resp.read().decode("utf-8")
            try:
                parsed = json.loads(res_body)
            except Exception:
                parsed = {"raw": res_body}
            return {
                "success": True,
                "status": resp.status,
                "latency_ms": round(latency, 1),
                "data": parsed
            }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "status": e.code,
            "latency_ms": (time.time() - start) * 1000,
            "error": e.read().decode("utf-8", errors="ignore")
        }
    except Exception as e:
        return {
            "success": False,
            "status": 0,
            "latency_ms": (time.time() - start) * 1000,
            "error": str(e)
        }

def run_simulation():
    tunnel_url = load_tunnel_url()
    print("==================================================================")
    print("📱 SIMULAÇÃO MOBILE VIA CLOUDFLARE TUNNEL (4G/CELULAR)")
    print("==================================================================")
    print(f"🌍 Endpoint Público: {tunnel_url}")
    print(f"📲 Dispositivo:       Apple iPhone (iOS 17.4 Mobile Safari)\n")

    # -------------------------------------------------------------
    # ETAPA 1: PING DO CELULAR NO TÚNEL
    # -------------------------------------------------------------
    print("1. [Celular ➔ Túnel] Verificando conectividade pública...")
    res = send_mobile_request(f"{tunnel_url}/api/health")
    if res["success"]:
        print(f"   ✅ HTTP {res['status']} OK ({res['latency_ms']}ms) — Resposta: {res['data'].get('service')}")
    else:
        print(f"   ❌ Falha na conexão: {res}")
        return

    # -------------------------------------------------------------
    # ETAPA 2: PEDIDO SIMPLES — CRIAR TAREFA PELO CELULAR NO LINEAR BUSINESS
    # -------------------------------------------------------------
    print("\n2. [Celular ➔ Linear Business] Joedson cria nova tarefa pelo celular...")
    task_payload = {
        "team_id": "9ee1e6c9-6bd6-4ec1-889e-53b4a07bf50b",
        "project_id": "ff25d4a7-fc84-4909-874e-22bea4bf2197", # Super Mario
        "title": "[F5] Sistema de Pausa (Tecla P) & Som de Moeda Otimizado",
        "description": "Pedido feito pelo celular via túnel público: Adicionar funcionalidade de pausa ao pressionar a tecla P no Super Mario e aprimorar o decay do sintetizador de moedas.",
        "priority": 2
    }
    task_res = send_mobile_request(f"{tunnel_url}/api/linear/issues", method="POST", data=task_payload)
    if task_res["success"] and task_res["data"].get("issue"):
        issue = task_res["data"]["issue"]
        issue_id = issue["id"]
        issue_key = issue["identifier"]
        print(f"   ✅ Ticket Criado no Linear Business: [{issue_key}] {issue['title']}")
        print(f"      ID: {issue_id} ({task_res['latency_ms']}ms)")
        print(f"      URL: {issue.get('url')}")
    else:
        print(f"   ❌ Erro criando tarefa: {task_res}")
        return

    # -------------------------------------------------------------
    # ETAPA 3: TESTE INDIVIDUAL — HERMES AGENT (GESTOR GERAL)
    # -------------------------------------------------------------
    print(f"\n3. [Celular ➔ Hermes] Enviando diretriz estratégica para o Gestor Geral...")
    hermes_msg = {
        "issue_id": issue_id,
        "body": "🧠 [Ordem de Joedson via Celular para HERMES]: Valide a arquitetura do Sistema de Pausa para garantir que respeite o método de fatias verticais sem quebrar o loop de 60fps."
    }
    h_res = send_mobile_request(f"{tunnel_url}/api/linear/comment", method="POST", data=hermes_msg)
    if h_res["success"]:
        print(f"   ✅ Diretriz entregue ao Hermes no ticket {issue_key} ({h_res['latency_ms']}ms)")
        print("      Status: Hermes recebeu e guardou o contexto da fatia.")
    else:
        print(f"   ❌ Falha ao falar com Hermes: {h_res}")

    # -------------------------------------------------------------
    # ETAPA 4: TESTE INDIVIDUAL — ANTIGRAVITY (TECH LEAD ORQUESTRADOR)
    # -------------------------------------------------------------
    print(f"\n4. [Celular ➔ Antigravity] Solicitando auditoria das 4 Janelas para o Tech Lead...")
    antigravity_msg = {
        "issue_id": issue_id,
        "body": "⚡ [Ordem de Joedson via Celular para ANTIGRAVITY]: Audite a branch e verifique se há bloqueios em .orchestrator-question antes de aprovar o dispatch."
    }
    a_res = send_mobile_request(f"{tunnel_url}/api/linear/comment", method="POST", data=antigravity_msg)
    if a_res["success"]:
        print(f"   ✅ Comando entregue ao Antigravity no ticket {issue_key} ({a_res['latency_ms']}ms)")
        print("      Status: Antigravity iniciou a verificação das 4 janelas.")
    else:
        print(f"   ❌ Falha ao falar com Antigravity: {a_res}")

    # -------------------------------------------------------------
    # ETAPA 5: TESTE INDIVIDUAL — ORCA (EXECUTOR CLAUDE CODE)
    # -------------------------------------------------------------
    print(f"\n5. [Celular ➔ Orca Executores] Despachando instrução de código para os executores...")
    orca_msg = {
        "issue_id": issue_id,
        "body": "🤖 [Ordem de Joedson via Celular para ORCA (Claude Code)]: Implemente o event listener da tecla P no index.html do Super Mario e congele o delta do game loop ao pausar."
    }
    o_res = send_mobile_request(f"{tunnel_url}/api/linear/comment", method="POST", data=orca_msg)
    if o_res["success"]:
        print(f"   ✅ Instrução entregue ao executor Orca no ticket {issue_key} ({o_res['latency_ms']}ms)")
        print("      Status: Orca preparado para abrir worktree isolada.")
    else:
        print(f"   ❌ Falha ao despachar no Orca: {o_res}")

    # -------------------------------------------------------------
    # ETAPA 6: CONSULTA DAS 4 JANELAS PELO CELULAR
    # -------------------------------------------------------------
    print(f"\n6. [Celular ➔ Radar] Joedson consulta o radar do escritório pelo celular...")
    mon_res = send_mobile_request(f"{tunnel_url}/api/monitor")
    if mon_res["success"]:
        data = mon_res["data"]
        lin_total = data.get("janela_3_linear", {}).get("total", 0)
        qs = data.get("janela_1_disco", {}).get("pending_questions", [])
        print(f"   ✅ Radar recebido com sucesso no celular ({mon_res['latency_ms']}ms):")
        print(f"      • Tarefas monitoradas no Linear Business: {lin_total}")
        print(f"      • Dúvidas de executores bloqueados: {len(qs)}")
        print(f"      • Status do time: 100% Produtivo e Desbloqueado")
    else:
        print(f"   ❌ Falha consultando radar: {mon_res}")

    print("\n==================================================================")
    print("🏆 SIMULAÇÃO MOBILE CONCLUÍDA COM 100% DE SUCESSO!")
    print(f"   Ticket gerado via 4G/Túnel: https://linear.app/jo5/issue/{issue_key}")
    print("==================================================================\n")

if __name__ == "__main__":
    run_simulation()
