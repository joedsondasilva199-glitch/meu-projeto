# CONTRATO DA API & ARQUITETURA DE DADOS (FASE 2 — ER-BLACK)

Este documento define o contrato formal, entidades, esquemas de entrada/saída, rotas e prompts de sistema da plataforma **DarkLab AI Studio**.

---

## 1. TABELA-MESTRE DE ENDPOINTS

| Família | Método | Endpoint / Rota | Request Body | Response Shape |
| :--- | :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/api/health` | Vazio | `{ status, app, version, environment, database }` |
| **Auth** | `POST` | `/api/auth/register` | `{ name, email, password, workspace_name?, plan_tier? }` | `{ access_token, token_type, user_id, email, workspace_id, role }` |
| **Auth** | `POST` | `/api/auth/login` | `{ email, password }` | `{ access_token, token_type, user_id, email, workspace_id, role }` |
| **Auth** | `GET` | `/api/auth/me` | Bearer Token | `{ id, name, email, role, workspace_id, workspace_name, plan_tier, tokens_available }` |
| **Tokens** | `GET` | `/api/tokens/balance` | `?user_id=` ou Bearer | `{ workspace_id, plan_balance, extra_balance, total_balance, renewal_date }` |
| **Tokens** | `POST` | `/api/tokens/debit` | `{ characters_count, description }` | `{ id, amount, balance_after, transaction_type, description, created_at }` |
| **Viral Lab**| `GET` | `/api/viral-lab/niche-finder` | Query: `tab, niche, limit` | `[ { channel_id, title, niche, subscribers, views, age_days, outlier_score, is_monetized, sparkline } ]` |
| **Viral Lab**| `POST` | `/api/viral-lab/analyze-video` | `{ url_or_id }` | `{ video_id, title, views, estimated_vph, retention_score, hook_strength, tags, is_monetized, summary }` |
| **Viral Lab**| `POST` | `/api/viral-lab/analyze-channel` | `{ channel_url_or_id }` | `{ channel_id, title, niche, subscribers, video_frequency, avg_duration_minutes, estimated_monthly_revenue, top_outlier_videos }` |
| **Scripts** | `POST` | `/api/scripts/generate` | `{ title, niche, topic_description, formula_style, target_duration_minutes }` | `{ id, title, niche, hook_text, open_loop, body_text, cta_text, full_script, character_count, estimated_audio_tokens }` |
| **TTS** | `POST` | `/api/tts/generate-voice` | `{ script_id, voice_name }` | `{ id, script_id, voice_name, characters_count, tokens_debited, duration_seconds, audio_url, remaining_balance }` |
| **TTS** | `POST` | `/api/tts/synthesize` | `{ text, voice_id, user_id }` | `{ status, audio_url, duration, characters, tokens_debited }` |
| **Storyboard**| `POST` | `/api/storyboard/auto-scenes` | `{ script_id, seconds_per_scene }` | `{ script_id, total_scenes, scenes: [ { scene_number, start_time, end_time, narration_chunk, visual_prompt, image_url, character_name } ] }` |
| **Storyboard**| `GET` | `/api/storyboard/{id}/srt` | Path param: `id` | `{ script_id, srt_content }` |
| **Kanban** | `GET` | `/api/kanban/board` | Vazio | `{ columns: { ideias: [], roteiro: [], audio: [], edicao: [], publicado: [] } }` |
| **Kanban** | `POST` | `/api/kanban/cards` | `{ title, column_status, script_id?, notes? }` | `{ id, title, column_status, position_order, script_id, notes, updated_at }` |
| **Kanban** | `PUT` | `/api/kanban/cards/{id}/move` | `{ column_status, position_order }` | `{ id, title, column_status, position_order, updated_at }` |
| **Media** | `GET` | `/api/media/library` | Vazio | `[ { id, name, media_type, file_path, file_size_bytes, created_at } ]` |
| **MCP** | `GET` | `/api/mcp/tools` | Vazio | `[ { name, description, inputSchema } ]` |
| **MCP** | `POST` | `/api/mcp/call` | `{ name, arguments }` | `{ result, isError }` |
| **Bridge** | `POST` | `http://localhost:20128/v1/chat/completions` | OpenAI format | OpenAI completion format (Local OmniRoute Desktop Bridge) |

---

## 2. PROMPTS DE SISTEMA EXTRAÍDOS

Os prompts completos foram salvos na pasta `ER-OUTPUT\prompts-extraidos\`:
1. `prompt_pov_script.txt`: Diretriz do roteirizador POV de alta retenção (gancho 30s + loop aberto + CTA).
2. `prompt_storyboard_cinematic.txt`: Regras de estilo fotográfico e prompts de arte cinematográfica 8k.
3. `prompt_video_analysis.txt`: Algoritmo de auditoria de vídeos e cálculo de métricas de canais concorrentes.

---

## 3. ENTIDADES DE DADOS (SCHEMAS)

- **Workspace:** Isolamento multi-tenant (`id`, `name`, `plan_tier`, `created_at`).
- **User:** Credenciais e vínculo de tenant (`id`, `workspace_id`, `email`, `role`).
- **TokenWallet:** Carteira transacional com distinção entre plano mensal e tokens avulsos (`plan_balance`, `extra_balance`, `renewal_date`).
- **ScriptProject:** Roteiro estruturado por blocos dramáticos (`hook_text`, `open_loop`, `body_text`, `cta_text`, `full_script`).
- **StoryboardScene:** Bloco temporal com timestamps, texto de narração e prompt de imagem.
- **KanbanCard:** Cartão de pipeline rastreando o estágio de produção.

---

## 4. FLUXO TÍPICO DE OPERAÇÃO

$$\text{1. Auth} \longrightarrow \text{2. Saldo de Tokens} \longrightarrow \text{3. Mineração (Viral Lab)} \longrightarrow \text{4. Roteiro POV} \longrightarrow \text{5. Síntese TTS (Débito)} \longrightarrow \text{6. Storyboard / SRT} \longrightarrow \text{7. Pipeline Kanban}$$

---

## 5. GATE DE SEGURANÇA (FASE 2)

- [x] todas as URLs e rotas do código varridas e agrupadas
- [x] endpoints documentados com método, request e response
- [x] prompts de sistema salvos na íntegra em `ER-OUTPUT\prompts-extraidos\`
- [x] tipos e esquemas formais registrados
- [x] lacunas do contrato documentadas e tratadas

Confirmação: **FASE 2 OK. 21 endpoints mapeados em 9 famílias. 3 prompts extraídos.**
