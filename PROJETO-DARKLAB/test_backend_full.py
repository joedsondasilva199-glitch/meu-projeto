import sys
import os
import uuid

# Adiciona paths
BACKEND_DIR = r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT\backend"
OUTPUT_DIR = r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT"
for p in [BACKEND_DIR, OUTPUT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    print("="*60)
    print("INICIANDO SUITE DE TESTES DE CONTRATO E INTEGRACAO (FASE 4)")
    print("="*60)

    with TestClient(app) as client:
        passed = 0
        failed = 0

        def assert_test(name, condition, details=""):
            nonlocal passed, failed
            if condition:
                print(f"[OK] {name} {details}")
                passed += 1
            else:
                print(f"[FAIL] {name} {details}")
                failed += 1

        # 1. HEALTH CHECK
        r = client.get("/api/health")
        assert_test("Health Check", r.status_code == 200 and r.json().get("status") == "ok", f"Status: {r.status_code}")

        # 2. AUTH - REGISTER
        uid = uuid.uuid4().hex[:6]
        email = f"operador_{uid}@darklabapp.com"
        reg_payload = {
            "name": f"Operador {uid}",
            "email": email,
            "password": "SenhaSeguraDarkLab2026!",
            "workspace_name": f"Workspace {uid}",
            "plan_tier": "plus"
        }
        r = client.post("/api/auth/register", json=reg_payload)
        data = r.json()
        assert_test("Auth Register", r.status_code == 201 and "access_token" in data, f"User: {data.get('email')}")
        token = data.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        # 3. AUTH - LOGIN
        r = client.post("/api/auth/login", json={"email": email, "password": "SenhaSeguraDarkLab2026!"})
        assert_test("Auth Login", r.status_code == 200 and "access_token" in r.json())

        # 4. AUTH - ME
        r = client.get("/api/auth/me", headers=headers)
        assert_test("Auth Me", r.status_code == 200 and r.json().get("email") == email)

        # 5. TOKENS - BALANCE
        r = client.get("/api/tokens/balance", headers=headers)
        bal_data = r.json()
        assert_test("Tokens Balance", r.status_code == 200 and bal_data.get("total_balance", 0) > 0, f"Saldo Inicial: {bal_data.get('total_balance')}")

        # 6. VIRAL LAB - NICHE FINDER
        r = client.get("/api/viral-lab/niche-finder?tab=exploding", headers=headers)
        niche_list = r.json()
        assert_test("Viral Lab Niche Finder", r.status_code == 200 and len(niche_list) > 0, f"Canais minerados: {len(niche_list)}")

        # 7. VIRAL LAB - ANALYZE VIDEO
        r = client.post("/api/viral-lab/analyze-video", json={"url_or_id": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}, headers=headers)
        assert_test("Viral Lab Analyze Video", r.status_code == 200 and "retention_score" in r.json())

        # 8. SCRIPTS - GENERATE (POV)
        script_payload = {
            "title": "O Segredo Proibido do Almirante Byrd",
            "niche": "misterio",
            "topic_description": "A expedição secreta à Antártida além das montanhas de gelo.",
            "formula_style": "pov_conflito",
            "target_duration_minutes": 15
        }
        r = client.post("/api/scripts/generate", json=script_payload, headers=headers)
        script_data = r.json()
        script_id = script_data.get("id")
        assert_test("Script Generate POV", r.status_code == 201 and script_id is not None, f"Script ID: {script_id}")

        # 8.1 NOVA FUNÇÃO: EXPORTAÇÃO TELEPROMPTER & MARKDOWN
        r = client.get(f"/api/scripts/{script_id}/export?format=teleprompter", headers=headers)
        assert_test("Nova Função - Export Teleprompter", r.status_code == 200 and "[GANCHO 30S]" in r.json().get("content", ""))
        r = client.get(f"/api/scripts/{script_id}/export?format=markdown", headers=headers)
        assert_test("Nova Função - Export Markdown", r.status_code == 200 and "## 1. Gancho Inicial" in r.json().get("content", ""))

        # 9. TTS - GENERATE VOICE (COM DÉBITO)
        r = client.post("/api/tts/generate-voice", json={"script_id": script_id, "voice_name": "Marcus (Tensão)"}, headers=headers)
        tts_data = r.json()
        assert_test("TTS Generate Voice", r.status_code == 201 and "audio_url" in tts_data, f"Audio URL: {tts_data.get('audio_url')}")

        # 10. TTS - SYNTHESIZE DIRETO
        r = client.post("/api/tts/synthesize", json={"text": "Teste de áudio neural.", "voice_id": "marcus", "user_id": email})
        assert_test("TTS Direct Synthesize", r.status_code == 200 and "audio_url" in r.json())

        # 11. STORYBOARD - AUTO SCENES
        r = client.post("/api/storyboard/auto-scenes", json={"script_id": script_id, "seconds_per_scene": 4}, headers=headers)
        sb_data = r.json()
        assert_test("Storyboard Auto Scenes", r.status_code == 201 and sb_data.get("total_scenes", 0) > 0, f"Total cenas: {sb_data.get('total_scenes')}")

        # 12. STORYBOARD - SRT
        r = client.get(f"/api/storyboard/{script_id}/srt", headers=headers)
        srt_data = r.json()
        assert_test("Storyboard SRT Export", r.status_code == 200 and "srt_content" in srt_data)

        # 13. KANBAN - BOARD
        r = client.get("/api/kanban/board", headers=headers)
        assert_test("Kanban Board", r.status_code == 200 and "columns" in r.json())

        # 14. KANBAN - CREATE CARD
        r = client.post("/api/kanban/cards", json={"title": "Novo Vídeo Misterioso", "column_status": "ideia", "script_id": script_id}, headers=headers)
        card_id = r.json().get("id")
        assert_test("Kanban Create Card", r.status_code == 201 and card_id is not None)

        # 15. KANBAN - MOVE CARD
        r = client.put(f"/api/kanban/cards/{card_id}/move", json={"column_status": "audio", "position_order": 1}, headers=headers)
        assert_test("Kanban Move Card", r.status_code == 200 and r.json().get("column_status") == "audio")

        # 16. MEDIA LIBRARY
        r = client.get("/api/media/library", headers=headers)
        assert_test("Media Library", r.status_code == 200 and isinstance(r.json(), list))

        # 17. MCP TOOLS & CALL
        r = client.get("/api/mcp/tools")
        assert_test("MCP List Tools", r.status_code == 200 and "tools" in r.json())
        r = client.post("/api/mcp/call", json={"name": "find_trending_niches", "arguments": {"tab": "exploding"}})
        assert_test("MCP Call Tool", r.status_code == 200 and not r.json().get("isError"))

        # 18. PERFUMARIA STUBS
        r = client.post("/public/waitlist", json={"email": "teste@email.com"})
        assert_test("Perfumaria Waitlist", r.status_code == 200 and r.json().get("success"))
        r = client.get("/public/platform-settings")
        assert_test("Perfumaria Settings", r.status_code == 200 and not r.json().get("maintenance"))

        print("="*60)
        print(f"RESULTADO FINAL: {passed} PASSARAM | {failed} FALHARAM")
        print("="*60)
        return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
