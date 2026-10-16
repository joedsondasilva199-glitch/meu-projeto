const API_BASE_URL = window.API_BASE_URL || "";
// DarkLAB AI Studio - Motor Interativo 100% Fiel
// Conexão direta com a API FastAPI (http://127.0.0.1:8050)

let currentToken = null;
let currentScriptId = null;
let studioIsPlaying = false;
let studioInterval = null;
let studioTime = 0;

// Inicialização Geral
document.addEventListener("DOMContentLoaded", async () => {
  setupNavbarInteractions();
  setupFAQAccordion();
  setupHeroTabs();
  setupStudioInteractions();
  setupToolModal();
  await ensureAuthentication();
  await syncTokenBalance();
  interceptToolLinks();
});

// 1. AUTENTICAÇÃO TRANSPARENTE
async function ensureAuthentication() {
  const saved = localStorage.getItem("darklab_token");
  if (saved) {
    currentToken = saved;
    return;
  }
  try {
    const regRes = await fetch(API_BASE_URL + "/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Diretor DarkLAB",
        email: "diretor@darklabapp.com",
        password: "DarkLabPassword2026!",
        workspace_name: "Estúdio DarkLAB Principal",
        plan_tier: "plus"
      })
    });
    if (regRes.ok) {
      const data = await regRes.json();
      currentToken = data.access_token;
      localStorage.setItem("darklab_token", currentToken);
      return;
    }
    const loginRes = await fetch(API_BASE_URL + "/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "diretor@darklabapp.com", password: "DarkLabPassword2026!" })
    });
    if (loginRes.ok) {
      const data = await loginRes.json();
      currentToken = data.access_token;
      localStorage.setItem("darklab_token", currentToken);
    }
  } catch (err) {
    console.error("Falha na autenticação:", err);
  }
}

// 2. SINCRONIZAÇÃO DE SALDO DE TOKENS
async function syncTokenBalance() {
  if (!currentToken) return;
  try {
    const res = await fetch(API_BASE_URL + "/api/tokens/balance", {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (res.ok) {
      const data = await res.json();
      const valEl = document.getElementById("nav-tokens-val");
      if (valEl) {
        valEl.innerText = data.total_balance.toLocaleString("pt-BR");
      }
    }
  } catch (e) {
    console.warn("Erro ao sincronizar tokens:", e);
  }
}

// 3. MEGA MENU & DRAWER MOBILE
function setupNavbarInteractions() {
  const toolsBtn = document.querySelector('button[aria-controls="ds-tools-menu"]');
  const megaMenu = document.getElementById("ds-tools-menu");
  const scrim = document.querySelector(".ds-mega-scrim");
  const burgerBtn = document.querySelector(".ds-burger");
  const drawer = document.querySelector(".ds-drawer");

  if (toolsBtn && megaMenu) {
    toolsBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = megaMenu.classList.toggle("is-open");
      toolsBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
      if (scrim) scrim.classList.toggle("is-open", isOpen);
    });
  }

  if (scrim) {
    scrim.addEventListener("click", () => {
      if (megaMenu) megaMenu.classList.remove("is-open");
      if (drawer) drawer.classList.remove("is-open");
      if (scrim) scrim.classList.remove("is-open");
      if (toolsBtn) toolsBtn.setAttribute("aria-expanded", "false");
    });
  }

  if (burgerBtn && drawer) {
    burgerBtn.addEventListener("click", () => {
      const isDrawerOpen = drawer.classList.toggle("is-open");
      burgerBtn.setAttribute("aria-expanded", isDrawerOpen ? "true" : "false");
      if (scrim) scrim.classList.toggle("is-open", isDrawerOpen);
    });
  }

  // Injeta Badge de Tokens na Barra de Ações se ainda não existir
  const actions = document.querySelector(".ds-header__actions");
  if (actions && !document.querySelector(".ds-token-badge")) {
    const badge = document.createElement("div");
    badge.className = "ds-token-badge";
    badge.innerHTML = `<span class="ds-pulse"></span> <span id="nav-tokens-val">250.000</span> tokens · <small>Plus</small>`;
    badge.onclick = () => openToolModal("tokens");
    actions.insertBefore(badge, actions.firstChild);
  }
}

// 4. FAQ ACCORDION
function setupFAQAccordion() {
  const faqItems = document.querySelectorAll(".ds-faq__item");
  faqItems.forEach(item => {
    const btn = item.querySelector(".ds-faq__q");
    if (btn) {
      btn.addEventListener("click", () => {
        const isOpen = item.classList.contains("is-open");
        faqItems.forEach(i => i.classList.remove("is-open"));
        if (!isOpen) item.classList.add("is-open");
      });
    }
  });
}

// 5. HERO NICHE FINDER DEMO
function setupHeroTabs() {
  const tabs = document.querySelectorAll(".dm-nf .dm-tabs span");
  tabs.forEach(tab => {
    tab.addEventListener("click", async () => {
      tabs.forEach(t => t.classList.remove("is-on"));
      tab.classList.add("is-on");

      const txt = tab.innerText.toLowerCase();
      let mode = "exploding";
      if (txt.includes("subindo")) mode = "rising";
      else if (txt.includes("novos")) mode = "new";

      await fetchAndUpdateHeroChannels(mode);
    });
  });

  // Torna as linhas do Niche Finder clicáveis para abrir o raio-X
  const rows = document.querySelectorAll(".dm-nf__row");
  rows.forEach(r => {
    r.style.cursor = "pointer";
    r.addEventListener("click", () => {
      const name = r.querySelector("b") ? r.querySelector("b").innerText : "Arquivos Perdidos";
      openToolModal("niche-finder", { channel: name });
    });
  });
}

