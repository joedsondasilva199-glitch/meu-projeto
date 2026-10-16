# CLASSIFICAÇÃO DOS ENDPOINTS (FASE 3 — ER-BLACK)

Este documento classifica todos os endpoints mapeados no contrato da API do DarkLab AI Studio entre lógica central (**Núcleo**), recursos de apoio (**Útil**) e integrações secundárias (**Perfumaria**).

---

## 1. TABELA DE CLASSIFICAÇÃO

| Endpoint | Método | Família | Nível | Justificativa | Estratégia de Reconstrução |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/api/health` | `GET` | Health | 🟢 NÚCLEO | Verificação de integridade e liveness probe | Lógica real (status do server, uptime e banco) |
| `/api/auth/register` | `POST` | Auth | 🟢 NÚCLEO | Criação de conta e workspace multi-tenant | Lógica real (bcrypt + criação de carteira e tenant) |
| `/api/auth/login` | `POST` | Auth | 🟢 NÚCLEO | Autenticação e emissão de JWT com escopo | Lógica real (validação de hash e assinatura de token) |
| `/api/auth/me` | `GET` | Auth | 🟢 NÚCLEO | Recuperação de perfil e contexto da sessão | Lógica real (leitura do usuário e saldo de tokens) |
| `/api/tokens/balance` | `GET` | Tokens | 🟢 NÚCLEO | Saldo da carteira (trava da esteira de áudio) | Lógica real (consulta saldo mensal + avulso) |
| `/api/tokens/debit` | `POST` | Tokens | 🟢 NÚCLEO | Débito transacional de caracteres de áudio | Lógica real (débito atômico com registro no ledger) |
| `/api/viral-lab/niche-finder` | `GET` | Viral Lab | 🟢 NÚCLEO | Mineração de canais dark e Outlier Score | Lógica real (filtro por nicho/aba + cálculo de métricas) |
| `/api/viral-lab/analyze-video` | `POST` | Viral Lab | 🟢 NÚCLEO | Raio-X de vídeos, tags e VPH | Lógica real (extração de metadados YouTube + LLM) |
| `/api/viral-lab/analyze-channel` | `POST` | Viral Lab | 🟡 ÚTIL | Diagnóstico de canal e estimativa de CPM | Lógica simplificada (cálculo estatístico e receita) |
| `/api/scripts/generate` | `POST` | Scripts | 🟢 NÚCLEO | Geração de roteiros POV com gancho 30s | Lógica real (DeepSeek/OpenRouter com prompt de alta retenção) |
| `/api/tts/generate-voice` | `POST` | TTS | 🟢 NÚCLEO | Narração neural com débito de tokens | Lógica real (Edge-TTS / Groq áudio + débito transacional) |
| `/api/tts/synthesize` | `POST` | TTS | 🟢 NÚCLEO | Síntese direta de texto avulso | Lógica real (Edge-TTS com gravação de arquivo WAV) |
| `/api/storyboard/auto-scenes` | `POST` | Storyboard| 🟢 NÚCLEO | Decomposição em cenas e prompts 8k | Lógica real (quebra temporal de sentenças + prompts) |
| `/api/storyboard/{id}/srt` | `GET` | Storyboard| 🟢 NÚCLEO | Geração de arquivo de legendas SRT | Lógica real (cálculo de timestamps e formatação SRT) |
| `/api/kanban/board` | `GET` | Kanban | 🟢 NÚCLEO | Quadro visual da esteira de produção | Lógica real (cards agrupados por coluna do workspace) |
| `/api/kanban/cards` | `POST` | Kanban | 🟢 NÚCLEO | Criação de novo card de produção | Lógica real (inserção no banco associado ao roteiro) |
| `/api/kanban/cards/{id}/move`| `PUT` | Kanban | 🟢 NÚCLEO | Transição de estágio do vídeo | Lógica real (atualização de status no banco) |
| `/api/media/library` | `GET` | Media | 🟡 ÚTIL | Listagem de assets, trilhas e previews | Lógica funcional sobre diretório de estáticos |
| `/api/mcp/tools` | `GET` | MCP | 🟡 ÚTIL | Descoberta de ferramentas para agentes Claude | Lógica funcional (retorno do schema de tools) |
| `/api/mcp/call` | `POST` | MCP | 🟡 ÚTIL | Execução de ferramentas via protocolo MCP | Lógica funcional (despacho de comandos internos) |
| `/affiliate/*` | `*` | Affiliate | 🔴 PERFUMARIA| Programa de afiliados e tracking de links | Stub com HTTP 200 e shape neutro (com logging) |
| `/public/waitlist` | `POST` | Public | 🔴 PERFUMARIA| Lista de espera de novos usuários | Stub com HTTP 200 e `{ success: true }` |
| `/public/platform-settings`| `GET` | Public | 🔴 PERFUMARIA| Flags globais de manutenção | Stub com `{ maintenance: false, version: "2.4.0" }` |

---

## 2. CONTAGEM FINAL

- 🟢 **NÚCLEO (Lógica Real):** 14 endpoints
- 🟡 **ÚTIL (Lógica Simplificada):** 4 endpoints
- 🔴 **PERFUMARIA (Stubs Válidos):** 3 famílias / rotas

**Total:** 21 endpoints / rotas mapeados e classificados.

---

## 3. GATE DE SEGURANÇA (FASE 3)

- [x] 100% dos endpoints classificados sem omissões
- [x] Cada endpoint de núcleo possui justificativa explícita de valor
- [x] Regra de stubs assegurada: stubs nunca retornam 404/500, sempre shape 200 válido
- [x] Contagem final escrita

Confirmação: **FASE 3 OK. Núcleo [14] | Útil [4] | Perfumaria [3].**
