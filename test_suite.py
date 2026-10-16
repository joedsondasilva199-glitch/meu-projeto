#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_suite.py
=============
Bateria de Testes Abrangente de Ponta a Ponta (E2E) da Stack de Agentes:
[1] API Local & Healthcheck
[2] Cloudflare Tunnel Público (HTTPS)
[3] Linear Business (Conta, Equipe, Projetos & Tickets)
[4] Ciclo Completo de Issue & Comentários do Linear
[5] Orca ADE & Detector de Bloqueios (.orchestrator-question)
[6] Jogo Super Mario Bros AI (Assets, Canvas & Loop)
[7] Dashboard The Sims HQ (Interface, Canvas & Rotas)
[8] Hermes Agent & Gateway do Telegram
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

TEST_RESULTS = []

def record_test(name: str, passed: bool, details: str = "", latency_ms: float = 0):
    status_str = "✅ PASSOU" if passed else "❌ FALHOU"
    TEST_RESULTS.append({
        "name": name,
        "passed": passed,
        "details": details,
        "latency_ms": round(latency_ms, 2)
    })
    print(f"{status_str} | {name} ({round(latency_ms, 1)}ms)")
    if details:
        print(f"   └─ {details}")

def test_api_local():
    print("\n[TESTE 1] Testando Servidor de API Local (FastAPI)...")
    start = time.time()
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/api/health")
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
            latency = (time.time() - start) * 1000
            passed = (resp.status == 200 and data.get("status") == "healthy")
            record_test("Healthcheck Local (/api/health)", passed, f"Status: {resp.status}, Payload: {data.get('service')}", latency)
    except Exception as e:
        record_test("Healthcheck Local (/api/health)", False, f"Erro: {e}", (time.time() - start) * 1000)

