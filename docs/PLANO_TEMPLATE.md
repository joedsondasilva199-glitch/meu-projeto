# PLANO DE DESENVOLVIMENTO: FATIAS VERTICAIS (PLANO.md)

Este documento é a fonte da verdade sobre o que construir, organizado em fases sequenciais.
Nenhuma fase é iniciada sem que a anterior esteja 100% testada e aprovada pelo Tech Lead.

---

## FASE 0 — BLUEPRINT & CONTRATO ARQUITETURAL
- [ ] **Nome do Projeto & Descrição:** O que o app resolve e seu valor único.
- [ ] **Multi-tenant:** Definição da chave `workspace_id` em todas as tabelas/coleções.
- [ ] **Entidades Principais:**
  - `User`: id, email, password_hash, role, workspace_id, created_at
  - `Workspace`: id, name, slug, owner_id, plan, created_at
  - `[Entidade_Core]`: campos específicos do domínio
- [ ] **Papéis (RBAC):** `owner`, `admin`, `editor`, `viewer`.
- [ ] **Matriz de Endpoints:** Métodos, rotas, corpos esperados e papéis exigidos.
- [ ] **Telas & Ações:** Lista de páginas e qual endpoint cada botão aciona.
- [ ] **Integrações Externas:** Mapeamento de adaptadores com modo MOCK.

---

## FASE 1 — ESQUELETO QUE SOBE & HEALTHCHECK
- [ ] Estrutura base de backend (ex: FastAPI ou Node.js) com rota `/api/health` retornando 200 OK.
- [ ] Estrutura base de frontend (ex: React + Tailwind + Vite) renderizando tela inicial conectada à API.
- [ ] Configuração de Dockerfile / docker-compose e `.env.example`.
- [ ] **Critério de Pronto:** O projeto sobe com um único comando e responde healthcheck.

---

## FASE 2 — AUTENTICAÇÃO + MULTI-TENANT
- [ ] Registro de usuário com criação de workspace inicial.
- [ ] Login com geração de JWT e hashing de senhas seguro (bcrypt).
- [ ] Middleware de autenticação e injeção do contexto de workspace em toda requisição.
- [ ] Rotas protegidas por permissão (RBAC).
- [ ] **Critério de Pronto:** Teste real de login, emissão de token e rejeição de token inválido.

---

## FASE 3..N — FATIAS VERTICAIS FUNCIONAIS
*(Para cada fatia de negócio: Banco ➔ Endpoints ➔ Tela ➔ Teste Real)*

### FASE 3: [Nome da Primeira Funcionalidade Core]
- [ ] Modelo no banco com `workspace_id`.
- [ ] Endpoints de CRUD com validação de payload e RBAC.
- [ ] Telas com loading, erro e listagem conectada ao backend.
- [ ] Botão que dispara a ação e persiste no banco de dados.
- [ ] **Critério de Pronto:** Registro criado pela interface visível e persistido no banco.

### FASE 4: [Próxima Funcionalidade]
- [ ] ...
