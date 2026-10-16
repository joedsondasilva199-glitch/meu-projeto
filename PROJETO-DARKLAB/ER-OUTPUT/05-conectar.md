# RELATÓRIO DA FASE 5 — CONECTAR (ER-BLACK)

## 1. MAPA DE EQUIVALÊNCIA DE ROTAS (FRONTEND $\longrightarrow$ BACKEND NOVO)

| Rota Original do Alvo | Rota no Backend Reconstruído | Método | Tipo de Resposta |
| :--- | :--- | :--- | :--- |
| `https://api.darklabapp.com/api/auth/register` | `/api/auth/register` | `POST` | JSON (Token JWT + Workspace) |
| `https://api.darklabapp.com/api/auth/login` | `/api/auth/login` | `POST` | JSON (Token JWT + Claims) |
| `https://api.darklabapp.com/api/auth/me` | `/api/auth/me` | `GET` | JSON (Perfil + Saldo de Tokens) |
| `https://api.darklabapp.com/api/tokens/balance` | `/api/tokens/balance` | `GET` | JSON (Balanço Mensal + Avulso) |
| `https://api.darklabapp.com/api/viral-lab/niche-finder` | `/api/viral-lab/niche-finder` | `GET` | JSON (Array de canais com Outlier Score) |
| `https://api.darklabapp.com/api/scripts/generate` | `/api/scripts/generate` | `POST` | JSON (Roteiro POV estruturado) |
| `https://api.darklabapp.com/api/tts/generate-voice` | `/api/tts/generate-voice` | `POST` | JSON (Áudio URL + Débito de Tokens) |
| `https://api.darklabapp.com/api/storyboard/auto-scenes` | `/api/storyboard/auto-scenes` | `POST` | JSON (Array de cenas + Prompts 8k) |
| `https://api.darklabapp.com/api/kanban/board` | `/api/kanban/board` | `GET` | JSON (Quadro de estágios de produção) |
| `https://api.darklabapp.com/public/*` | `/public/*` | `GET/POST` | JSON (Stubs neutros compatíveis) |

---

## 2. ADAPTAÇÕES DE AUTENTICAÇÃO E JWT

- **Claims incluídos no token JWT:**
  - `sub`: Identificador único do usuário.
  - `user_id`: ID do usuário.
  - `email`: E-mail autenticado.
  - `workspace_id`: ID do tenant isolado.
  - `role`: Papel de acesso (`director`, `admin`, `operator`).
  - `exp`: Expiração configurada para 1440 minutos (renovação automática).
- **Consumo transparente pelo Front:** O token emitido é gravado no `localStorage` sob a chave `darklab_token` ou `auth`, e lido automaticamente pelos interceptores em `bundle_darklab.js`, `darklab_engine.js` e `dashboard.js`.

---

## 3. RESULTADO DO TESTE PONTA-A-PONTA REAL (`test_integration_http.py`)

O servidor integrado FastAPI + Frontend foi submetido a testes HTTP reais em `http://127.0.0.1:8088`:

- **Entrega de UI:**
  - `GET /` $\rightarrow$ `HTTP 200 OK` (43.890 bytes servidos)
  - `GET /landing.html` $\rightarrow$ `HTTP 200 OK` (126.102 bytes servidos)
- **Registro Real:** `POST /api/auth/register` $\rightarrow$ `HTTP 201 Created`
- **Consulta ao Viral Lab:** `GET /api/viral-lab/niche-finder?tab=exploding` $\rightarrow$ `HTTP 200 OK` (5 canais minerados com Outlier Score)
- **Geração de Roteiro:** `POST /api/scripts/generate` $\rightarrow$ `HTTP 201 Created` (Roteiro POV com 4 blocos dramáticos)
- **Narração Neural & Débito:** `POST /api/tts/generate-voice` $\rightarrow$ `HTTP 201 Created` (Arquivo de áudio WAV gerado e debitado da carteira)
- **Cenas do Storyboard:** `POST /api/storyboard/auto-scenes` $\rightarrow$ `HTTP 201 Created` (14 cenas visuais com prompts cinematográficos)
- **Esteira Kanban:** `GET /api/kanban/board` $\rightarrow$ `HTTP 200 OK` (Quadro industrial completo)

---

## 4. GATE DE SEGURANÇA (FASE 5)

- [x] `API_BASE_URL` configurada e apontando para o backend local reconstruído
- [x] Autenticação e claims de JWT funcionando ponta a ponta
- [x] Cada fatia do núcleo testada via HTTP e validada no front clonado
- [x] Nenhuma chamada pendente vazando para o alvo original

Confirmação: **FASE 5 OK. Front conectado ao backend novo. Núcleo funcionando ponta a ponta.**