def test_cloudflare_tunnel():
    print("\n[TESTE 2] Testando Cloudflare Tunnel Público (HTTPS)...")
    tunnel_file = "tunnel_url.txt"
    if not os.path.exists(tunnel_file):
        record_test("Cloudflare Tunnel", False, "Arquivo tunnel_url.txt não encontrado")
        return

    with open(tunnel_file, "r", encoding="utf-8") as f:
        url = f.read().strip()

    start = time.time()
    try:
        req = urllib.request.Request(f"{url}/api/health", headers={"User-Agent": "AntigravityTestBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            latency = (time.time() - start) * 1000
            passed = (resp.status == 200 and data.get("status") == "healthy")
            record_test("Cloudflare Public HTTPS (/api/health)", passed, f"URL: {url} | Código: {resp.status}", latency)
    except Exception as e:
        record_test("Cloudflare Public HTTPS (/api/health)", False, f"Erro: {e}", (time.time() - start) * 1000)

def test_linear_business():
    print("\n[TESTE 3] Testando Conexão e Direitos da Conta Business no Linear...")
    start = time.time()
    try:
        from linear_manager import LinearClient
        client = LinearClient()
        account = client.get_account_info()
        latency = (time.time() - start) * 1000
        plan = account.get("organization", {}).get("subscription", {}).get("type", "")
        org_name = account.get("organization", {}).get("name", "")
        user_name = account.get("name", "")
        passed = (bool(account.get("id")) and "business" in plan.lower())
        record_test("Linear Business Account", passed, f"Org: {org_name} | User: {user_name} | Plano: {plan}", latency)

        # Checa Teams
        teams = client.list_teams()
        joe_team = next((t for t in teams if t["key"] == "JOE"), None)
        record_test("Linear Team JOEDSON [JOE]", bool(joe_team), f"ID: {joe_team.get('id') if joe_team else 'N/A'}")

        # Checa Projetos
        projects = client.list_projects()
        mario_proj = next((p for p in projects if "mario" in p["name"].lower()), None)
        record_test("Projeto Super Mario Bros AI", bool(mario_proj), f"Encontrado: {mario_proj.get('name') if mario_proj else 'Não'}")

    except Exception as e:
        record_test("Linear Business Conexão", False, f"Erro: {e}", (time.time() - start) * 1000)

def test_linear_issue_lifecycle():
    print("\n[TESTE 4] Testando Ciclo de Vida do Ticket (Criar, Comentar & Atualizar)...")
    start = time.time()
    try:
        from linear_manager import LinearClient
        client = LinearClient()
        team_id = "9ee1e6c9-6bd6-4ec1-889e-53b4a07bf50b"

        # 1. Cria Issue de Teste
        res = client.create_issue(
            team_id=team_id,
            title="[TESTE-AUTOMATIZADO] Validação de Ciclo E2E",
            description="Tarefa temporária criada para validação de ciclo da stack de agentes.",
            priority=4
        )
        issue = res.get("issue", {})
        issue_id = issue.get("id")
        identifier = issue.get("identifier")
        record_test("Linear Create Issue", bool(issue_id), f"Issue criada: {identifier}")

        if issue_id:
            # 2. Adiciona Comentário
            c_res = client.add_comment(issue_id, "Comentário de teste automático do Tech Lead Antigravity.")
            record_test("Linear Add Comment", bool(c_res.get("comment", {}).get("id")), f"Comentário ID: {c_res.get('comment', {}).get('id')}")

            # 3. Mover estado para Canceled ou Done
            # Busca ID do estado Canceled
            teams = client.list_teams()
            joe_team = next((t for t in teams if t["key"] == "JOE"), {})
            canceled_state = next((s["id"] for s in joe_team.get("states", {}).get("nodes", []) if s["type"] == "canceled"), None)
            if canceled_state:
                u_res = client.update_issue_state(issue_id, canceled_state)
                record_test("Linear Update Issue State", bool(u_res.get("issue")), "Status alterado para Canceled (limpeza concluída)")

    except Exception as e:
        record_test("Linear Issue Lifecycle", False, f"Erro: {e}")

def test_orca_bridge():
    print("\n[TESTE 5] Testando Orca Bridge e Scanner de Bloqueios (.orchestrator-question)...")
    try:
        from orca_bridge import OrcaBridge
        bridge = OrcaBridge()
        
        # Scanner de perguntas
        questions = bridge.scan_for_questions()
        record_test("Orca Question Scanner", True, f"Varredura concluída sem falhas. Dúvidas pendentes: {len(questions)}")

        # Status do runtime
        st = bridge.status()
        record_test("Orca Status Check", isinstance(st, dict), f"Runtime: {st.get('runtimeState', 'detectado')}")
    except Exception as e:
        record_test("Orca Bridge", False, f"Erro: {e}")

def test_super_mario_game():
    print("\n[TESTE 6] Testando Jogo Super Mario Bros AI...")
    mario_path = r"d:\Super Mario AI\index.html"
    exists = os.path.exists(mario_path)
    if not exists:
        record_test("Super Mario File", False, "Arquivo index.html não encontrado")
        return

    with open(mario_path, "r", encoding="utf-8") as f:
        html = f.read()

    has_canvas = "<canvas id=\"canvas\"" in html
    has_audio = "AudioContext" in html
    has_mario = "mario = {" in html
    has_goomba = "spawnGoomba" in html
    has_powerup = "mushrooms" in html
    has_flag = "flagpole" in html

    all_features = has_canvas and has_audio and has_mario and has_goomba and has_powerup and has_flag
    record_test("Super Mario Engine", all_features, f"Tamanho: {len(html)} bytes | Canvas: {has_canvas} | Goombas: {has_goomba} | Powerups: {has_powerup} | Bandeira: {has_flag}")

    # Testa via rota HTTP
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/mario", timeout=3) as resp:
            record_test("Super Mario HTTP Route (/mario)", resp.status == 200, f"Código HTTP: {resp.status}")
    except Exception as e:
        record_test("Super Mario HTTP Route (/mario)", False, f"Erro: {e}")

def test_sims_dashboard():
    print("\n[TESTE 7] Testando The Sims HQ Dashboard...")
    office_path = r"d:\Stack de Agentes\dashboard\office.html"
    exists = os.path.exists(office_path)
    if not exists:
        record_test("The Sims HTML File", False, "Arquivo office.html não encontrado")
        return

    with open(office_path, "r", encoding="utf-8") as f:
        html = f.read()

    has_plumbob = "plumbob" in html
    has_canvas = "simsCanvas" in html
    has_sims = "SIMS = {" in html
    has_coffee = "COFFEE_MACHINE" in html
    has_mario_btn = "/mario" in html

    all_sims = has_plumbob and has_canvas and has_sims and has_coffee and has_mario_btn
    record_test("The Sims Engine & UI", all_sims, f"Tamanho: {len(html)} bytes | Plumbob: {has_plumbob} | Sims AI: {has_sims} | Café: {has_coffee}")

    # Testa via rota HTTP
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/office", timeout=3) as resp:
            record_test("The Sims HTTP Route (/office)", resp.status == 200, f"Código HTTP: {resp.status}")
    except Exception as e:
        record_test("The Sims HTTP Route (/office)", False, f"Erro: {e}")

def test_hermes_integration():
    print("\n[TESTE 8] Testando Hermes Agent & Gateway...")
    hermes_dir = r"C:\Users\Lipe\AppData\Local\hermes"
    agents_md = os.path.join(hermes_dir, "AGENTS.md")
    gateway_state = os.path.join(hermes_dir, "gateway_state.json")

    has_agents = os.path.exists(agents_md)
    has_stack_rules = False
    if has_agents:
        with open(agents_md, "r", encoding="utf-8") as f:
            content = f.read()
            has_stack_rules = "GESTOR GERAL" in content and "http://127.0.0.1:8000" in content

    record_test("Hermes AGENTS.md Conexão", has_stack_rules, "Regras de orquestração e API injetadas")

    # Verifica se o Gateway está rodando
    gw_connected = False
    if os.path.exists(gateway_state):
        try:
            with open(gateway_state, "r", encoding="utf-8") as f:
                data = json.load(f)
            tg_state = data.get("platforms", {}).get("telegram", {}).get("state")
            gw_connected = (data.get("gateway_state") == "running" and tg_state == "connected")
            record_test("Hermes Telegram Gateway", gw_connected, f"Gateway: {data.get('gateway_state')} | Telegram: {tg_state}")
        except Exception as e:
            record_test("Hermes Telegram Gateway", False, f"Erro de leitura: {e}")
    else:
        record_test("Hermes Telegram Gateway", False, "gateway_state.json não localizado")

def main():
    print("==================================================================")
    print("🧪 INICIANDO SUÍTE DE TESTES E2E DA STACK DE AGENTES PRO")
    print("==================================================================")

    test_api_local()
    test_cloudflare_tunnel()
    test_linear_business()
    test_linear_issue_lifecycle()
    test_orca_bridge()
    test_super_mario_game()
    test_sims_dashboard()
    test_hermes_integration()

    print("\n==================================================================")
    print("📊 RELATÓRIO CONSOLIDADO DOS TESTES:")
    print("==================================================================")
    total = len(TEST_RESULTS)
    passed = sum(1 for t in TEST_RESULTS if t["passed"])
    failed = total - passed
    print(f"Total de Testes Executados: {total}")
    print(f"Testes Aprovados:           {passed} ✅")
    print(f"Testes Falhos:              {failed} ❌")
    print(f"Taxa de Sucesso:            {(passed/total)*100:.1f}%\n")

    if failed == 0:
        print("🎉 TODOS OS TESTES PASSARAM COM 100% DE SUCESSO E EVIDÊNCIAS REAIS!")
    else:
        print("⚠️ Alguns testes apresentaram alertas. Verifique os detalhes acima.")
    print("==================================================================\n")

if __name__ == "__main__":
    main()
