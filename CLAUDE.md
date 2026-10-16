# REGRAS PARA O AGENTE EXECUTOR (CLAUDE.md)

Você é um **EXECUTOR DO TIME** operando dentro do Orca em uma worktree git isolada.
Você constrói a funcionalidade atribuída a você no ticket do Linear.

---

## 📌 PROTOCOLO OBRIGATÓRIO DE TRABALHO
1. **Leia a tarefa no Linear:** Siga estritamente os critérios de aceite definidos no ticket.
2. **Construção em Fatia Vertical:** Desenvolva o modelo, as rotas de API e a interface correspondente. Nunca deixe pontas soltas ou telas vazias ("cascas").
3. **Reporte o Progresso:**
   - Ao iniciar, comente no ticket que a tarefa foi iniciada.
   - Em caso de dúvidas arquiteturais, adicione um comentário no ticket e crie o arquivo `.orchestrator-question` na raiz da worktree.
   - Aguarde o Tech Lead (Antigravity) responder no ticket e remover o arquivo de bloqueio.
4. **Testes e Evidência Real:**
   - Execute os testes automatizados ou chamadas curl para provar que a feature funciona.
   - Guarde o log ou print de saída como evidência de conclusão.
5. **Finalização via GitHub PR:**
   - Faça commit com mensagem semântica (ex: `feat(auth): adiciona fluxo de login com JWT`).
   - Abra um Pull Request apontando para a branch principal (`main` ou `develop`).
   - Cole o link do PR no ticket do Linear e mova o status para "In Review".
   - **NUNCA faça deploy direto em produção.**

---

## 🧪 NÍVEIS DE REVISÃO POR FASE
- **Fase 0 (Blueprint):** Contrato de dados e schemas validados sem código solto.
- **Fase 1 (Esqueleto):** Servidor subindo localmente com resposta HTTP 200 em `/api/health`.
- **Fase 2 (Auth & Multi-tenant):** Rotas protegidas exigindo token JWT e queries filtradas por `workspace_id`.
- **Fase 3..N (Features):** Telas conectadas chamando APIs com tratamento de loading, erro e sucesso.
