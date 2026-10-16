# REQUISITOS DO BACKEND (PROJETO DARKLAB AI)

Este documento especifica a infraestrutura, contas, chaves e dependências necessárias para a reconstrução do cérebro da aplicação.

---

## A) FERRAMENTAS & STACK SELECIONADA

| Camada | Tecnologia | Justificativa |
| :--- | :--- | :--- |
| **API Web** | **FastAPI + Uvicorn** (Python 3.13) | Alta performance assíncrona, validação nativa Pydantic v2 e compatibilidade total. |
| **Banco de Dados** | **SQLite (WAL) / Supabase (Postgres)** | Suporte híbrido: roda 100% autônomo e localmente via SQLite WAL ou conectado ao Postgres Supabase. |
| **Autenticação** | **JWT (python-jose + bcrypt)** | Geração e validação de tokens JWT compatíveis com o cliente SPA do DarkLab. |
| **Transcrição / Áudio** | **faster-whisper (local) + Groq API (fallback)** | faster-whisper já disponível localmente para zero custo, com Groq como acelerador. |
| **IA / LLM (Geração)** | **DeepSeek API / OpenRouter** | Motor de raciocínio e síntese com custo mínimo e alta fidelidade via endpoint OpenAI-compatible. |
| **Síntese de Voz (TTS)** | **Edge-TTS / Groq Audio** | Geração neural de áudio sem necessidade de GPU dedicada. |
| **Processamento Assíncrono** | **FastAPI BackgroundTasks** | Fila leve em memória para renderização e síntese sem sobrecarga de infraestrutura. |

---

## B) CONTAS E CHAVES NECESSÁRIAS

1. **DeepSeek / OpenRouter:**
   - Para geração de roteiros, ganchos e análise de canais virais.
   - Link: https://platform.deepseek.com ou https://openrouter.ai
2. **Groq (Opcional - Aceleração):**
   - Para transcrição ultrarrápida via Whisper-large-v3.
   - Link: https://console.groq.com
3. **Supabase (Opcional se usar persistência SQLite local):**
   - Para banco Postgres em nuvem e autenticação gerenciada.
   - Link: https://supabase.com

---

## C) STATUS DE CONFIGURAÇÃO (O QUE JÁ TEMOS vs O QUE FALTA)

- [x] **Python 3.13.7 + FastAPI + Uvicorn**: ✅ Instalado e verificado
- [x] **Ripgrep 15.1.0**: ✅ Instalado e verificado
- [x] **Node.js v24.6.0 + NPM 11.5.1**: ✅ Instalado e verificado
- [x] **Motor TTS Local (Edge-TTS)**: ✅ Instalado e verificado
- [x] **Motor Whisper Local (faster-whisper)**: ✅ Instalado e verificado
- [x] **OpenRouter API Key**: ✅ Disponível no ambiente (`OPENROUTER_API_KEY`)
- [ ] **Supabase URL / Chaves**: ⚠️ Opcional (Modo local SQLite pronto como padrão)
- [ ] **Groq API Key**: ⚠️ Opcional (Whisper local atende 100%)

---

## D) COMO PREENCHER O .env (3 PASSOS)

1. Copie o arquivo `.env.example` para `.env` na raiz do projeto ou backend.
2. Insira suas chaves em `DEEPSEEK_API_KEY` ou `OPENROUTER_API_KEY`.
3. Mantenha `JWT_SECRET` com uma chave segura aleatória ou utilize a gerada automaticamente.
