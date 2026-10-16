import sys
import os
import time
import subprocess
import urllib.request
import json

SERVER_PORT = 8088
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"

def test_integration():
    print("="*60)
    print(f"TESTE DE INTEGRAÇÃO PONTA-A-PONTA (FASE 5) NA PORTA {SERVER_PORT}")
    print("="*60)

    # 1. Inicia o servidor uvicorn em subprocesso
    env = os.environ.copy()
    backend_path = r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT\backend"
    output_path = r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT"
    env["PYTHONPATH"] = f"{backend_path};{output_path};" + env.get("PYTHONPATH", "")

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(SERVER_PORT)],
        cwd=backend_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        # Aguarda subida do servidor
        print("Aguardando servidor subir...")
        ready = False
        for _ in range(20):
            try:
                with urllib.request.urlopen(f"{BASE_URL}/api/health", timeout=1) as res:
                    if res.status == 200:
                        ready = True
                        break
            except Exception:
                time.sleep(0.5)

        if not ready:
            print("[FAIL] O servidor não respondeu dentro do tempo limite.")
            return False

        print("[OK] Servidor respondendo em /api/health!")

        # 2. Testa entrega da interface (HTML do Dashboard e Landing)
        with urllib.request.urlopen(f"{BASE_URL}/", timeout=3) as res:
            assert res.status == 200
            print(f"[OK] Frontend Dashboard servido com status {res.status} ({len(res.read())} bytes)")

        with urllib.request.urlopen(f"{BASE_URL}/landing.html", timeout=3) as res:
            assert res.status == 200
            print(f"[OK] Frontend Landing Page servida com status {res.status} ({len(res.read())} bytes)")

        # 3. Testa chamada de registro vinda do front
        reg_payload = json.dumps({
            "name": "Diretor DarkLAB Clone",
            "email": f"diretor_{int(time.time())}@darklabapp.com",
            "password": "SenhaSeguraDarkLab2026!",
            "workspace_name": "Estúdio DarkLAB Clone",
            "plan_tier": "plus"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/api/auth/register",
            data=reg_payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode("utf-8"))
            token = data["access_token"]
            print(f"[OK] Registro ponta-a-ponta via HTTP realizado: {data['email']}")

        # 4. Testa busca no Viral Lab
        req = urllib.request.Request(
            f"{BASE_URL}/api/viral-lab/niche-finder?tab=exploding",
            headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, timeout=3) as res:
            channels = json.loads(res.read().decode("utf-8"))
            print(f"[OK] Viral Lab consumido com sucesso ({len(channels)} canais)")

        # 5. Testa geração de roteiro
        script_payload = json.dumps({
            "title": "O Mistério da Estação Vostok",
            "niche": "misterio",
            "topic_description": "O lago pré-histórico isolado por 15 milhões de anos sob o gelo.",
            "formula_style": "pov_conflito"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/api/scripts/generate",
            data=script_payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, timeout=3) as res:
            script_data = json.loads(res.read().decode("utf-8"))
            script_id = script_data["id"]
            print(f"[OK] Roteiro gerado via HTTP: {script_data['title']} (ID: {script_id})")

        # 6. Testa síntese de voz (TTS)
        tts_payload = json.dumps({
            "script_id": script_id,
            "voice_name": "Marcus (Tensão/Mistério)"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/api/tts/generate-voice",
            data=tts_payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, timeout=3) as res:
            voice_data = json.loads(res.read().decode("utf-8"))
            print(f"[OK] Narração TTS gerada com sucesso: {voice_data['audio_url']}")

        # 7. Testa storyboard automático
        sb_payload = json.dumps({
            "script_id": script_id,
            "seconds_per_scene": 4
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/api/storyboard/auto-scenes",
            data=sb_payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, timeout=3) as res:
            sb_data = json.loads(res.read().decode("utf-8"))
            print(f"[OK] Storyboard gerado com {sb_data['total_scenes']} cenas visuais")

        # 8. Testa quadro Kanban
        req = urllib.request.Request(
            f"{BASE_URL}/api/kanban/board",
            headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, timeout=3) as res:
            kb_data = json.loads(res.read().decode("utf-8"))
            print(f"[OK] Quadro Kanban consultado com sucesso")

        print("="*60)
        print("[SUCESSO] INTEGRAÇÃO PONTA-A-PONTA CONCLUÍDA COM 100% DE SUCESSO!")
        print("="*60)
        return True

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    ok = test_integration()
    sys.exit(0 if ok else 1)
