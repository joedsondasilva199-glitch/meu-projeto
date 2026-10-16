# PROTOCOLO DE ORQUESTRAÇÃO DE AGENTES (AGENTS.md)

Este documento define as regras inegociáveis de operação do time de desenvolvimento autônomo com IA.

---

## 1. A ESTRUTURA DO TIME & PAPÉIS

| Papel | Agente / Ferramenta | Responsabilidade |
| :--- | :--- | :--- |
| **O Dono (Humano)** | Você | Define o produto, decide prioridades de negócio, aprova deploys sensíveis e custos. |
| **O Gestor Geral** | **Hermes Agent** | Guarda o contexto geral do projeto, decisões arquiteturais, método e supervisão macro. |
| **A IA Orquestradora** | **Antigravity (Tech Lead)** | Cria tickets no Linear, despacha tarefas no Orca, responde dúvidas dos executores e audita nas 4 janelas. |
| **Os Executores** | **Orca (Claude / Codex)** | Desenvolvem o código em worktrees isoladas e em paralelo; reportam no ticket e abrem PRs. |
| **A Fonte da Verdade ("O Quê")** | **Linear (Conta Business)** | Gestão de backlog, projetos, ciclos, SLAs e histórico das conversas de cada ticket. |
| **A Fonte da Verdade ("O Feito")** | **GitHub** | Código versionado, branches isoladas, testes automatizados e Pull Requests. |

---

## 2. O MÉTODO: CONSTRUÇÃO POR FATIAS VERTICAIS

> **Regra de Ouro:** NUNCA construa em camadas horizontais ("todo o frontend primeiro", "todo o banco depois") e NUNCA peça "faça o app inteiro".

Cada funcionalidade é entregue como uma **Fatia Vertical Completa e Funcional**:
$$\text{Banco de Dados} \longrightarrow \text{Endpoints de API} \longrightarrow \text{Interface (UI)} \longrightarrow \text{Integração Real} \longrightarrow \text{Teste com Evidência}$$

### As Fases do Projeto:
- **FASE 0 — O Blueprint (O Contrato):**
  Definição estrita das entidades, campos, multi-tenant (`workspace_id`), papéis (RBAC), rotas e telas antes de escrever código.
- **FASE 1 — Esqueleto que Sobe:**
  Backend com `/api/health`, frontend renderizando, Dockerfile e variáveis de ambiente. **Tem que subir e responder antes de qualquer feature.**
- **FASE 2 — Auth + Multi-tenant Primeiro:**
  Registro, login com JWT + bcrypt, escopo de workspace em todas as queries e proteção de rotas por RBAC.
- **FASE 3..N — Fatias Verticais de Negócio:**
  Uma funcionalidade por vez, testada de verdade, com persistência real no banco de dados.

---

## 3. AS 4 JANELAS DE AUDITORIA DO TECH LEAD (ANTIGRAVITY)

O Tech Lead nunca aceita promessas verbais dos executores. Ele valida nas 4 janelas:
1. **LINEAR (MCP / API):** Lê os comentários do executor no ticket e verifica critérios de aceite.
2. **DISCO (Worktree Local):** Examina o código-fonte alterado e o `git show <commit>`.
3. **GITHUB (`gh pr view`):** Confere o diff do PR, integridade de commits e checks de CI.
4. **PRODUÇÃO / TESTE REAL:** Executa o endpoint ou script de teste e confere a persistência real.

---

## 4. O CANAL DE DÚVIDAS & DESBLOQUEIO IMEDIATO

Quando um executor no Orca encontrar uma ambiguidade, dependência ou bloqueio:
1. **No Linear:** Ele adiciona um comentário detalhado no ticket descrevendo a dúvida.
2. **No Disco:** Ele cria um arquivo `.orchestrator-question` na raiz da sua worktree com o texto exato da dúvida.
3. **O Antigravity (Orquestrador):**
   - Detecta o arquivo via `orchestrator_monitor.py` ou leitura direta.
   - Responde à dúvida no ticket do Linear com a decisão técnica.
   - Remove o arquivo `.orchestrator-question` para liberar a thread de execução do executor.

---

## 5. REGRAS DE QUALIDADE & HONESTIDADE

- **Evidência Obrigatória:** Toda conclusão de tarefa deve vir acompanhada da evidência de teste (output do comando, status HTTP 200, registro salvo no banco).
- **Sem Telas Casca:** Todo botão deve chamar um endpoint existente. Todo endpoint deve persistir ou ler dados reais. Toda tela deve tratar estados de carregamento, lista vazia e erro.
- **Modo Mock Primeiro:** Toda integração externa (pagamentos, e-mails, IA externa) deve nascer com um adaptador e modo MOCK para testes sem depender de credenciais externas.
- **Deploy Somente com Aprovação:** Nenhum agente tem permissão para fazer deploy direto em produção sem o aval explícito do dono humano.