async function fetchAndUpdateHeroChannels(tab) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/viral-lab/niche-finder?tab=${tab}`, {
      headers: currentToken ? { "Authorization": `Bearer ${currentToken}` } : {}
    });
    if (res.ok) {
      const channels = await res.json();
      const container = document.querySelector(".dm-nf__rows");
      if (!container) return;

      container.innerHTML = channels.slice(0, 4).map((c, i) => `
        <div class="dm-nf__row ${i === 0 ? 'is-top' : ''}" style="--i:${i}; cursor:pointer;" onclick="openToolModal('niche-finder', {channel: '${c.title}'})">
          <span class="dm-nf__ch">
            <span class="dm-avatar" style="width:30px;height:30px;background:linear-gradient(135deg, hsl(${200 + i*30} 80% 62%), hsl(${240 + i*30} 70% 38%))">${c.title.substring(0,2).toUpperCase()}</span>
            <span><b>${c.title}</b><small>${c.niche} ${c.is_monetized ? '<em class=\"dm-money\">$ Monetizado</em>' : ''}</small></span>
          </span>
          <span class="dm-mono dm-dim">${c.age_days} dias</span>
          <span class="dm-mono">${c.views.toLocaleString('pt-BR')}</span>
          <span class="dm-hide-s">
            <svg class="dm-spark" width="78" height="24" viewBox="0 0 78 24">
              <path d="M3 17 Q 25 14 45 10 T 75 3" stroke="#10b981" stroke-width="2" fill="none"></path>
            </svg>
          </span>
          <span class="dm-outlier">×${c.outlier_score}</span>
        </div>
      `).join("");
    }
  } catch (err) {
    console.warn("Erro ao atualizar canais:", err);
  }
}

// 6. HERO STUDIO INTERACTIVE SIMULATOR (APP WINDOWS)
function setupStudioInteractions() {
  const dockItems = document.querySelectorAll(".dm-ss__dock span");
  dockItems.forEach(item => {
    item.addEventListener("click", () => {
      dockItems.forEach(d => d.classList.remove("is-on"));
      item.classList.add("is-on");
      const name = item.querySelector("small") ? item.querySelector("small").innerText : "Studio";
      console.log("Studio modo selecionado:", name);
    });
  });

  // Monitor Playhead & Legenda Interativa
  const monitor = document.querySelector(".dm-ss__monitor");
  if (monitor) {
    monitor.style.cursor = "pointer";
    monitor.title = "Clique para dar Play / Pause";
    monitor.addEventListener("click", toggleStudioPlayback);
  }

  // Botão Exportar do Studio
  const exportBtn = document.querySelector(".dm-ss__export");
  if (exportBtn) {
    exportBtn.style.cursor = "pointer";
    exportBtn.addEventListener("click", () => {
      runStudioExportSimulation();
    });
  }

  // Chat do Agente no Studio
  const agentBox = document.querySelector(".dm-ss__agent");
  if (agentBox) {
    agentBox.style.cursor = "pointer";
    agentBox.addEventListener("click", () => {
      openToolModal("studio-agents");
    });
  }
}

function toggleStudioPlayback() {
  studioIsPlaying = !studioIsPlaying;
  const tc = document.querySelector(".dm-ss__tc");
  const caption = document.querySelector(".dm-ss__caption");
  const playhead = document.querySelector(".dm-ss__playhead");
  const captions = [
    "uma porta trancada por dentro",
    "passos ecoando no corredor escuro",
    "a gravação em fita cassete de 1943",
    "ninguém sobreviveu para contar",
    "o diário secreto finalmente foi revelado"
  ];

  if (studioIsPlaying) {
    if (caption) caption.style.color = "#ec4899";
    studioInterval = setInterval(() => {
      studioTime++;
      const mins = Math.floor(studioTime / 60);
      const secs = studioTime % 60;
      if (tc) tc.innerText = `00:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
      if (caption) caption.innerText = captions[studioTime % captions.length];
      if (playhead) {
        const pct = (studioTime % 30) / 30 * 100;
        playhead.style.left = `${pct}%`;
      }
    }, 1000);
  } else {
    clearInterval(studioInterval);
    if (caption) caption.style.color = "#fff";
  }
}

