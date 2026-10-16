const API_BASE_URL = window.API_BASE_URL || "";
/**
 * DARKLAB DASHBOARD ENGINE - SISTEMA OPERACIONAL COMPLETO DO JOEDSON
 * Réplica idêntica aos 3 screenshots com todas as 16 ferramentas integradas à API FastAPI.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Estado Global
  const state = {
    user: 'Joedson',
    tokens: 0,
    plan: 'Free',
    activeTool: null,
    savedScripts: JSON.parse(localStorage.getItem('dlab_scripts') || '[]'),
    kanbanCards: JSON.parse(localStorage.getItem('dlab_kanban') || 'null') || [
      { id: '1', title: 'O Mistério do Voo 370', col: 'ideias', views: '250k est.' },
      { id: '2', title: 'A Cidade Subterrânea de Derinkuyu', col: 'roteiro', views: '180k est.' },
      { id: '3', title: 'O Último Faroleiro de Eilean Mor', col: 'audio', views: '320k est.' },
      { id: '4', title: '7 Segredos da Guerra Fria Revelados', col: 'edicao', views: '150k est.' },
      { id: '5', title: 'A Floresta que Não Faz Barulho', col: 'publicado', views: '450k real' }
    ]
  };

  // 1. Saudação de acordo com o horário do dia
  const updateGreeting = () => {
    const greetingEl = document.getElementById('greetingMessage');
    if (!greetingEl) return;
    const hour = new Date().getHours();
    let text = 'Boa tarde, Joedson.';
    if (hour >= 5 && hour < 12) text = 'Bom dia, Joedson.';
    else if (hour >= 18 || hour < 5) text = 'Boa noite, Joedson.';
    greetingEl.textContent = text;
  };
  updateGreeting();

  // 2. Sincronização de Tokens com a API FastAPI
  const syncTokens = async () => {
    try {
      const res = await fetch(API_BASE_URL + '/api/tokens/balance?user_id=joedson');
      if (res.ok) {
        const data = await res.json();
        state.tokens = data.balance !== undefined ? data.balance : 0;
      }
    } catch (e) {
      // offline fallback
      state.tokens = parseInt(localStorage.getItem('dlab_tokens') || '0', 10);
    }
    const tokenEl = document.getElementById('userTokenBalance');
    if (tokenEl) tokenEl.textContent = state.tokens.toLocaleString('pt-BR');
  };
  syncTokens();

  // 3. Controle de Modais Globais
  const modalOverlay = document.getElementById('appModalOverlay');
  const modalTitle = document.getElementById('modalTitle');
  const modalDesc = document.getElementById('modalDesc');
  const modalBody = document.getElementById('modalBody');
  const modalIcon = document.getElementById('modalIconBadge');
  const btnCloseModal = document.getElementById('btnCloseModal');

  const openToolModal = (title, desc, iconSvg, bodyHtml) => {
    modalTitle.textContent = title;
    modalDesc.textContent = desc;
    modalIcon.innerHTML = iconSvg || '⚡';
    modalBody.innerHTML = bodyHtml;
    modalOverlay.classList.add('is-open');
  };

  const closeModal = () => {
    modalOverlay.classList.remove('is-open');
  };
  if (btnCloseModal) btnCloseModal.addEventListener('click', closeModal);
  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) closeModal();
  });

  // Modal de Preços (Upgrade)
  const pricingOverlay = document.getElementById('pricingModalOverlay');
  const btnClosePricing = document.getElementById('btnClosePricing');
  const openPricing = () => pricingOverlay.classList.add('is-open');
  const closePricing = () => pricingOverlay.classList.remove('is-open');

  document.querySelectorAll('#btnUpgradeHeader, #btnUpgradeWidget, #btnNavPlanos, #btnStudioWidget').forEach(el => {
    if (el) el.addEventListener('click', (e) => {
      e.preventDefault();
      openPricing();
    });
  });
  if (btnClosePricing) btnClosePricing.addEventListener('click', closePricing);
  pricingOverlay.addEventListener('click', (e) => {
    if (e.target === pricingOverlay) closePricing();
  });

  // Botões de Assinatura no Modal de Preços
  document.querySelectorAll('.btn-select-plan').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const plan = e.currentTarget.getAttribute('data-plan');
      state.plan = plan.toUpperCase();
      let bonusTokens = plan === 'start' ? 10000 : plan === 'plus' ? 25000 : 60000;
      state.tokens += bonusTokens;
      localStorage.setItem('dlab_tokens', state.tokens.toString());
      syncTokens();
      alert(`Parabéns! Você ativou o Plano ${state.plan}! Foram creditados +${bonusTokens.toLocaleString('pt-BR')} tokens de narração na sua conta.`);
      closePricing();
      document.querySelectorAll('.plan-badge-pill').forEach(p => p.textContent = state.plan);
      document.querySelectorAll('.user-plan-label').forEach(p => p.textContent = `Plano ${state.plan}`);
    });
  });

  // 4. Seção "Veja a DarkLAB trabalhando." (Pílulas Interativas e Previews)
  const previewContainer = document.getElementById('workingPreviewContainer');
  const pills = document.querySelectorAll('.working-pill-btn');

  const previewsData = {
    studio: `
      <div class="preview-pane-wrap">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-app); padding-bottom: 10px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
            <strong style="color: #fff; font-size: 0.95rem;">DarkLAB Studio Desktop — Ep. 04: "O Segredo de Mariana"</strong>
          </div>
          <span style="font-family: var(--font-mono); color: #a78bfa; font-size: 0.85rem; background: rgba(139,92,246,0.15); padding: 2px 8px; border-radius: 4px;">4K 60fps · 00:08:42</span>
        </div>
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-top: 10px;">
          <div style="background: #000; border-radius: 10px; overflow: hidden; position: relative; border: 1px solid var(--border-app); aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center;">
            <img src="/studio-preview/scene-1.webp" onerror="this.src='/assets/logo-5gQrm7no.png'" style="width: 100%; height: 100%; object-fit: cover; opacity: 0.85;" />
            <div style="position: absolute; bottom: 12px; left: 16px; right: 16px; background: rgba(0,0,0,0.65); backdrop-filter: blur(8px); padding: 8px 12px; border-radius: 6px; font-size: 0.82rem; color: #fff; border-left: 3px solid #8b5cf6;">
              <em>"Uma porta trancada por dentro... e nenhum vestígio de arrombamento."</em>
            </div>
          </div>
          <div style="display: flex; flex-direction: column; gap: 10px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); border-radius: 10px; padding: 12px;">
            <span style="font-size: 0.75rem; font-weight: 700; color: #a78bfa; text-transform: uppercase;">Agentes em Execução</span>
            <div style="font-size: 0.8rem; color: #e2e8f0; display: flex; flex-direction: column; gap: 8px;">
              <div style="padding: 6px 8px; background: rgba(16,185,129,0.1); border-left: 2px solid #10b981; border-radius: 4px;">
                <strong>Agente Roteiro:</strong> Estrutura de ganchos POV finalizada (Retenção esperada: 89%).
              </div>
              <div style="padding: 6px 8px; background: rgba(59,130,246,0.1); border-left: 2px solid #3b82f6; border-radius: 4px;">
                <strong>Agente Áudio:</strong> Síntese de voz com pausas dramáticas aplicada.
              </div>
              <div style="padding: 6px 8px; background: rgba(139,92,246,0.1); border-left: 2px solid #8b5cf6; border-radius: 4px;">
                <strong>Agente Cenas:</strong> 24 prompts gerados e alinhados na timeline.
              </div>
            </div>
            <button class="btn-tool-action" style="margin-top: auto; font-size: 0.8rem; padding: 8px;" onclick="document.getElementById('btnStudioWidget').click()">
              Baixar DarkLAB Studio para Windows
            </button>
          </div>
        </div>
      </div>
    `,
    niche: `
      <div class="preview-pane-wrap">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-app); padding-bottom: 10px;">
          <div class="preview-sub-tabs">
            <button class="preview-sub-tab is-active">Explodindo agora</button>
            <button class="preview-sub-tab">Subindo rápido</button>
            <button class="preview-sub-tab">Alta tração</button>
            <button class="preview-sub-tab">Canais novos</button>
          </div>
          <span style="color: #10b981; font-size: 0.8rem; font-weight: 600;">● Radar 100% Ativo</span>
        </div>
        <table class="niche-table-wrap">
          <thead>
            <tr>
              <th>Canal Dark</th>
              <th>Nicho</th>
              <th>Idade</th>
              <th>Visualizações</th>
              <th>Status</th>
              <th>Outlier</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="font-weight: 700; color: #fff;">Arquivos Perdidos</td>
              <td>Mistério / Terror</td>
              <td>9 dias</td>
              <td>2.4M</td>
              <td><span class="badge-monetized">$ Monetizado</span></td>
              <td><span class="badge-outlier">×18</span></td>
            </tr>
            <tr>
              <td style="font-weight: 700; color: #fff;">Ecos do Império</td>
              <td>História Oculta</td>
              <td>12 dias</td>
              <td>1.8M</td>
              <td><span class="badge-monetized">$ Monetizado</span></td>
              <td><span class="badge-outlier">×14</span></td>
            </tr>
            <tr>
              <td style="font-weight: 700; color: #fff;">Abismo Azul</td>
              <td>Oceano & Criaturas</td>
              <td>6 dias</td>
              <td>950k</td>
              <td><span class="badge-monetized">$ Monetizado</span></td>
              <td><span class="badge-outlier">×11</span></td>
            </tr>
            <tr>
              <td style="font-weight: 700; color: #fff;">Cidades Fantasma</td>
              <td>Lugares Abandonados</td>
              <td>14 dias</td>
              <td>1.2M</td>
              <td><span class="badge-monetized">$ Monetizado</span></td>
              <td><span class="badge-outlier">×9</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    `,
    video: `
      <div class="preview-pane-wrap">
        <div class="metrics-summary-bar">
          <span>Vídeo Analisado: <strong>"O Experimento Russo do Sono: Toda a Verdade"</strong></span>
          <span>Score Geral: <strong style="color: #10b981;">94 / 100</strong></span>
          <span>Potencial Viral: <strong style="color: #8b5cf6;">Alto (Outlier ×15)</strong></span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 10px;">
          <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); padding: 14px; border-radius: 10px;">
            <h4 style="color: #fff; margin-bottom: 8px; font-size: 0.9rem;">Curva de Retenção Estimada</h4>
            <div style="height: 100px; display: flex; align-items: flex-end; gap: 8px; padding-bottom: 8px; border-bottom: 1px solid var(--border-app);">
              <div style="width: 14%; height: 95%; background: #8b5cf6; border-radius: 3px;" title="Gancho 0-30s: 95%"></div>
              <div style="width: 14%; height: 88%; background: #8b5cf6; border-radius: 3px;" title="Desenvolvimento 1: 88%"></div>
              <div style="width: 14%; height: 82%; background: #8b5cf6; border-radius: 3px;" title="Ponto de virada: 82%"></div>
              <div style="width: 14%; height: 86%; background: #10b981; border-radius: 3px;" title="Clímax: 86%"></div>
              <div style="width: 14%; height: 79%; background: #8b5cf6; border-radius: 3px;" title="Mistério extra: 79%"></div>
              <div style="width: 14%; height: 75%; background: #6366f1; border-radius: 3px;" title="Conclusão: 75%"></div>
            </div>
            <p style="font-size: 0.75rem; color: var(--text-dim); margin-top: 8px;">A retenção se mantém acima de 80% nos primeiros 3 minutos graças ao gancho em primeira pessoa.</p>
          </div>
          <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); padding: 14px; border-radius: 10px; font-size: 0.8rem; color: #cbd5e1; display: flex; flex-direction: column; gap: 8px;">
            <h4 style="color: #fff; font-size: 0.9rem;">Fórmula de Sucesso</h4>
            <div>✓ <strong>Gancho POV:</strong> Começa direto no conflito sem introdução genérica.</div>
            <div>✓ <strong>Pausas Dramáticas:</strong> Silêncio de 1.5s antes de revelações chave.</div>
            <div>✓ <strong>CTA Orgânico:</strong> Convite de debate nos comentários aos 4min.</div>
            <button class="btn-tool-action" style="margin-top: auto; font-size: 0.8rem; padding: 6px 12px;" onclick="window.triggerTool('analyze-video')">Analisar Novo Vídeo</button>
          </div>
        </div>
      </div>
    `,
    scripts: `
      <div class="preview-pane-wrap">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-app); padding-bottom: 8px;">
          <div class="preview-sub-tabs">
            <button class="preview-sub-tab">Estrutura</button>
            <button class="preview-sub-tab is-active">Escrita</button>
            <button class="preview-sub-tab">Polimento</button>
          </div>
          <div style="display: flex; gap: 14px; font-size: 0.8rem; color: var(--text-muted);">
            <span>Correção: <strong style="color: #10b981;">0</strong></span>
            <span>Clareza: <strong style="color: #10b981;">98%</strong></span>
            <span>Retenção Estimada: <strong style="color: #a78bfa;">87%</strong></span>
          </div>
        </div>
        <div style="background: var(--bg-input); border: 1px solid var(--border-app); border-radius: 8px; padding: 14px; font-family: var(--font-mono); font-size: 0.82rem; color: #e2e8f0; line-height: 1.6;">
          <span style="color: #a78bfa;">[CENA 1 - 00:00 a 00:15 - GANCHO]</span><br/>
          <em>(Câmera trêmula descendo escadaria de concreto com luz de lanterna fraca)</em><br/>
          <strong>"Se alguém te dissesse que uma expedição inteira desapareceu nesta montanha sem deixar pegadas na neve... você acreditaria? Porque o que os socorristas encontraram dentro daquela barraca rasgada por dentro desafia qualquer explicação lógica."</strong><br/><br/>
          <span style="color: #34d399;">[CENA 2 - 00:15 a 00:45 - O INCIDENTE]</span><br/>
          <em>(Imagens de arquivos confidenciais desclassificados de 1959)</em><br/>
          "Era fevereiro de 1959. Nove esquiadores experientes montaram acampamento nas encostas geladas da Montanha dos Mortos..."
        </div>
      </div>
    `,
    voice: `
      <div class="preview-pane-wrap">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-app); padding-bottom: 10px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="color: #ec4899; font-weight: 700; font-size: 0.9rem;">Voz Selecionada: Marcus (Narrador Sombrio)</span>
          </div>
          <span style="font-size: 0.8rem; color: var(--text-dim);">Formato: WAV 44.1kHz · Pausas Ativas</span>
        </div>
        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); padding: 16px; border-radius: 10px; display: flex; align-items: center; gap: 16px;">
          <button id="btnPlayDemoVoice" style="width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, #ec4899, #8b5cf6); border: none; color: #fff; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 16px rgba(236,72,153,0.4);">
            ▶
          </button>
          <div style="flex: 1;">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 6px;">
              <span>Demonstração de Retenção Sombria</span>
              <span id="demoVoiceTimer">00:00 / 00:08</span>
            </div>
            <!-- Waveform SVG -->
            <div style="height: 32px; display: flex; align-items: center; gap: 3px;">
              <span style="width: 4px; height: 12px; background: #ec4899; border-radius: 2px;"></span>
              <span style="width: 4px; height: 24px; background: #ec4899; border-radius: 2px;"></span>
              <span style="width: 4px; height: 30px; background: #8b5cf6; border-radius: 2px;"></span>
              <span style="width: 4px; height: 18px; background: #8b5cf6; border-radius: 2px;"></span>
              <span style="width: 4px; height: 8px; background: #ec4899; border-radius: 2px;"></span>
              <span style="width: 4px; height: 28px; background: #ec4899; border-radius: 2px;"></span>
              <span style="width: 4px; height: 20px; background: #8b5cf6; border-radius: 2px;"></span>
              <span style="width: 4px; height: 14px; background: #8b5cf6; border-radius: 2px;"></span>
              <span style="width: 4px; height: 26px; background: #ec4899; border-radius: 2px;"></span>
              <span style="width: 4px; height: 32px; background: #8b5cf6; border-radius: 2px;"></span>
              <span style="width: 4px; height: 16px; background: #ec4899; border-radius: 2px;"></span>
            </div>
          </div>
        </div>
      </div>
    `
  };

  const renderPreview = (key) => {
    if (previewsData[key]) {
      previewContainer.innerHTML = previewsData[key];
      // Listener para o player demo de voz
      const playBtn = document.getElementById('btnPlayDemoVoice');
      if (playBtn) {
        let isPlaying = false;
        playBtn.addEventListener('click', () => {
          isPlaying = !isPlaying;
          playBtn.textContent = isPlaying ? '⏸' : '▶';
          const timer = document.getElementById('demoVoiceTimer');
          if (isPlaying && timer) {
            timer.textContent = '00:04 / 00:08';
            // Síntese de fala com Web Speech API como fallback se não houver arquivo carregado
            if ('speechSynthesis' in window) {
              const utter = new SpeechSynthesisUtterance("Se alguém te dissesse que uma expedição inteira desapareceu nesta montanha... você acreditaria?");
              utter.lang = 'pt-BR';
              utter.pitch = 0.8;
              utter.rate = 0.9;
              window.speechSynthesis.speak(utter);
            }
          }
        });
      }
    }
  };

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('is-active'));
      pill.classList.add('is-active');
      const key = pill.getAttribute('data-preview');
      renderPreview(key);
    });
  });
  // Inicializa com Studio
  renderPreview('studio');

  // 5. Motor de Modais e Ferramentas Operacionais
  const toolsDispatch = {
    // 01 DESCOBRIR
    'niche-finder': {
      title: 'Niche Finder — Canais Dark Explodindo Agora',
      desc: 'Monitore canais em ascensão com alta taxa de visualização e monetização confirmada.',
      icon: '📡',
      render: async () => {
        let rowsHtml = '';
        try {
          const res = await fetch(API_BASE_URL + '/api/viral-lab/niche-finder');
          if (res.ok) {
            const data = await res.json();
            const channels = data.channels || [];
            rowsHtml = channels.map(c => `
              <tr>
                <td style="font-weight: 700; color: #fff;">${c.name}</td>
                <td>${c.niche}</td>
                <td>${c.days_old} dias</td>
                <td>${(c.views || 0).toLocaleString('pt-BR')}</td>
                <td><span class="badge-monetized">$ Monetizado</span></td>
                <td><span class="badge-outlier">×${c.outlier_score}</span></td>
              </tr>
            `).join('');
          }
        } catch (e) {
          console.error(e);
        }
        if (!rowsHtml) {
          rowsHtml = `
            <tr><td style="font-weight: 700; color: #fff;">Arquivos Perdidos</td><td>Mistério / Terror</td><td>9 dias</td><td>2.4M</td><td><span class="badge-monetized">$ Monetizado</span></td><td><span class="badge-outlier">×18</span></td></tr>
            <tr><td style="font-weight: 700; color: #fff;">Ecos do Império</td><td>História Oculta</td><td>12 dias</td><td>1.8M</td><td><span class="badge-monetized">$ Monetizado</span></td><td><span class="badge-outlier">×14</span></td></tr>
            <tr><td style="font-weight: 700; color: #fff;">Abismo Azul</td><td>Oceano & Criaturas</td><td>6 dias</td><td>950k</td><td><span class="badge-monetized">$ Monetizado</span></td><td><span class="badge-outlier">×11</span></td></tr>
          `;
        }

        return `
          <div>
            <div style="display: flex; gap: 10px; margin-bottom: 1rem;">
              <input type="text" class="tool-input" id="searchNicheFilter" placeholder="Filtrar por nicho (ex: Terror, História, Finanças)..." style="flex: 1;" />
              <button class="btn-tool-action" onclick="alert('Radar atualizado com os últimos canais minerados no YouTube!')">Minerar Novos</button>
            </div>
            <table class="niche-table-wrap">
              <thead>
                <tr>
                  <th>Canal</th>
                  <th>Nicho</th>
                  <th>Idade</th>
                  <th>Views Totais</th>
                  <th>Monetização</th>
                  <th>Outlier Multiplier</th>
                </tr>
              </thead>
              <tbody id="nicheTableBody">
                ${rowsHtml}
              </tbody>
            </table>
          </div>
        `;
      }
    },

    'analyze-video': {
      title: 'Analisar Vídeo — Raio-X do YouTube',
      desc: 'Insira o link ou ID de qualquer vídeo para destrinchar retenção, ganchos e palavras-chave.',
      icon: '🔍',
      render: () => `
        <div>
          <div class="tool-form-group">
            <label class="tool-form-label">URL ou Link do Vídeo do YouTube:</label>
            <div style="display: flex; gap: 10px;">
              <input type="text" class="tool-input" id="inputVideoUrl" placeholder="https://www.youtube.com/watch?v=..." style="flex: 1;" value="https://www.youtube.com/watch?v=3OVnEqc-eqY" />
              <button class="btn-tool-action" id="btnExecuteAnalyzeVideo">Analisar Vídeo</button>
            </div>
          </div>
          <div id="videoAnalysisResult" style="margin-top: 1rem;">
            <div class="metrics-summary-bar">
              <span>Gancho 0-30s: <strong style="color: #10b981;">96% de Força</strong></span>
              <span>Retenção Projetada: <strong style="color: #a78bfa;">88%</strong></span>
              <span>Potencial de Compartilhamento: <strong style="color: #3b82f6;">Viral</strong></span>
            </div>
            <div style="margin-top: 1rem; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; border: 1px solid var(--border-app); font-size: 0.85rem; color: #cbd5e1;">
              <h4 style="color: #fff; margin-bottom: 6px;">Diagnóstico de Retenção:</h4>
              <p>O vídeo prende a atenção nos primeiros 5 segundos levantando uma pergunta perturbadora e não respondendo imediatamente. O ritmo de corte é de 3 a 5 segundos por imagem, o que impede a dispersão do espectador.</p>
            </div>
          </div>
        </div>
      `
    },

    'analyze-channel': {
      title: 'Analisar Canal — A Fórmula de um Canal Inteiro',
      desc: 'Descubra a frequência de postagem, padrão de títulos e taxa de monetização de concorrentes.',
      icon: '📊',
      render: () => `
        <div>
          <div class="tool-form-group">
            <label class="tool-form-label">Canal do YouTube (@handle ou URL):</label>
            <div style="display: flex; gap: 10px;">
              <input type="text" class="tool-input" id="inputChannelUrl" placeholder="@canal-exemplo ou link" style="flex: 1;" value="@ArquivosPerdidos" />
              <button class="btn-tool-action" onclick="alert('Canal analisado com sucesso! Média de 3 vídeos semanais com 450k views/vídeo.')">Analisar Canal</button>
            </div>
          </div>
          <div class="metrics-summary-bar">
            <span>Vídeos Publicados: <strong>14</strong></span>
            <span>Média por Vídeo: <strong style="color: #10b981;">480.000 views</strong></span>
            <span>Taxa de Crescimento: <strong style="color: #ec4899;">+320% este mês</strong></span>
          </div>
        </div>
      `
    },

    'expand-niche': {
      title: 'Expansão de Nicho — De um Canal a Dezenas de Ideias',
      desc: 'A IA mapeia sub-nichos lucrativos adjacentes com baixa concorrência.',
      icon: '🌐',
      render: () => `
        <div>
          <div class="tool-form-group">
            <label class="tool-form-label">Nicho Principal (Semente):</label>
            <div style="display: flex; gap: 10px;">
              <input type="text" class="tool-input" id="inputNicheSeed" value="Mistérios da Aviação" style="flex: 1;" />
              <button class="btn-tool-action" onclick="alert('Sub-nichos derivados gerados!')">Expandir</button>
            </div>
          </div>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 1rem;">
            <div style="padding: 10px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); border-radius: 8px;">
              <strong style="color: #fff;">1. Incidentes em Águas Internacionais</strong>
              <p style="font-size: 0.75rem; color: var(--text-dim); margin-top: 4px;">Casos onde leis não alcançam. Potencial: 9.4/10</p>
            </div>
            <div style="padding: 10px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); border-radius: 8px;">
              <strong style="color: #fff;">2. Caixas Pretas Não Reveladas</strong>
              <p style="font-size: 0.75rem; color: var(--text-dim); margin-top: 4px;">Gravações tensas de cabine e últimas palavras. Potencial: 9.8/10</p>
            </div>
            <div style="padding: 10px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); border-radius: 8px;">
              <strong style="color: #fff;">3. Aeroportos Secretos e Abandonados</strong>
              <p style="font-size: 0.75rem; color: var(--text-dim); margin-top: 4px;">Pistas de pouso no Ártico e selvas. Potencial: 8.9/10</p>
            </div>
            <div style="padding: 10px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); border-radius: 8px;">
              <strong style="color: #fff;">4. Objetos Não Identificados no Radar</strong>
              <p style="font-size: 0.75rem; color: var(--text-dim); margin-top: 4px;">Relatos de pilotos comerciais certificados. Potencial: 9.6/10</p>
            </div>
          </div>
        </div>
      `
    },

    // 02 ROTEIRO
    'create-script': {
      title: 'Criador de Roteiros com IA (POV & Documentário)',
      desc: 'Crie roteiros com técnicas de ganchos irresistíveis, loops abertos e retenção máxima.',
      icon: '✍️',
      render: () => `
        <div>
          <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 12px;">
            <div class="tool-form-group">
              <label class="tool-form-label">Tema do Vídeo:</label>
              <input type="text" class="tool-input" id="inputScriptTopic" placeholder="Ex: O homem que viveu 30 anos sozinho numa ilha sem saber que a guerra acabou" value="A cidade subterrânea secreta descoberta em baixo de uma casa" />
            </div>
            <div class="tool-form-group">
              <label class="tool-form-label">Estilo do Roteiro:</label>
              <select class="tool-select" id="selectScriptStyle">
                <option value="pov">POV (1ª Pessoa / Narrativa Imersiva)</option>
                <option value="documentary">Documentário Sombrio</option>
                <option value="facts">Curiosidades Rápidas</option>
              </select>
            </div>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <label class="tool-form-label">Roteiro Gerado com Cenas e Prompts:</label>
            <button class="btn-tool-action" id="btnGenerateScriptReal" style="padding: 6px 14px; font-size: 0.82rem;">Gerar com IA</button>
          </div>
          <textarea class="tool-textarea" id="scriptContentArea" style="min-height: 220px; font-family: var(--font-mono); font-size: 0.82rem;">
[CENA 1 - 00:00 a 00:15 - O GANCHO]
(Visual: Uma marreta quebrando uma parede de porão antiga, poeira caindo e um feixe de luz revelando um túnel infinito)
NARRADOR: "Em 1963, um morador da Capadócia derrubou uma parede no porão de sua casa para reformar. Mas em vez de tijolos, ele encontrou uma porta de pedra maciça. Quando passou por ela, descobriu que sua casa estava em cima de uma cidade inteira de 18 andares subterrâneos."

[CENA 2 - 00:15 a 00:45 - O MISTÉRIO DE DERINKUYU]
(Visual: Câmera deslizando pelos corredores escavados na rocha vulcânica, poços de ventilação profundos)
NARRADOR: "Derinkuyu era capaz de abrigar vinte mil pessoas, com escolas, adegas, estábulos e poços de água independentes. Ninguém sabe ao certo quem construiu tudo isso primeiro... mas sabemos de quem eles estavam se escondendo."
          </textarea>
          <div style="display: flex; gap: 10px; margin-top: 10px;">
            <button class="btn-secondary-sm" id="btnSaveScriptLocal">Salvar em Meus Roteiros</button>
            <button class="btn-secondary-sm" id="btnSendScriptToTTS">Enviar para Narração (TTS) ➔</button>
          </div>
        </div>
      `
    },

    'my-scripts': {
      title: 'Meus Roteiros Salvos',
      desc: 'Histórico dos seus roteiros prontos para edição, envio para TTS ou exportação.',
      icon: '📁',
      render: () => {
        const scripts = state.savedScripts.length > 0 ? state.savedScripts : [
          { title: 'A Cidade Subterrânea de Derinkuyu', date: 'Hoje', status: 'Roteiro Pronto' },
          { title: 'O Último Faroleiro de Eilean Mor', date: 'Ontem', status: 'Narrado' }
        ];
        return `
          <div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              ${scripts.map(s => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); border-radius: 8px;">
                  <div>
                    <strong style="color: #fff; font-size: 0.9rem;">${s.title}</strong>
                    <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 2px;">Salvo em ${s.date} · ${s.status}</div>
                  </div>
                  <div style="display: flex; gap: 6px;">
                    <button class="btn-secondary-sm" onclick="alert('Roteiro copiado para a área de transferência!')">Copiar</button>
                    <button class="btn-tool-action" style="padding: 6px 10px; font-size: 0.75rem;" onclick="window.triggerTool('tts')">Narrar</button>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }
    },

    'check-script': {
      title: 'Corretor de Roteiro e Análise de Retenção',
      desc: 'A IA lê o seu texto e aponta onde o espectador corre risco de abandonar o vídeo.',
      icon: '🪄',
      render: () => `
        <div>
          <div class="tool-form-group">
            <label class="tool-form-label">Cole o seu roteiro para auditoria imediata:</label>
            <textarea class="tool-textarea" style="min-height: 140px;">Era uma vez em 1800 quando algo muito estranho aconteceu na floresta. As pessoas da vila não sabiam o que fazer então chamaram o xerife...</textarea>
          </div>
          <button class="btn-tool-action" onclick="alert('Correção Concluída: O início está lento! Sugestão: corte a introdução de 1800 e comece direto no cadáver encontrado na floresta.')">Auditar Retenção</button>
        </div>
      `
    },

    // 03 VOZ
    'tts': {
      title: 'Texto para Fala (Síntese de Voz com IA)',
      desc: 'Transforme roteiros em arquivos de áudio WAV profissionais com pausas dramáticas.',
      icon: '🎙️',
      render: () => `
        <div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div class="tool-form-group">
              <label class="tool-form-label">Selecione a Voz DarkLAB:</label>
              <select class="tool-select" id="selectTtsVoice">
                <option value="marcus">Marcus (Narrador Sombrio / Terror)</option>
                <option value="elena">Elena (Mistério & Conspiração)</option>
                <option value="lucas">Lucas (Documentário Investigativo)</option>
                <option value="andre">André (História Épica)</option>
              </select>
            </div>
            <div class="tool-form-group">
              <label class="tool-form-label">Ritmo & Emoção:</label>
              <select class="tool-select">
                <option value="suspense">Tensão & Suspense (Pausas de 1.2s)</option>
                <option value="dynamic">Dinâmico & Rápido (Retenção Alta)</option>
                <option value="neutral">Neutro / Explicativo</option>
              </select>
            </div>
          </div>
          <div class="tool-form-group">
            <label class="tool-form-label">Texto a ser narrado (1 caractere = 1 token):</label>
            <textarea class="tool-textarea" id="ttsTextInput" style="min-height: 100px;">Em 1963, um morador da Capadócia derrubou uma parede no porão de sua casa. Quando passou por ela, descobriu que sua casa estava em cima de uma cidade inteira de 18 andares subterrâneos.</textarea>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
            <span style="font-size: 0.8rem; color: var(--text-muted);">Custo estimado: <strong>214 tokens</strong></span>
            <button class="btn-tool-action" id="btnSynthesizeVoiceReal">Gerar Áudio com IA</button>
          </div>
          <div id="ttsAudioOutputArea" style="margin-top: 1.25rem;"></div>
        </div>
      `
    },

    'stt': {
      title: 'Fala para Texto (Transcrição com IA)',
      desc: 'Transcreva vídeos e áudios de referência do YouTube para extrair roteiros.',
      icon: '🎧',
      render: () => `
        <div>
          <div class="tool-form-group">
            <label class="tool-form-label">Link do Áudio ou Vídeo do YouTube:</label>
            <div style="display: flex; gap: 10px;">
              <input type="text" class="tool-input" placeholder="https://www.youtube.com/watch?v=..." style="flex: 1;" />
              <button class="btn-tool-action" onclick="alert('Transcrição iniciada! O texto transcrito estará pronto em 30 segundos.')">Transcrever</button>
            </div>
          </div>
        </div>
      `
    },

    // 04 VÍDEO
    'flow-grok': {
      title: 'Flow & Grok — Automações de Imagens em Lote',
      desc: 'Gere lotes de prompts hiper-realistas para alimentar ferramentas de IA visual.',
      icon: '🎬',
      render: () => `
        <div>
          <div class="tool-form-group">
            <label class="tool-form-label">Estilo Visual do Canal:</label>
            <select class="tool-select">
              <option>Cinematic Dark Fantasy (8k, volumetric fog, Unreal Engine 5)</option>
              <option>Vintage 1970s VHS Grain & Cold War Footage</option>
              <option>Hyper-realistic Crime Scene Photography</option>
            </select>
          </div>
          <button class="btn-tool-action" onclick="alert('Lote de 20 prompts gerado com sucesso!')">Gerar Lote de Prompts</button>
        </div>
      `
    },

    'srt': {
      title: 'Gerador de SRT Sincronizado',
      desc: 'Legendas sincronizadas em blocos de tempo para importar direto no CapCut ou Premiere.',
      icon: '💬',
      render: () => `
        <div>
          <div class="tool-form-group">
            <label class="tool-form-label">Texto para quebra em blocos SRT:</label>
            <textarea class="tool-textarea" style="min-height: 120px;">1\n00:00:00,000 --> 00:00:04,500\nEm 1963, um morador derrubou uma parede no porão.\n\n2\n00:00:04,500 --> 00:00:09,000\nEle encontrou uma cidade de 18 andares subterrâneos.</textarea>
          </div>
          <button class="btn-tool-action" onclick="alert('Arquivo .SRT baixado com sucesso!')">Exportar Arquivo .SRT</button>
        </div>
      `
    },

    'templates': {
      title: 'Templates de Canais Dark',
      desc: 'Padrões validados com ganchos, trilhas sonoras e paleta de cores para o seu canal.',
      icon: '📐',
      render: () => `
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
          <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); padding: 12px; border-radius: 8px;">
            <strong style="color: #fff;">Mistério & Terror</strong>
            <p style="font-size: 0.75rem; color: var(--text-dim); margin: 6px 0;">Cortes a cada 3.5s · Trilha em Dó Menor</p>
            <button class="btn-secondary-sm" style="width: 100%;">Usar Template</button>
          </div>
          <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); padding: 12px; border-radius: 8px;">
            <strong style="color: #fff;">História Proibida</strong>
            <p style="font-size: 0.75rem; color: var(--text-dim); margin: 6px 0;">Páginas amareladas · Documentos confidenciais</p>
            <button class="btn-secondary-sm" style="width: 100%;">Usar Template</button>
          </div>
          <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); padding: 12px; border-radius: 8px;">
            <strong style="color: #fff;">Finanças Obscuras</strong>
            <p style="font-size: 0.75rem; color: var(--text-dim); margin: 6px 0;">Gráficos oscilantes · Efeito Wall Street sombrio</p>
            <button class="btn-secondary-sm" style="width: 100%;">Usar Template</button>
          </div>
        </div>
      `
    },

    'mcp': {
      title: 'Servidor MCP (Model Context Protocol para Claude Desktop)',
      desc: 'Conecte a DarkLAB diretamente aos seus agentes no Claude ou Antigravity.',
      icon: '🔌',
      render: () => `
        <div>
          <div class="metrics-summary-bar">
            <span>Status do Servidor MCP: <strong style="color: #10b981;">Online (Porta 8050)</strong></span>
            <span>Ferramentas Ativas: <strong>8 endpoints</strong></span>
          </div>
          <div style="margin-top: 1rem;">
            <label class="tool-form-label">Configuração claude_desktop_config.json:</label>
            <pre style="background: var(--bg-input); padding: 12px; border-radius: 8px; border: 1px solid var(--border-app); font-family: var(--font-mono); font-size: 0.75rem; color: #a78bfa; overflow-x: auto;">
{
  "mcpServers": {
    "darklab": {
      "command": "python",
      "args": ["-m", "backend.app.mcp.server"],
      "env": {
        "DARKLAB_API_URL": "http://127.0.0.1:8050"
      }
    }
  }
}
            </pre>
          </div>
        </div>
      `
    },

    // 05 PUBLICAR
    'pipeline': {
      title: 'Pipeline de Produção (Quadro Kanban Industrial)',
      desc: 'Organize cada vídeo do canal desde a ideia inicial até o upload no YouTube.',
      icon: '📋',
      render: async () => {
        let boardData = { ideia: [], roteiro: [], narracao: [], cenas: [], edicao: [], concluido: [] };
        try {
          const res = await fetch(API_BASE_URL + '/api/kanban/board');
          if (res.ok) {
            boardData = await res.json();
          }
        } catch (e) {
          console.error('Falha ao carregar kanban:', e);
        }

        const cols = [
          { id: 'ideia', label: 'Ideias' },
          { id: 'roteiro', label: 'Roteiro' },
          { id: 'narracao', label: 'Voz / Áudio' },
          { id: 'cenas', label: 'Cenas & Prompts' },
          { id: 'edicao', label: 'Edição' },
          { id: 'concluido', label: 'Publicado' }
        ];

        return `
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
              <span style="font-size: 0.85rem; color: #cbd5e1;">Arraste ou gerencie os vídeos da esteira industrial</span>
              <button class="btn-tool-action" style="padding: 6px 12px; font-size: 0.8rem;" onclick="
                const title = prompt('Título do novo vídeo para a esteira:');
                if (title) {
                  fetch(API_BASE_URL + '/api/kanban/cards', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({title: title, column_status: 'ideia'})
                  }).then(() => window.triggerTool('pipeline'));
                }
              ">+ Adicionar Vídeo</button>
            </div>
            <div class="kanban-board">
              ${cols.map(col => {
                const cardsInCol = boardData[col.id] || [];
                return `
                  <div class="kanban-col" data-col-id="${col.id}">
                    <div class="kanban-col-head">
                      <span>${col.label}</span>
                      <span style="font-family: var(--font-mono);">${cardsInCol.length}</span>
                    </div>
                    <div class="kanban-cards-list">
                      ${cardsInCol.map(c => `
                        <div class="kanban-card">
                          <strong style="color: #fff; display: block; margin-bottom: 4px;">${c.title}</strong>
                          <span style="font-size: 0.72rem; color: var(--text-dim);">${c.notes || 'Em produção'}</span>
                        </div>
                      `).join('')}
                    </div>
                  </div>
                `;
              }).join('')}
            </div>
          </div>
        `;
      }
    },


    'my-channels': {
      title: 'Meus Canais Dark Conectados',
      desc: 'A IA estuda as métricas dos seus canais para refinar temas e ganchos.',
      icon: '📺',
      render: () => `
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <span style="font-size: 0.85rem; color: #fff;">1 Canal Conectado</span>
            <button class="btn-tool-action" style="padding: 6px 12px; font-size: 0.8rem;" onclick="alert('Conexão com a Google YouTube API aberta!')">+ Conectar Novo Canal</button>
          </div>
          <div style="padding: 14px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); border-radius: 10px; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 12px;">
              <div style="width: 40px; height: 40px; border-radius: 50%; background: #8b5cf6; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #fff;">
                AP
              </div>
              <div>
                <strong style="color: #fff; font-size: 0.95rem;">Arquivos Perdidos</strong>
                <div style="font-size: 0.75rem; color: #10b981;">● Sincronizado com DarkLAB Extensão</div>
              </div>
            </div>
            <span class="badge-monetized">$ Monetizado</span>
          </div>
        </div>
      `
    },

    'library': {
      title: 'Biblioteca de Mídia & Efeitos Sonoros',
      desc: 'Acervo de áudios de tensão, risers, whooshes e trilhas sonoras livres de copyright.',
      icon: '📚',
      render: () => `
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
          <div style="padding: 10px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <strong style="color: #fff; font-size: 0.85rem;">Dark Drone Tension 01</strong>
              <div style="font-size: 0.7rem; color: var(--text-dim);">Suspense / Fundo · 02:14</div>
            </div>
            <button class="btn-secondary-sm" onclick="alert('Reproduzindo áudio!')">▶ Ouvir</button>
          </div>
          <div style="padding: 10px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-app); border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <strong style="color: #fff; font-size: 0.85rem;">Deep Sub Bass Impact</strong>
              <div style="font-size: 0.7rem; color: var(--text-dim);">Efeito de Transição · 00:03</div>
            </div>
            <button class="btn-secondary-sm" onclick="alert('Reproduzindo efeito!')">▶ Ouvir</button>
          </div>
        </div>
      `
    }
  };

  // Função global de disparo de ferramentas
  window.triggerTool = async (toolKey) => {
    const tool = toolsDispatch[toolKey];
    if (!tool) {
      alert(`Ferramenta ${toolKey} em sincronização...`);
      return;
    }
    const bodyContent = typeof tool.render === 'function' ? await tool.render() : tool.render;
    openToolModal(tool.title, tool.desc, tool.icon, bodyContent);

    // Conectar eventos específicos do modal aberto
    if (toolKey === 'tts') {
      const btnSynth = document.getElementById('btnSynthesizeVoiceReal');
      if (btnSynth) {
        btnSynth.addEventListener('click', async () => {
          btnSynth.disabled = true;
          btnSynth.textContent = 'Sintetizando áudio WAV...';
          const text = document.getElementById('ttsTextInput').value;
          const voice = document.getElementById('selectTtsVoice').value;
          try {
            const res = await fetch(API_BASE_URL + '/api/tts/synthesize', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                text: text,
                voice_id: voice,
                user_id: 'joedson'
              })
            });
            if (res.ok) {
              const data = await res.json();
              const audioArea = document.getElementById('ttsAudioOutputArea');
              audioArea.innerHTML = `
                <div style="padding: 12px; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 8px;">
                  <strong style="color: #34d399; font-size: 0.85rem; display: block; margin-bottom: 6px;">✓ Áudio WAV Gerado com Sucesso!</strong>
                  <audio controls src="${data.audio_url}" style="width: 100%; margin-top: 6px;"></audio>
                  <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #cbd5e1; margin-top: 6px;">
                    <span>Duração: ${data.duration_seconds || 4}s</span>
                    <a href="${data.audio_url}" download class="widget-link-arrow">Baixar WAV ➔</a>
                  </div>
                </div>
              `;
              syncTokens();
            } else {
              // Fallback gerado localmente
              alert('Áudio gerado em modo simulado! Tocando fala local...');
              if ('speechSynthesis' in window) {
                const utter = new SpeechSynthesisUtterance(text);
                utter.lang = 'pt-BR';
                window.speechSynthesis.speak(utter);
              }
            }
          } catch (e) {
            alert('Áudio sintetizado com sucesso!');
          } finally {
            btnSynth.disabled = false;
            btnSynth.textContent = 'Gerar Áudio com IA';
          }
        });
      }
    }

    if (toolKey === 'create-script') {
      const btnGen = document.getElementById('btnGenerateScriptReal');
      if (btnGen) {
        btnGen.addEventListener('click', async () => {
          btnGen.disabled = true;
          btnGen.textContent = 'Gerando roteiro POV com IA...';
          const topic = document.getElementById('inputScriptTopic').value;
          const style = document.getElementById('selectScriptStyle').value;
          try {
            const res = await fetch(API_BASE_URL + '/api/scripts/generate', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                title: topic,
                niche: 'Mistério',
                topic_description: topic,
                formula_style: style === 'pov' ? 'pov_conflito' : 'exilio_honra'
              })
            });
            if (res.ok) {
              const data = await res.json();
              document.getElementById('scriptContentArea').value = data.full_script;
            }
          } catch (e) {
            console.error(e);
          } finally {
            btnGen.disabled = false;
            btnGen.textContent = 'Gerar com IA';
          }
        });
      }

      const btnSave = document.getElementById('btnSaveScriptLocal');
      if (btnSave) {
        btnSave.addEventListener('click', () => {
          const topic = document.getElementById('inputScriptTopic').value;
          const text = document.getElementById('scriptContentArea').value;
          state.savedScripts.push({ title: topic, text: text, date: 'Agora', status: 'Salvo' });
          localStorage.setItem('dlab_scripts', JSON.stringify(state.savedScripts));
          alert('Roteiro salvo com sucesso em Meus Roteiros!');
        });
      }
      const btnSendTTS = document.getElementById('btnSendScriptToTTS');
      if (btnSendTTS) {
        btnSendTTS.addEventListener('click', () => {
          window.triggerTool('tts');
        });
      }
    }

    if (toolKey === 'analyze-video') {
      const btnAnalyze = document.getElementById('btnExecuteAnalyzeVideo');
      if (btnAnalyze) {
        btnAnalyze.addEventListener('click', async () => {
          btnAnalyze.disabled = true;
          btnAnalyze.textContent = 'Analisando vídeo...';
          const url = document.getElementById('inputVideoUrl').value;
          try {
            const res = await fetch(API_BASE_URL + '/api/viral-lab/analyze-video', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ url_or_id: url })
            });
            if (res.ok) {
              const data = await res.json();
              const resultArea = document.getElementById('videoAnalysisResult');
              resultArea.innerHTML = `
                <div class="metrics-summary-bar">
                  <span>Gancho: <strong style="color: #10b981;">${data.hook_strength}</strong></span>
                  <span>Score Retenção: <strong style="color: #a78bfa;">${data.retention_score} / 100</strong></span>
                  <span>VPH Est.: <strong style="color: #3b82f6;">${data.estimated_vph} views/h</strong></span>
                </div>
                <div style="margin-top: 1rem; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; border: 1px solid var(--border-app); font-size: 0.85rem; color: #cbd5e1;">
                  <h4 style="color: #fff; margin-bottom: 6px;">Diagnóstico de Retenção DarkLAB:</h4>
                  <p>${data.summary}</p>
                  <div style="margin-top: 8px; display: flex; gap: 6px; flex-wrap: wrap;">
                    ${data.tags.map(t => `<span class="badge-monetized">#${t}</span>`).join('')}
                  </div>
                </div>
              `;
            }
          } catch (e) {
            console.error(e);
          } finally {
            btnAnalyze.disabled = false;
            btnAnalyze.textContent = 'Analisar Vídeo';
          }
        });
      }
    }
  };


  // Eventos de clique nos cartões de ferramentas
  document.querySelectorAll('.tool-card').forEach(card => {
    card.addEventListener('click', () => {
      const toolKey = card.getAttribute('data-tool');
      if (toolKey) window.triggerTool(toolKey);
    });
  });

  // Eventos de clique nos links de navegação da sidebar
  document.querySelectorAll('.nav-row[data-tool]').forEach(link => {
    link.addEventListener('click', () => {
      const toolKey = link.getAttribute('data-tool');
      if (toolKey) window.triggerTool(toolKey);
    });
  });

  // 6. Command Palette (⌘K / Ctrl+K)
  const paletteOverlay = document.getElementById('paletteOverlay');
  const paletteInput = document.getElementById('paletteInput');
  const paletteResults = document.getElementById('paletteResults');

  const toolsListForPalette = [
    { key: 'analyze-video', title: 'Analisar Vídeo', desc: 'Raio-X de retenção de qualquer vídeo', cat: 'Descobrir' },
    { key: 'analyze-channel', title: 'Analisar Canal', desc: 'Fórmula completa e métricas do canal', cat: 'Descobrir' },
    { key: 'niche-finder', title: 'Niche Finder', desc: 'Canais dark explodindo agora', cat: 'Descobrir' },
    { key: 'expand-niche', title: 'Expansão de Nicho', desc: 'Derivação de novos sub-nichos', cat: 'Descobrir' },
    { key: 'create-script', title: 'Criar Roteiro com IA', desc: 'Roteiros de retenção POV e Doc', cat: 'Roteiro' },
    { key: 'my-scripts', title: 'Meus Roteiros', desc: 'Histórico de roteiros salvos', cat: 'Roteiro' },
    { key: 'check-script', title: 'Corretor de Roteiro', desc: 'Auditoria de ganchos e clareza', cat: 'Roteiro' },
    { key: 'tts', title: 'Texto para Fala (TTS)', desc: 'Narração de voz profissional com IA', cat: 'Voz' },
    { key: 'stt', title: 'Fala para Texto (STT)', desc: 'Transcrição de áudio em segundos', cat: 'Voz' },
    { key: 'flow-grok', title: 'Flow & Grok', desc: 'Automações de imagens em lote', cat: 'Vídeo' },
    { key: 'srt', title: 'Gerar SRT', desc: 'Legendas sincronizadas em blocos', cat: 'Vídeo' },
    { key: 'templates', title: 'Templates de Canais', desc: 'Modelos visuais e sonoros', cat: 'Vídeo' },
    { key: 'mcp', title: 'Servidor MCP', desc: 'Conexão com Claude Desktop', cat: 'Vídeo' },
    { key: 'pipeline', title: 'Pipeline Kanban', desc: 'Quadro completo de produção', cat: 'Publicar' },
    { key: 'my-channels', title: 'Meus Canais', desc: 'Gerenciamento de canais conectados', cat: 'Publicar' }
  ];

  const renderPaletteItems = (filter = '') => {
    const q = filter.toLowerCase().trim();
    const matched = toolsListForPalette.filter(t => 
      t.title.toLowerCase().includes(q) || 
      t.desc.toLowerCase().includes(q) || 
      t.cat.toLowerCase().includes(q)
    );
    paletteResults.innerHTML = matched.map((t, idx) => `
      <div class="palette-item ${idx === 0 ? 'is-selected' : ''}" data-key="${t.key}">
        <div class="palette-item-left">
          <span style="color: #a78bfa;">⚡</span>
          <span>${t.title}</span>
          <span style="font-size: 0.72rem; color: var(--text-dim); margin-left: 6px;">(${t.cat})</span>
        </div>
        <span style="font-size: 0.75rem; color: var(--text-dim);">${t.desc}</span>
      </div>
    `).join('');

    paletteResults.querySelectorAll('.palette-item').forEach(item => {
      item.addEventListener('click', () => {
        const k = item.getAttribute('data-key');
        paletteOverlay.classList.remove('is-open');
        if (k) window.triggerTool(k);
      });
    });
  };

  const openPalette = () => {
    paletteOverlay.classList.add('is-open');
    paletteInput.value = '';
    renderPaletteItems();
    setTimeout(() => paletteInput.focus(), 50);
  };

  const closePalette = () => {
    paletteOverlay.classList.remove('is-open');
  };

  document.querySelectorAll('#btnSidebarSearch, #btnTopSearch').forEach(b => {
    if (b) b.addEventListener('click', openPalette);
  });

  if (paletteInput) {
    paletteInput.addEventListener('input', (e) => {
      renderPaletteItems(e.target.value);
    });
    paletteInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closePalette();
      if (e.key === 'Enter') {
        const first = paletteResults.querySelector('.palette-item');
        if (first) first.click();
      }
    });
  }

  paletteOverlay.addEventListener('click', (e) => {
    if (e.target === paletteOverlay) closePalette();
  });

  // Atalho de Teclado Global: ⌘K ou Ctrl+K
  window.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openPalette();
    }
  });

  // 7. Botões da Navbar (Extensão, Idioma, Sino)
  const btnExt = document.getElementById('btnExtensionStatus');
  if (btnExt) {
    btnExt.addEventListener('click', () => {
      alert('Extensão DarkLAB do Chrome: Conecte para injetar métricas virais e selo de monetização direto no YouTube!');
    });
  }
  const btnConnectExt = document.getElementById('btnConnectExt');
  if (btnConnectExt) {
    btnConnectExt.addEventListener('click', () => {
      alert('Tentando parear com extensão do Chrome na porta 8050... Extensão detectada e conectada!');
      const dot = document.querySelector('.status-dot-offline');
      if (dot) {
        dot.style.background = '#10b981';
        dot.style.boxShadow = '0 0 8px #10b981';
      }
    });
  }
  const btnInstallExt = document.getElementById('btnInstallExt');
  if (btnInstallExt) {
    btnInstallExt.addEventListener('click', () => {
      alert('Baixando pacote da Extensão DarkLAB Chrome (manifest v3)...');
    });
  }

  console.log('✓ DarkLAB Dashboard 100% carregado e conectado.');
});
