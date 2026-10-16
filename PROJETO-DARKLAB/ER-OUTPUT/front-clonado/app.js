// DarkLAB AI Studio - Frontend Application Engine
let currentToken = null;
let currentScriptId = null;

// Inicialização
document.addEventListener("DOMContentLoaded", async () => {
  await ensureAuthentication();
  await refreshTokens();
  await loadNicheChannels("exploding");
  await loadKanbanBoard();
});

// Autenticação automática para desenvolvimento
async function ensureAuthentication() {
  const savedToken = localStorage.getItem("darklab_token");
  if (savedToken) {
    currentToken = savedToken;
    return;
  }

  try {
    // Tenta registrar usuário padrão de teste
    const regRes = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Produtor Dark",
        email: "criador@darklab.ai",
        password: "senha_segura_123",
        workspace_name: "Dark Studio Alpha",
        plan_tier: "plus"
      })
    });

    if (regRes.ok) {
      const data = await regRes.json();
      currentToken = data.access_token;
      localStorage.setItem("darklab_token", currentToken);
      return;
    }

    // Se já existia, faz login
    const loginRes = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: "criador@darklab.ai",
        password: "senha_segura_123"
      })
    });

    if (loginRes.ok) {
      const data = await loginRes.json();
      currentToken = data.access_token;
      localStorage.setItem("darklab_token", currentToken);
    }
  } catch (err) {
    console.error("Erro na autenticação:", err);
  }
}

// Navegação entre Abas
function switchTab(tabId) {
  const sections = ["viral-lab", "roteiros", "narracao", "storyboard", "kanban"];
  sections.forEach(s => {
    const el = document.getElementById(`section-${s}`);
    if (el) el.style.display = (s === tabId) ? "block" : "none";
  });

  document.querySelectorAll(".nav-item").forEach(item => {
    item.classList.remove("active");
  });
  if (event && event.target) {
    event.target.classList.add("active");
  }
}

// Atualizar Saldo de Tokens
async function refreshTokens() {
  if (!currentToken) return;
  try {
    const res = await fetch("/api/tokens/balance", {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (res.ok) {
      const data = await res.json();
      const el = document.getElementById("token-balance-display");
      if (el) el.innerText = data.total_balance.toLocaleString("pt-BR");
    }
  } catch (e) {
    console.error("Falha ao atualizar tokens:", e);
  }
}

// Carregar Canais do Niche Finder
async function loadNicheChannels(tab, btnElement) {
  if (btnElement) {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    btnElement.classList.add("active");
  }

  const tbody = document.getElementById("channels-table-body");
  tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">Varrendo radar do YouTube...</td></tr>`;

  try {
    const res = await fetch(`/api/viral-lab/niche-finder?tab=${tab}`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (res.ok) {
      const channels = await res.json();
      tbody.innerHTML = channels.map(c => `
        <tr>
          <td><strong>${c.title}</strong></td>
          <td>${c.niche}</td>
          <td>${c.subscribers.toLocaleString("pt-BR")}</td>
          <td>${c.views.toLocaleString("pt-BR")}</td>
          <td>${c.age_days} dias</td>
          <td><span class="outlier-badge">×${c.outlier_score}</span></td>
          <td>${c.is_monetized ? '<span class="money-badge">$ Sim</span>' : '<span style="color:var(--text-dim)">Não</span>'}</td>
        </tr>
      `).join("");
    }
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="color:red; text-align:center;">Erro ao carregar canais.</td></tr>`;
  }
}

// Raio-X de Vídeo
async function analyzeVideo() {
  const url = document.getElementById("video-url-input").value;
  const outBox = document.getElementById("video-analysis-output");
  outBox.style.display = "block";
  outBox.innerText = "Executando Raio-X com IA...";

  try {
    const res = await fetch("/api/viral-lab/analyze-video", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${currentToken}`
      },
      body: JSON.stringify({ url_or_id: url })
    });
    if (res.ok) {
      const data = await res.json();
      outBox.innerHTML = `
        <strong>Título:</strong> ${data.title}<br>
        <strong>Visualizações:</strong> ${data.views.toLocaleString("pt-BR")} | <strong>VPH Estimado:</strong> ${data.estimated_vph} views/h<br>
        <strong>Índice de Retenção:</strong> ${data.retention_score}% | <strong>Força do Gancho:</strong> ${data.hook_strength}<br>
        <strong>Monetizado:</strong> ${data.is_monetized ? 'Sim ($)' : 'Não'}<br>
        <strong>Tags Ocultas:</strong> ${data.tags.join(", ")}<br><br>
        <strong>Diagnóstico Clínico:</strong> ${data.summary}
      `;
    }
  } catch (err) {
    outBox.innerText = "Erro ao analisar vídeo.";
  }
}

// Geração de Roteiro
async function generateScript() {
  const title = document.getElementById("script-title-input").value;
  const niche = document.getElementById("script-niche-input").value;
  const formula = document.getElementById("script-formula-select").value;
  const topic = document.getElementById("script-topic-input").value;
  const box = document.getElementById("script-result-box");

  box.style.display = "block";
  box.innerText = "Engenhando roteiro POV com gancho nos primeiros 30s...";

  try {
    const res = await fetch("/api/scripts/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${currentToken}`
      },
      body: JSON.stringify({
        title: title,
        niche: niche,
        topic_description: topic,
        formula_style: formula
      })
    });

    if (res.ok) {
      const script = await res.json();
      currentScriptId = script.id;
      box.innerHTML = `
        <div style="color:var(--accent-green); font-weight:bold; margin-bottom:10px;">
          ✅ Roteiro Gerado com Sucesso! (${script.character_count} caracteres | ~${script.estimated_audio_tokens} tokens de voz necessários)
        </div>
        <strong>[GANCHO - PRIMEIROS 30 SEGUNDOS]:</strong>\n${script.hook_text}\n\n
        <strong>[LOOP ABERTO / RETENÇÃO]:</strong>\n${script.open_loop}\n\n
        <strong>[CORPO DO RELATO POV]:</strong>\n${script.body_text}\n\n
        <strong>[CHAMADA PARA AÇÃO - CTA]:</strong>\n${script.cta_text}
      `;
    }
  } catch (err) {
    box.innerText = "Erro ao gerar roteiro.";
  }
}

