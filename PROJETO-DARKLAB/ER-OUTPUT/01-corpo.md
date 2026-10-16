# RELATÓRIO DA FASE 1 — CLONAR O CORPO (ER-BLACK)

## 1. IDENTIFICAÇÃO DO CLIENTE E ARTEFATOS

- **Tipo de Cliente:** Web SPA (Single Page Application) em React 19 / Vite.
- **Linguagem:** JavaScript (ESNext / Bundled), HTML5, CSS3.
- **Origem dos Artefatos:** Extraídos da aplicação DarkLab Studio em `D:\DarkLab AI\`.
- **Integridade Prévia (Original):**
  - Arquivo: `bundle_darklab.js`
  - Tamanho: 698.370 bytes
  - SHA256: `5154AA1450466FA5422AF5A25306CB12A3166E30B98137C6BE50C8FA27A1C357` (registrado em `ER-OUTPUT\00-hashes.txt`).

---

## 2. ESTRUTURA EXTRAÍDA (`ER-OUTPUT\front-clonado\`)

```
ER-OUTPUT\front-clonado\
  ├── assets/                 # SVGs, ícones e assets estáticos
  ├── brand/                  # Logos e identidade visual da aplicação
  ├── studio-preview/         # Previews dos módulos de estúdio
  ├── app.js                  # Lógica de controle de rotas da aplicação
  ├── bundle_darklab.js       # Bundle core minificado e desempacotado
  ├── darklab_app.css         # Folhas de estilo da UI
  ├── darklab_engine.js       # Motor interativo com bind nas ferramentas
  ├── darklab_original.css    # Estilos originais completos extraídos
  ├── dashboard.css           # Estilos do painel de controle operacional
  ├── dashboard.js            # Lógica do painel Kanban, balanço e ferramentas
  ├── index.html              # Interface do Dashboard operacional
  └── landing.html            # Interface da Landing Page oficial completa
```

---

## 3. CENTRALIZAÇÃO DE API_BASE_URL (PREPARAÇÃO FASE 5)

A constante de conexão com a API foi centralizada para permitir chaveamento dinâmico sem quebrar as rotas internas:

1. **Em `bundle_darklab.js`:**
   - Original: `const $t="https://api.darklabapp.com";`
   - Reconfigurado: `const API_BASE_URL=window.API_BASE_URL||"";const $t=API_BASE_URL;`
2. **Em `darklab_engine.js`:**
   - Inserido topo: `const API_BASE_URL = window.API_BASE_URL || "";`
   - Chamadas de fetch parametrizadas para: `API_BASE_URL + "/api/..."`
3. **Em `dashboard.js`:**
   - Inserido topo: `const API_BASE_URL = window.API_BASE_URL || "";`
   - Chamadas de fetch parametrizadas para: `API_BASE_URL + "/api/..."`

---

## 4. SMOKE TEST EXECUTADO (PROVA REAL)

O cliente foi servido a partir do código fonte em `http://127.0.0.1:8091` e submetido a requisições de integridade:

- **PEDIDO:** `GET http://127.0.0.1:8091/`
  - **RESPOSTA:** `HTTP 200 OK`, `Content-Length: 43890` (HTML do Dashboard renderizado)
- **PEDIDO:** `GET http://127.0.0.1:8091/landing.html`
  - **RESPOSTA:** `HTTP 200 OK`, `Content-Length: 126102` (Landing Page renderizada)
- **PEDIDO:** `GET http://127.0.0.1:8091/bundle_darklab.js`
  - **RESPOSTA:** `HTTP 200 OK`, `Content-Length: 699109` (Bundle com API_BASE_URL centralizada)

---

## 5. GATE DE SEGURANÇA (FASE 1)

- [x] sha256 do cliente original salvo antes de qualquer escrita (`ER-OUTPUT\00-hashes.txt`)
- [x] nenhum caminho absoluto nem credencial no código reescrito
- [x] nenhuma LACUNA aberta sem justificativa
- [x] cliente extraído e fonte acessível em `ER-OUTPUT\front-clonado\`
- [x] API_BASE_URL centralizada em um local único
- [x] smoke test do front executado com sucesso e evidenciado

Confirmação: **FASE 1 OK. Cliente Web/PWA extraído e rebrandado em front-clonado\.**