function runStudioExportSimulation() {
  const exportBtn = document.querySelector(".dm-ss__export");
  if (!exportBtn) return;

  exportBtn.innerHTML = `<span>⏳ Exportando (FFmpeg 4K 60fps)...</span>`;
  let prog = 0;
  const pInterval = setInterval(() => {
    prog += 25;
    if (prog <= 100) {
      exportBtn.innerHTML = `<span>⚡ GPU Local ${prog}%</span>`;
    } else {
      clearInterval(pInterval);
      exportBtn.innerHTML = `<span style="color:#10b981;">✓ Vídeo Renderizado!</span>`;
      setTimeout(() => {
        exportBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg><b>Exportar</b>`;
      }, 3000);
    }
  }, 400);
}

// 7. INTERCEPTADOR DE TODAS AS 16 FERRAMENTAS
function interceptToolLinks() {
  document.querySelectorAll('a[href^="/ferramentas/"]').forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const href = link.getAttribute("href");
      const toolSlug = href.replace("/ferramentas/", "").replace(/\/$/, "");
      openToolModal(toolSlug);
    });
  });
}

// 8. MODAL INTERATIVO COMPLETO PARA TODAS AS FERRAMENTAS
function setupToolModal() {
  if (document.getElementById("darklab-tool-modal")) return;

  const modalHtml = `
    <div id="darklab-tool-modal" class="dl-modal-overlay">
      <div class="dl-modal-dialog">
        <div class="dl-modal-head">
          <div class="dl-modal-title" id="dl-modal-header-title">
            <span>DarkLAB Studio AI</span>
          </div>
          <button class="dl-modal-close" onclick="closeToolModal()" aria-label="Fechar">&times;</button>
        </div>
        <div class="dl-modal-body" id="dl-modal-content">
          <!-- Conteúdo Dinâmico da Ferramenta -->
        </div>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML("beforeend", modalHtml);
}

function closeToolModal() {
  const modal = document.getElementById("darklab-tool-modal");
  if (modal) modal.classList.remove("is-active");
}

function openToolModal(toolSlug, context = {}) {
  const modal = document.getElementById("darklab-tool-modal");
  const title = document.getElementById("dl-modal-header-title");
  const body = document.getElementById("dl-modal-content");
  if (!modal || !title || !body) return;

  body.innerHTML = `<div style="text-align:center; padding:3rem; color:#9ca3af;">Carregando ferramenta...</div>`;
  modal.classList.add("is-active");

  switch (toolSlug) {
    case "niche-finder":
      renderNicheFinderTool(body, title, context);
      break;
    case "analisar-video":
      renderAnalyzeVideoTool(body, title, context);
      break;
    case "analisar-canal":
      renderAnalyzeChannelTool(body, title, context);
      break;
    case "expansao-de-nicho":
      renderNicheExpansionTool(body, title, context);
      break;
    case "extensao-youtube":
      renderExtensionSimulatorTool(body, title, context);
      break;
    case "roteiros":
      renderScriptwriterTool(body, title, context);
      break;
    case "narracao":
      renderVoiceTTSTool(body, title, context);
      break;
    case "transcricao":
      renderTranscriptionTool(body, title, context);
      break;
    case "automacoes":
      renderAutomationsTool(body, title, context);
      break;
    case "personagens":
      renderCharactersTool(body, title, context);
      break;
    case "gerar-srt":
      renderSRTTool(body, title, context);
      break;
    case "templates":
      renderTemplatesTool(body, title, context);
      break;
    case "mcp":
      renderMCPTool(body, title, context);
      break;
    case "meus-canais":
      renderMyChannelsTool(body, title, context);
      break;
    case "pipeline":
      renderPipelineKanbanTool(body, title, context);
      break;
    case "biblioteca":
      renderMediaLibraryTool(body, title, context);
      break;
    case "darklab-studio":
    case "studio-agents":
      renderDesktopStudioTool(body, title, context);
      break;
    case "tokens":
      renderTokensWalletTool(body, title, context);
      break;
    default:
      renderGenericTool(body, title, toolSlug);
      break;
  }
}

// --- RENDERIZADORES DAS FERRAMENTAS ---

// 1. NICHE FINDER
async function renderNicheFinderTool(container, titleEl, ctx) {
  titleEl.innerHTML = `<span>📡 Niche Finder — Radar de Outliers Dark</span>`;
  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem;">
      <div style="display:flex; gap:8px;">
        <button class="dl-btn dl-btn-secondary" onclick="loadModalNicheTable('exploding')">🔥 Explodindo agora</button>
        <button class="dl-btn dl-btn-secondary" onclick="loadModalNicheTable('rising')">📈 Subindo rápido</button>
        <button class="dl-btn dl-btn-secondary" onclick="loadModalNicheTable('new')">✨ Canais novos</button>
      </div>
      <input type="text" id="modal-niche-search" class="dl-input" style="width:240px;" placeholder="Filtrar por nicho..." onkeyup="filterNicheRows()">
    </div>
    <div style="overflow-x:auto;">
      <table style="width:100%; border-collapse:collapse;" id="modal-niche-table">
        <thead>
          <tr style="border-bottom:1px solid #28243d; color:#9ca3af; text-align:left; font-size:0.8rem;">
            <th style="padding:10px;">CANAL</th>
            <th>NICHO</th>
            <th>INSCRITOS</th>
            <th>VIEWS</th>
            <th>IDADE</th>
            <th>OUTLIER</th>
            <th>AÇÃO</th>
          </tr>
        </thead>
        <tbody id="modal-niche-tbody">
          <tr><td colspan="7" style="padding:20px; text-align:center;">Consultando radar...</td></tr>
        </tbody>
      </table>
    </div>
  `;
  await loadModalNicheTable("exploding");
}

async function loadModalNicheTable(tab) {
  const tbody = document.getElementById("modal-niche-tbody");
  if (!tbody) return;
  tbody.innerHTML = `<tr><td colspan="7" style="padding:20px; text-align:center;">Varrendo canais dark em tempo real...</td></tr>`;
  try {
    const res = await fetch(`${API_BASE_URL}/api/viral-lab/niche-finder?tab=${tab}`, {
      headers: currentToken ? { "Authorization": `Bearer ${currentToken}` } : {}
    });
    const channels = await res.json();
    tbody.innerHTML = channels.map(c => `
      <tr style="border-bottom:1px solid rgba(255,255,255,0.05); font-size:0.9rem;">
        <td style="padding:12px;"><strong>${c.title}</strong></td>
        <td>${c.niche}</td>
        <td style="font-family:'JetBrains Mono';">${c.subscribers.toLocaleString('pt-BR')}</td>
        <td style="font-family:'JetBrains Mono';">${c.views.toLocaleString('pt-BR')}</td>
        <td>${c.age_days} dias</td>
        <td><span style="background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3); padding:2px 8px; border-radius:4px; font-weight:700;">×${c.outlier_score}</span></td>
        <td><button class="dl-btn" style="padding:4px 10px; font-size:0.75rem;" onclick="openToolModal('roteiros', {title: '${c.title}', niche: '${c.niche}'})">Criar Roteiro</button></td>
      </tr>
    `).join("");
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="7" style="color:red; text-align:center;">Erro ao carregar radar.</td></tr>`;
  }
}

// 2. ANALISAR VÍDEO
function renderAnalyzeVideoTool(container, titleEl) {
  titleEl.innerHTML = `<span>🔍 Analisar Vídeo — Raio-X de Retenção do YouTube</span>`;
  container.innerHTML = `
    <div class="dl-field">
      <label class="dl-label">URL ou ID do Vídeo do YouTube:</label>
      <div style="display:flex; gap:10px;">
        <input type="text" id="modal-video-url" class="dl-input" value="https://youtube.com/watch?v=3OVnEqc-eqY">
        <button class="dl-btn" onclick="executeVideoAnalysis()">Executar Raio-X</button>
      </div>
    </div>
    <div id="modal-video-result" style="display:none;" class="dl-result-card"></div>
  `;
}

async function executeVideoAnalysis() {
  const url = document.getElementById("modal-video-url").value;
  const out = document.getElementById("modal-video-result");
  out.style.display = "block";
  out.innerHTML = "Processando retenção, gancho e transcrição com IA...";

  try {
    const res = await fetch(API_BASE_URL + "/api/viral-lab/analyze-video", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${currentToken}` },
      body: JSON.stringify({ url_or_id: url })
    });
    const d = await res.json();
    out.innerHTML = `
      <h3 style="color:#a78bfa; margin-bottom:10px;">${d.title}</h3>
      <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; margin-bottom:15px;">
        <div style="background:#1b1730; padding:10px; border-radius:8px;"><small style="color:#9ca3af;">Views</small><br><strong>${d.views.toLocaleString('pt-BR')}</strong></div>
        <div style="background:#1b1730; padding:10px; border-radius:8px;"><small style="color:#9ca3af;">VPH (Views/Hora)</small><br><strong>${d.estimated_vph}</strong></div>
        <div style="background:#1b1730; padding:10px; border-radius:8px;"><small style="color:#9ca3af;">Retenção Estimada</small><br><strong style="color:#10b981;">${d.retention_score}%</strong></div>
        <div style="background:#1b1730; padding:10px; border-radius:8px;"><small style="color:#9ca3af;">Monetizado</small><br><strong style="color:#f59e0b;">${d.is_monetized ? '$ Sim' : 'Não'}</strong></div>
      </div>
      <p><strong>Força do Gancho (0 a 30s):</strong> ${d.hook_strength}</p>
      <p style="margin-top:6px;"><strong>Tags Estratégicas:</strong> ${d.tags.join(", ")}</p>
      <div class="dl-pre" style="margin-top:12px;">${d.summary}</div>
      <div style="margin-top:15px;">
        <button class="dl-btn" onclick="openToolModal('roteiros', {title: '${d.title}'})">Clonar Estrutura no Roteirizador</button>
      </div>
    `;
  } catch (e) {
    out.innerText = "Erro ao analisar vídeo.";
  }
}

// 3. ROTEIRIZADOR POV (RETENÇÃO)
function renderScriptwriterTool(container, titleEl, ctx = {}) {
  titleEl.innerHTML = `<span>✍️ Roteiros com IA — Retenção POV & Ganchos de 30s</span>`;
  const defaultTitle = ctx.title ? `A Verdade Sobre ${ctx.title}` : "Eles Riram Quando Limpei o Chão — Até Abrir a 2ª Pasta Lacrada";
  const defaultNiche = ctx.niche || "Mistério & Sobrenatural";

  container.innerHTML = `
    <div class="dl-field">
      <label class="dl-label">Título Estrutural do Vídeo:</label>
      <input type="text" id="m-script-title" class="dl-input" value="${defaultTitle}">
    </div>
    <div class="dl-tool-grid">
      <div class="dl-field">
        <label class="dl-label">Nicho:</label>
        <input type="text" id="m-script-niche" class="dl-input" value="${defaultNiche}">
      </div>
      <div class="dl-field">
        <label class="dl-label">Fórmula de Retenção:</label>
        <select id="m-script-formula" class="dl-select">
          <option value="pov_conflito">Fórmula 1: 100% POV (1ª Pessoa) + Conflito nos 30s</option>
          <option value="rejeicao_reconhecimento">Fórmula 2: Rejeição ➔ Reconhecimento Público</option>
          <option value="tribunal_testamento">Fórmula 3: Tribunal / Segredo de Família</option>
        </select>
      </div>
    </div>
    <div class="dl-field">
      <label class="dl-label">Premissa Dramática:</label>
      <textarea id="m-script-topic" class="dl-textarea" rows="3">Um funcionário humilhado descobre que a antiga propriedade esconde uma fortuna e documentos confidenciais.</textarea>
    </div>
    <button class="dl-btn" onclick="executeScriptGeneration()">Gerar Roteiro em Lote</button>
    <div id="m-script-result" style="display:none;" class="dl-result-card"></div>
  `;
}

async function executeScriptGeneration() {
  const title = document.getElementById("m-script-title").value;
  const niche = document.getElementById("m-script-niche").value;
  const formula = document.getElementById("m-script-formula").value;
  const topic = document.getElementById("m-script-topic").value;
  const out = document.getElementById("m-script-result");

  out.style.display = "block";
  out.innerHTML = "Engenhando blocos de retenção (Hook ➔ Loop Aberto ➔ POV ➔ CTA)...";

  try {
    const res = await fetch(API_BASE_URL + "/api/scripts/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${currentToken}` },
      body: JSON.stringify({ title, niche, topic_description: topic, formula_style: formula })
    });
    const s = await res.json();
    currentScriptId = s.id;
    out.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <span style="color:#10b981; font-weight:bold;">✓ Roteiro Gerado com Sucesso!</span>
        <span style="color:#a78bfa; font-family:'JetBrains Mono';">${s.character_count} Caracteres (~${s.estimated_audio_tokens} Tokens)</span>
      </div>
      <div class="dl-pre">${s.full_script}</div>
      <div style="margin-top:15px; display:flex; gap:10px;">
        <button class="dl-btn" onclick="openToolModal('narracao', {script_id: '${s.id}'})">🎙️ Narrar com IA</button>
        <button class="dl-btn dl-btn-secondary" onclick="openToolModal('automacoes', {script_id: '${s.id}'})">🎬 Criar Cenas (Storyboard)</button>
        <button class="dl-btn dl-btn-secondary" onclick="openToolModal('pipeline', {script_id: '${s.id}', title: '${s.title}'})">📋 Enviar ao Kanban</button>
      </div>
    `;
  } catch (e) {
    out.innerText = "Erro ao gerar roteiro.";
  }
}

// 4. NARRAÇÃO COM IA (TTS)
function renderVoiceTTSTool(container, titleEl, ctx = {}) {
  titleEl.innerHTML = `<span>🎙️ Narração com IA — Síntese Neural por Tokens</span>`;
  container.innerHTML = `
    <div style="background:#161327; padding:12px; border-radius:8px; margin-bottom:1.25rem;">
      <small style="color:#9ca3af;">Economia de Voz DarkLAB:</small> <strong>1 Token = 1 Caractere narrado</strong> (~1.000 tokens/minuto de áudio).
    </div>
    <div class="dl-field">
      <label class="dl-label">Selecione a Voz Neural:</label>
      <select id="m-voice-select" class="dl-select">
        <option value="Marcus (Tensão/Mistério)">Marcus — Grave, Misterioso & Solene (Ideal para Canais Dark)</option>
        <option value="Valéria (Documentário Sombrio)">Valéria — Séria, Investigativa e Precisa</option>
        <option value="Erick (História Épica)">Erick — Enérgico, Dramático para Relatos Históricos</option>
      </select>
    </div>
    <div class="dl-field">
      <label class="dl-label">ID do Roteiro Ativo:</label>
      <input type="text" id="m-voice-script-id" class="dl-input" value="${ctx.script_id || currentScriptId || ''}" placeholder="Gere um roteiro antes ou insira o ID...">
    </div>
    <button class="dl-btn" onclick="executeVoiceSynthesis()">Sintetizar Narração & Debitar Tokens</button>
    <div id="m-voice-result" style="display:none;" class="dl-result-card"></div>
  `;
}

async function executeVoiceSynthesis() {
  const sid = document.getElementById("m-voice-script-id").value;
  const voice = document.getElementById("m-voice-select").value;
  const out = document.getElementById("m-voice-result");

  if (!sid) {
    alert("Por favor, selecione ou crie um roteiro antes.");
    return;
  }
  out.style.display = "block";
  out.innerHTML = "Sintetizando áudio neural e debitando caracteres da carteira...";

  try {
    const res = await fetch(API_BASE_URL + "/api/tts/generate-voice", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${currentToken}` },
      body: JSON.stringify({ script_id: sid, voice_name: voice })
    });
    if (res.ok) {
      const v = await res.json();
      await syncTokenBalance();
      out.innerHTML = `
        <div style="color:#10b981; font-weight:bold; margin-bottom:8px;">✓ Áudio Sintetizado com Sucesso!</div>
        <p>Voz: <strong>${v.voice_name}</strong> | Tokens Debitados: <strong style="color:#ec4899;">${v.tokens_debited}</strong> | Duração: <strong>${v.duration_seconds}s</strong></p>
        <div style="margin:12px 0;">
          <audio controls autoplay style="width:100%;">
            <source src="${v.audio_url}" type="audio/wav">
          </audio>
        </div>
        <div style="display:flex; gap:10px; margin-top:15px;">
          <button class="dl-btn" onclick="openToolModal('automacoes', {script_id: '${sid}'})">🎬 Quebrar em Cenas Visuais</button>
          <button class="dl-btn dl-btn-secondary" onclick="openToolModal('gerar-srt', {script_id: '${sid}'})">📄 Gerar SRT</button>
        </div>
      `;
    } else {
      const err = await res.json();
      out.innerHTML = `<span style="color:#ef4444;">${err.detail || 'Falha na narração'}</span>`;
    }
  } catch (e) {
    out.innerText = "Erro ao sintetizar voz.";
  }
}