// Síntese de Narração TTS com Débito de Tokens
async function generateNarration() {
  if (!currentScriptId) {
    alert("Por favor, gere um roteiro primeiro na aba 'Roteiros POV'.");
    switchTab("roteiros");
    return;
  }

  const voiceName = document.getElementById("voice-name-select").value;
  const playerContainer = document.getElementById("narration-player-container");
  const infoText = document.getElementById("narration-info-text");
  const audioPlayer = document.getElementById("tts-audio-player");

  infoText.innerText = "Sintetizando voz e debitando caracteres da carteira...";
  playerContainer.style.display = "flex";

  try {
    const res = await fetch("/api/tts/generate-voice", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${currentToken}`
      },
      body: JSON.stringify({
        script_id: currentScriptId,
        voice_name: voiceName
      })
    });

    if (res.ok) {
      const data = await res.json();
      infoText.innerHTML = `
        🎙️ Narração Concluída! Voz: <strong>${data.voice_name}</strong> |
        Caracteres: <strong>${data.characters_count}</strong> |
        Tokens Debitados: <strong style="color:var(--accent-pink);">${data.tokens_debited}</strong> |
        Duração: <strong>${data.duration_seconds}s</strong>
      `;
      audioPlayer.src = data.audio_url;
      audioPlayer.play();
      await refreshTokens();
    } else {
      const err = await res.json();
      infoText.innerHTML = `<span style="color:red;">Falha: ${err.detail || 'Erro na síntese'}</span>`;
    }
  } catch (err) {
    infoText.innerText = "Erro ao gerar áudio.";
  }
}

// Storyboard de Cenas Automático
async function generateStoryboard() {
  if (!currentScriptId) {
    alert("Por favor, gere um roteiro primeiro na aba 'Roteiros POV'.");
    switchTab("roteiros");
    return;
  }

  const container = document.getElementById("scenes-container");
  container.innerHTML = "<p style='color:var(--text-muted);'>Processando timeline e criando prompts cinematográficos...</p>";

  try {
    const res = await fetch("/api/storyboard/auto-scenes", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${currentToken}`
      },
      body: JSON.stringify({ script_id: currentScriptId, seconds_per_scene: 4 })
    });

    if (res.ok) {
      const data = await res.json();
      container.innerHTML = data.scenes.map(s => `
        <div class="scene-card">
          <div class="scene-time">Cena #${s.scene_number} (${s.start_time}s ➔ ${s.end_time}s)</div>
          <div style="font-size:0.85rem;"><strong>Trecho de Áudio:</strong> "${s.narration_chunk}"</div>
          <div class="scene-prompt"><strong>Prompt de Imagem:</strong> ${s.visual_prompt}</div>
          <div style="font-size:0.75rem; color:var(--accent-purple);">Avatar Consistente: ${s.character_name}</div>
        </div>
      `).join("");
    }
  } catch (err) {
    container.innerHTML = "<p style='color:red;'>Erro ao gerar storyboard.</p>";
  }
}

// Visualizar SRT
async function loadSRT() {
  if (!currentScriptId) {
    alert("Gere o roteiro e as cenas primeiro.");
    return;
  }
  const display = document.getElementById("srt-display");
  display.style.display = "block";
  display.innerText = "Buscando arquivo SRT...";

  try {
    const res = await fetch(`/api/storyboard/${currentScriptId}/srt`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (res.ok) {
      const data = await res.json();
      display.innerText = data.srt_content;
    }
  } catch (e) {
    display.innerText = "Erro ao buscar legendas SRT.";
  }
}

// Carregar Quadro Kanban
async function loadKanbanBoard() {
  if (!currentToken) return;
  try {
    const res = await fetch("/api/kanban/board", {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (res.ok) {
      const board = await res.json();
      const cols = ["ideia", "roteiro", "narracao", "cenas", "edicao", "concluido"];
      cols.forEach(col => {
        const colEl = document.getElementById(`col-${col}`);
        if (!colEl) return;
        const cards = board[col] || [];
        const header = colEl.querySelector(".column-header").outerHTML;
        colEl.innerHTML = header + cards.map(c => `
          <div class="kanban-card-item">
            <div>${c.title}</div>
            <div style="font-size:0.7rem; color:var(--text-dim); margin-top:4px;">ID: ${c.id.substring(0,8)}...</div>
          </div>
        `).join("");
      });
    }
  } catch (err) {
    console.error("Erro ao carregar kanban:", err);
  }
}

// Adicionar Card Exemplo
async function addSampleKanbanCard() {
  if (!currentToken) return;
  const title = prompt("Título do novo vídeo dark:", "O Farol Abandonado de 1928");
  if (!title) return;

  await fetch("/api/kanban/cards", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${currentToken}`
    },
    body: JSON.stringify({ title: title, column_status: "ideia" })
  });
  await loadKanbanBoard();
}