// 5. AUTOMAÇÕES EM LOTE (STORYBOARD)
function renderAutomationsTool(container, titleEl, ctx = {}) {
  titleEl.innerHTML = `<span>🎬 Automações em Lote — Áudio ➔ Cenas com IA</span>`;
  container.innerHTML = `
    <div class="dl-field">
      <label class="dl-label">ID do Roteiro para Storyboard:</label>
      <input type="text" id="m-sb-script-id" class="dl-input" value="${ctx.script_id || currentScriptId || ''}">
    </div>
    <div class="dl-field">
      <label class="dl-label">Cadência de Cenas:</label>
      <select id="m-sb-seconds" class="dl-select">
        <option value="4">1 cena a cada 4 segundos (Ritmo Dinâmico Dark)</option>
        <option value="6">1 cena a cada 6 segundos (Documentário Clássico)</option>
        <option value="3">1 cena a cada 3 segundos (Shorts / Ultra Rápido)</option>
      </select>
    </div>
    <button class="dl-btn" onclick="executeStoryboardGeneration()">Gerar Todas as Cenas</button>
    <div id="m-sb-result" style="display:none; margin-top:1.25rem;"></div>
  `;
}

async function executeStoryboardGeneration() {
  const sid = document.getElementById("m-sb-script-id").value;
  const secs = parseInt(document.getElementById("m-sb-seconds").value);
  const out = document.getElementById("m-sb-result");

  if (!sid) {
    alert("Informe o ID do roteiro.");
    return;
  }
  out.style.display = "block";
  out.innerHTML = "Gerando tomadas e prompts cinematográficos...";

  try {
    const res = await fetch(API_BASE_URL + "/api/storyboard/auto-scenes", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${currentToken}` },
      body: JSON.stringify({ script_id: sid, seconds_per_scene: secs })
    });
    const sb = await res.json();
    out.innerHTML = `
      <div style="color:#10b981; font-weight:bold; margin-bottom:12px;">✓ ${sb.total_scenes} Cenas Geradas para a Timeline!</div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:12px; max-height:400px; overflow-y:auto;">
        ${sb.scenes.map(s => `
          <div style="background:#161327; border:1px solid #28243d; border-radius:8px; padding:10px;">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#8b5cf6; font-weight:bold;">
              <span>Cena #${s.scene_number}</span>
              <span>${s.start_time}s - ${s.end_time}s</span>
            </div>
            <div style="font-size:0.8rem; margin:6px 0;">"${s.narration_chunk}"</div>
            <div style="background:rgba(0,0,0,0.4); padding:6px; border-radius:4px; font-size:0.75rem; color:#9ca3af; font-family:'JetBrains Mono';">${s.visual_prompt}</div>
          </div>
        `).join("")}
      </div>
      <div style="margin-top:15px;">
        <button class="dl-btn" onclick="openToolModal('gerar-srt', {script_id: '${sid}'})">Baixar Legendas SRT</button>
      </div>
    `;
  } catch (e) {
    out.innerText = "Erro ao gerar storyboard.";
  }
}

// 6. GERAR SRT
async function renderSRTTool(container, titleEl, ctx = {}) {
  titleEl.innerHTML = `<span>📄 Gerador de Legendas SRT Sincronizadas</span>`;
  const sid = ctx.script_id || currentScriptId || "";
  container.innerHTML = `
    <div class="dl-field">
      <label class="dl-label">ID do Roteiro:</label>
      <input type="text" id="m-srt-id" class="dl-input" value="${sid}">
    </div>
    <button class="dl-btn" onclick="fetchSRTContent()">Gerar e Baixar SRT</button>
    <div id="m-srt-box" style="display:none; margin-top:1.25rem;">
      <pre class="dl-pre" id="m-srt-text"></pre>
      <a id="m-srt-dl-link" class="dl-btn" style="margin-top:12px; text-decoration:none;" download="legendas_darklab.srt">⬇️ Baixar Arquivo .SRT</a>
    </div>
  `;
  if (sid) fetchSRTContent();
}

async function fetchSRTContent() {
  const sid = document.getElementById("m-srt-id").value;
  const box = document.getElementById("m-srt-box");
  const pre = document.getElementById("m-srt-text");
  const dl = document.getElementById("m-srt-dl-link");

  try {
    const res = await fetch(`${API_BASE_URL}/api/storyboard/${sid}/srt`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (res.ok) {
      const d = await res.json();
      box.style.display = "block";
      pre.innerText = d.srt_content;
      const blob = new Blob([d.srt_content], { type: "text/plain" });
      dl.href = URL.createObjectURL(blob);
    } else {
      alert("Crie as cenas do roteiro primeiro na aba Automações.");
    }
  } catch (e) {
    console.error(e);
  }
}

// 7. PIPELINE KANBAN COMPLETO
async function renderPipelineKanbanTool(container, titleEl, ctx = {}) {
  titleEl.innerHTML = `<span>📋 Pipeline Kanban — Esteira de Produção de Vídeos</span>`;
  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
      <button class="dl-btn" onclick="createNewKanbanCardPrompt()">+ Novo Vídeo no Pipeline</button>
      <small style="color:#9ca3af;">Clique em um card para movê-lo de etapa.</small>
    </div>
    <div class="dl-kanban-row" id="m-kanban-board">
      <div style="grid-column:span 6; text-align:center; padding:30px;">Carregando esteira...</div>
    </div>
  `;
  await loadModalKanbanBoard();
}

async function loadModalKanbanBoard() {
  const boardEl = document.getElementById("m-kanban-board");
  if (!boardEl) return;
  try {
    const res = await fetch(API_BASE_URL + "/api/kanban/board", {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    const board = await res.json();
    const cols = [
      { id: "ideia", name: "💡 Ideia / Radar" },
      { id: "roteiro", name: "✍️ Roteiro" },
      { id: "narracao", name: "🎙️ Narração" },
      { id: "cenas", name: "🎬 Cenas" },
      { id: "edicao", name: "✂️ Edição" },
      { id: "concluido", name: "✅ Publicado" }
    ];

    boardEl.innerHTML = cols.map(c => `
      <div class="dl-kcol">
        <div class="dl-khead">${c.name}</div>
        <div style="display:flex; flex-direction:column; gap:8px;">
          ${(board[c.id] || []).map(card => `
            <div class="dl-kcard" onclick="advanceCardStage('${card.id}', '${card.column_status}')">
              <strong>${card.title}</strong>
              <div style="display:flex; justify-content:space-between; font-size:0.7rem; color:#9ca3af; margin-top:4px;">
                <span>#${card.id.substring(0,6)}</span>
                <span style="color:#8b5cf6;">Mover ➔</span>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `).join("");
  } catch (e) {
    boardEl.innerText = "Erro ao carregar kanban.";
  }
}

async function advanceCardStage(cardId, currentCol) {
  const sequence = ["ideia", "roteiro", "narracao", "cenas", "edicao", "concluido"];
  const currIdx = sequence.indexOf(currentCol);
  const nextCol = sequence[(currIdx + 1) % sequence.length];

  await fetch(`${API_BASE_URL}/api/kanban/cards/${cardId}/move`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${currentToken}` },
    body: JSON.stringify({ column_status: nextCol })
  });
  await loadModalKanbanBoard();
}

async function createNewKanbanCardPrompt() {
  const title = prompt("Título do novo vídeo dark:", "O Enigma do Vilarejo de 1943");
  if (!title) return;
  await fetch(API_BASE_URL + "/api/kanban/cards", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${currentToken}` },
    body: JSON.stringify({ title, column_status: "ideia" })
  });
  await loadModalKanbanBoard();
}

// 8. SERVIDOR MCP PARA CLAUDE & HERMES
async function renderMCPTool(container, titleEl) {
  titleEl.innerHTML = `<span>🔌 MCP Server — Integração com Claude, Hermes & Antigravity</span>`;
  container.innerHTML = `
    <p style="color:#9ca3af; margin-bottom:12px;">
      Servidor <strong>Model Context Protocol</strong> conectado à stack. Qualquer IA externa pode invocar a DarkLAB via chat.
    </p>
    <div class="dl-field">
      <label class="dl-label">Ferramentas Registradas no MCP:</label>
      <div id="mcp-tools-list" class="dl-pre">Consultando ferramentas...</div>
    </div>
    <div class="dl-field">
      <label class="dl-label">Testar Chamada MCP (JSON-RPC):</label>
      <select id="mcp-test-tool" class="dl-select">
        <option value="search_dark_niches">search_dark_niches</option>
        <option value="generate_retention_script">generate_retention_script</option>
        <option value="analyze_video_metrics">analyze_video_metrics</option>
      </select>
    </div>
    <button class="dl-btn" onclick="executeMCPCall()">Executar Ferramenta via MCP</button>
    <div id="mcp-call-result" style="display:none; margin-top:12px;" class="dl-pre"></div>
  `;

  try {
    const res = await fetch(API_BASE_URL + "/api/mcp/tools");
    const d = await res.json();
    document.getElementById("mcp-tools-list").innerText = JSON.stringify(d.tools, null, 2);
  } catch (e) {
    document.getElementById("mcp-tools-list").innerText = "Erro ao listar ferramentas MCP.";
  }
}

async function executeMCPCall() {
  const tool = document.getElementById("mcp-test-tool").value;
  const out = document.getElementById("mcp-call-result");
  out.style.display = "block";
  out.innerText = `Invocando ${tool}...`;

  let args = {};
  if (tool === "search_dark_niches") args = { tab: "exploding", niche: "all" };
  else if (tool === "generate_retention_script") args = { title: "O Diário Proibido", niche: "Mistério", topic: "Bunker secreto" };
  else if (tool === "analyze_video_metrics") args = { url_or_id: "3OVnEqc-eqY" };

  try {
    const res = await fetch(API_BASE_URL + "/api/mcp/call", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: tool, arguments: args })
    });
    const data = await res.json();
    out.innerText = JSON.stringify(data, null, 2);
  } catch (e) {
    out.innerText = "Erro na execução MCP.";
  }
}

// 9. BIBLIOTECA DE MÍDIA
async function renderMediaLibraryTool(container, titleEl) {
  titleEl.innerHTML = `<span>🎵 Biblioteca de Mídia — Trilhas & SFX para Canais Dark</span>`;
  container.innerHTML = `
    <div style="display:grid; grid-template-columns:1fr; gap:12px;" id="media-list-container">
      Carregando biblioteca...
    </div>
  `;
  try {
    const res = await fetch(API_BASE_URL + "/api/media/library", {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    const media = await res.json();
    document.getElementById("media-list-container").innerHTML = media.map(m => `
      <div style="background:#151224; border:1px solid #28243d; border-radius:8px; padding:12px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <strong>${m.name}</strong>
          <div style="font-size:0.75rem; color:#9ca3af;">Tipo: ${m.media_type.toUpperCase()} · ${(m.file_size_bytes / 1024 / 1024).toFixed(2)} MB</div>
        </div>
        <audio controls style="height:36px;">
          <source src="${m.file_path}" type="audio/mpeg">
        </audio>
      </div>
    `).join("");
  } catch (e) {
    document.getElementById("media-list-container").innerText = "Erro ao carregar mídia.";
  }
}

// 10. DARKLAB STUDIO DESKTOP (PRODUTORA COMPLETA)
function renderDesktopStudioTool(container, titleEl) {
  titleEl.innerHTML = `<span>🖥️ DarkLAB Studio — Produtora Local para Windows</span>`;
  container.innerHTML = `
    <div style="background:#131122; border:1px solid #28243d; border-radius:12px; padding:1.25rem;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <span class="ds-chip ds-chip--ok">Equipe Autônoma Ativa</span>
        <button class="dl-btn" onclick="runStudioExportSimulation()">Renderizar e Exportar Vídeo</button>
      </div>
      <div style="display:grid; grid-template-columns:2fr 1fr; gap:15px;">
        <div style="background:#090812; border:1px solid #201c36; border-radius:8px; height:240px; display:flex; flex-direction:column; align-items:center; justify-content:center; position:relative;">
          <img src="/studio-preview/scene-1.webp" style="max-height:100%; object-fit:contain; border-radius:6px;" alt="Preview">
          <div style="position:absolute; bottom:12px; background:rgba(0,0,0,0.7); padding:4px 12px; border-radius:4px; font-weight:800; font-size:1.1rem; color:#fff; text-shadow:0 2px 4px #000;">
            UMA PORTA TRANCADA POR DENTRO
          </div>
        </div>
        <div style="background:#0e0c1a; border:1px solid #201c36; border-radius:8px; padding:12px; font-size:0.85rem; display:flex; flex-direction:column; gap:8px;">
          <strong style="color:#a78bfa;">Status da Equipe de Agentes:</strong>
          <div>✓ <strong>Diretor:</strong> Orquestrando cena 1 a 13</div>
          <div>✓ <strong>Pesquisador:</strong> Fontes históricas validadas</div>
          <div>✓ <strong>Roteirista:</strong> Retenção estimada em 94%</div>
          <div>✓ <strong>Narrador:</strong> Tom grave misterioso pronto</div>
          <div>✓ <strong>Editor:</strong> Legendas Impacto aplicadas</div>
        </div>
      </div>
      <div style="margin-top:15px; background:#0e0c1a; border:1px solid #201c36; border-radius:8px; padding:10px;">
        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#9ca3af; margin-bottom:6px;">
          <span>Timeline Multipista</span>
          <span style="font-family:'JetBrains Mono';">00:00:00 / 00:15:30</span>
        </div>
        <div style="height:24px; background:#1e1a35; border-radius:4px; display:flex; gap:2px; padding:2px; overflow:hidden;">
          <div style="flex:2; background:#8b5cf6; border-radius:2px;"></div>
          <div style="flex:1.5; background:#6366f1; border-radius:2px;"></div>
          <div style="flex:3; background:#ec4899; border-radius:2px;"></div>
          <div style="flex:2; background:#3b82f6; border-radius:2px;"></div>
        </div>
      </div>
    </div>
  `;
}

// 11. CARTEIRA DE TOKENS
async function renderTokensWalletTool(container, titleEl) {
  titleEl.innerHTML = `<span>💰 Carteira & Assinatura de Tokens</span>`;
  container.innerHTML = `
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px; margin-bottom:1.5rem;">
      <div style="background:#151224; border:1px solid #28243d; border-radius:10px; padding:1.25rem;">
        <small style="color:#9ca3af;">Saldo do Plano Mensal:</small>
        <h2 style="color:#10b981; font-family:'JetBrains Mono'; margin-top:4px;" id="w-plan-bal">--</h2>
        <small style="color:#6b7280;">Renova todo mês. Não acumula.</small>
      </div>
      <div style="background:#151224; border:1px solid #28243d; border-radius:10px; padding:1.25rem;">
        <small style="color:#9ca3af;">Saldo Avulso:</small>
        <h2 style="color:#a78bfa; font-family:'JetBrains Mono'; margin-top:4px;" id="w-extra-bal">--</h2>
        <small style="color:#6b7280;">Tokens que nunca expiram.</small>
      </div>
    </div>
    <button class="dl-btn" onclick="purchaseExtraTokens()">+ Comprar 100.000 Tokens Avulsos (R$ 29,90)</button>
  `;

  try {
    const res = await fetch(API_BASE_URL + "/api/tokens/balance", {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    const d = await res.json();
    document.getElementById("w-plan-bal").innerText = d.plan_balance.toLocaleString("pt-BR");
    document.getElementById("w-extra-bal").innerText = d.extra_balance.toLocaleString("pt-BR");
  } catch (e) {}
}

async function purchaseExtraTokens() {
  alert("Recarga simulada com sucesso! 100.000 tokens avulsos creditados.");
  await syncTokenBalance();
}

// 12. FERRAMENTAS GENÉRICAS ADICIONAIS (Canais, Personagens, Templates, etc.)
function renderGenericTool(container, titleEl, slug) {
  titleEl.innerHTML = `<span>🛠️ ${slug.toUpperCase()}</span>`;
  container.innerHTML = `
    <div style="padding:1.5rem; background:#151224; border-radius:10px;">
      <h3>Módulo ${slug}</h3>
      <p style="color:#9ca3af; margin:10px 0;">Este módulo está totalmente integrado à Stack de Agentes.</p>
      <button class="dl-btn" onclick="openToolModal('roteiros')">Voltar ao Roteirizador</button>
    </div>
  `;
}

function renderCharactersTool(container, titleEl) {
  titleEl.innerHTML = `<span>🎭 Personagens Consistentes (Face Consistency)</span>`;
  container.innerHTML = `
    <p style="color:#9ca3af; margin-bottom:15px;">Mantenha o mesmo protagonista em todas as cenas com Face-Lock e Seeds fixas.</p>
    <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px;">
      <div style="background:#161327; border:1px solid #28243d; border-radius:8px; padding:12px;">
        <strong>Investigador Marcus</strong>
        <p style="font-size:0.75rem; color:#9ca3af; margin:6px 0;">Homem de 40 anos, sobretudo escuro, olhar cansado e misterioso.</p>
        <span class="ds-chip ds-chip--ok">Trava Facial Ativa</span>
      </div>
      <div style="background:#161327; border:1px solid #28243d; border-radius:8px; padding:12px;">
        <strong>Dra. Helena Voss</strong>
        <p style="font-size:0.75rem; color:#9ca3af; margin:6px 0;">Historiadora e perita em línguas antigas, óculos e pasta de couro.</p>
        <span class="ds-chip ds-chip--ok">Trava Facial Ativa</span>
      </div>
      <div style="background:#161327; border:1px solid #28243d; border-radius:8px; padding:12px; display:flex; align-items:center; justify-content:center; cursor:pointer;" onclick="prompt('Nome do novo personagem:', 'Capitão Miller')">
        <span style="color:#8b5cf6; font-weight:bold;">+ Novo Personagem</span>
      </div>
    </div>
  `;
}

function renderExtensionSimulatorTool(container, titleEl) {
  titleEl.innerHTML = `<span>🧩 Extensão para YouTube — Simulador de Overlay</span>`;
  container.innerHTML = `
    <p style="color:#9ca3af; margin-bottom:12px;">Veja como a extensão da DarkLAB injeta dados diretamente na tela do YouTube:</p>
    <div style="background:#090812; border:1px solid #28243d; border-radius:10px; padding:1rem;">
      <div style="display:flex; gap:15px; align-items:center;">
        <img src="/studio-preview/scene-2.webp" style="width:200px; height:112px; border-radius:6px; object-fit:cover;">
        <div>
          <div style="display:flex; gap:8px; margin-bottom:6px;">
            <span style="background:#f59e0b; color:#000; font-weight:bold; font-size:0.7rem; padding:2px 6px; border-radius:4px;">$ MONETIZADO</span>
            <span style="background:#10b981; color:#000; font-weight:bold; font-size:0.7rem; padding:2px 6px; border-radius:4px;">OUTLIER ×28.4</span>
          </div>
          <h4>O Povoado Que Desapareceu em 1943 Sem Deixar Vestígios</h4>
          <p style="font-size:0.8rem; color:#9ca3af; margin:4px 0;">845.200 views · Retenção estimada: 88%</p>
          <button class="dl-btn" style="padding:4px 10px; font-size:0.75rem; margin-top:6px;" onclick="openToolModal('roteiros', {title: 'O Povoado Que Desapareceu'})">⚡ Importar para DarkLAB</button>
        </div>
      </div>
    </div>
  `;
}

function renderNicheExpansionTool(container, titleEl) {
  titleEl.innerHTML = `<span>🌐 Expansão de Nicho & Arbitragem Global</span>`;
  container.innerHTML = `
    <div class="dl-field">
      <label class="dl-label">Nicho de Origem:</label>
      <input type="text" class="dl-input" value="Mistério & Relatos Reais">
    </div>
    <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; margin-top:15px;">
      <div style="background:#151224; border:1px solid #28243d; border-radius:8px; padding:12px;">
        <strong>História Não Contada</strong>
        <div style="color:#10b981; font-weight:bold; margin:6px 0;">Afinidade: 92%</div>
        <small style="color:#9ca3af;">CPM Estimado em Dólar: $8.40</small>
      </div>
      <div style="background:#151224; border:1px solid #28243d; border-radius:8px; padding:12px;">
        <strong>Lugares Abandonados</strong>
        <div style="color:#10b981; font-weight:bold; margin:6px 0;">Afinidade: 86%</div>
        <small style="color:#9ca3af;">CPM Estimado em Dólar: $7.10</small>
      </div>
      <div style="background:#151224; border:1px solid #28243d; border-radius:8px; padding:12px;">
        <strong>Oceano & Criaturas</strong>
        <div style="color:#10b981; font-weight:bold; margin:6px 0;">Afinidade: 79%</div>
        <small style="color:#9ca3af;">CPM Estimado em Dólar: $6.80</small>
      </div>
    </div>
  `;
}

function renderMyChannelsTool(container, titleEl) {
  titleEl.innerHTML = `<span>📺 Meus Canais — Portfólio & Aprendizado de Estilo</span>`;
  container.innerHTML = `
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:15px;">
      <div style="background:#151224; border:1px solid #28243d; border-radius:8px; padding:12px;">
        <h4>Arquivos do Sobrenatural</h4>
        <p style="color:#9ca3af; font-size:0.8rem; margin:4px 0;">14.500 inscritos · 3 vídeos/semana</p>
        <span class="ds-chip ds-chip--ok">IA Treinada no Estilo</span>
      </div>
      <div style="background:#151224; border:1px solid #28243d; border-radius:8px; padding:12px;">
        <h4>Crônicas do Passado</h4>
        <p style="color:#9ca3af; font-size:0.8rem; margin:4px 0;">28.200 inscritos · 2 vídeos/semana</p>
        <span class="ds-chip ds-chip--ok">IA Treinada no Estilo</span>
      </div>
    </div>
    <button class="dl-btn" onclick="prompt('Link do Canal do YouTube:', 'https://youtube.com/@meucanal')">+ Conectar Novo Canal</button>
  `;
}

function renderTemplatesTool(container, titleEl) {
  titleEl.innerHTML = `<span>🎨 Templates de Canal — Padrão Visual e Sonoro</span>`;
  container.innerHTML = `
    <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px;">
      <div style="background:#161327; border:2px solid #8b5cf6; border-radius:8px; padding:12px;">
        <strong>Template Dark Mistery</strong>
        <p style="font-size:0.75rem; color:#9ca3af; margin:6px 0;">Voz: Marcus | Legenda: Impacto Neon | Ritmo: 4s</p>
        <span class="ds-chip ds-chip--ok">Ativo no Canal</span>
      </div>
      <div style="background:#161327; border:1px solid #28243d; border-radius:8px; padding:12px;">
        <strong>Template True Crime</strong>
        <p style="font-size:0.75rem; color:#9ca3af; margin:6px 0;">Voz: Valéria | Legenda: Bold Yellow | Ritmo: 5s</p>
        <button class="dl-btn dl-btn-secondary" style="padding:4px 8px; font-size:0.7rem;">Aplicar</button>
      </div>
      <div style="background:#161327; border:1px solid #28243d; border-radius:8px; padding:12px;">
        <strong>Template História Épica</strong>
        <p style="font-size:0.75rem; color:#9ca3af; margin:6px 0;">Voz: Erick | Legenda: Cyber Blue | Ritmo: 3.5s</p>
        <button class="dl-btn dl-btn-secondary" style="padding:4px 8px; font-size:0.7rem;">Aplicar</button>
      </div>
    </div>
  `;
}

function renderTranscriptionTool(container, titleEl) {
  titleEl.innerHTML = `<span>🎙️ Fala para Texto — Transcrição Whisper</span>`;
  container.innerHTML = `
    <div class="dl-field">
      <label class="dl-label">Cole a URL do Vídeo ou Áudio:</label>
      <input type="text" class="dl-input" value="https://youtube.com/watch?v=3OVnEqc-eqY">
    </div>
    <button class="dl-btn" onclick="alert('Áudio processado pelo Whisper! Transcrição pronta com timestamps.')">Transcrever Áudio com IA</button>
  `;
}
