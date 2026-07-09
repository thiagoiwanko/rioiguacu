const $ = (id) => document.getElementById(id);

const fmt = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 3,
  maximumFractionDigits: 3,
});

const fmt1 = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const state = {
  loading: false,
  data: null,
};

function parseDate(value) {
  return new Date(value);
}

function formatDateTime(value) {
  const d = parseDate(value);
  return d.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatTime(value) {
  return parseDate(value).toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

const NIVEL_MAX_ESCALA = 5.5;

function colorForLevel(level) {
  const stops = [
    [0, [21, 108, 255]],
    [NIVEL_MAX_ESCALA * 0.25, [32, 231, 224]],
    [NIVEL_MAX_ESCALA * 0.42, [40, 244, 94]],
    [NIVEL_MAX_ESCALA * 0.67, [255, 236, 63]],
    [NIVEL_MAX_ESCALA * 0.84, [255, 156, 40]],
    [NIVEL_MAX_ESCALA, [255, 48, 48]],
  ];
  const value = Math.max(0, Math.min(NIVEL_MAX_ESCALA, level));
  for (let i = 0; i < stops.length - 1; i++) {
    const [a, ca] = stops[i];
    const [b, cb] = stops[i + 1];
    if (value >= a && value <= b) {
      const t = (value - a) / (b - a || 1);
      const rgb = ca.map((v, idx) => Math.round(v + (cb[idx] - v) * t));
      return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
    }
  }
  return "rgb(255,48,48)";
}

function allReferences(data) {
  const map = new Map();
  data.cotas_bairros.forEach((item) => map.set(Number(item.nivel), item.descricao));
  data.cotas_alerta.forEach((item) => map.set(Number(item.nivel), item.descricao));
  return [...map.entries()].map(([nivel, descricao]) => ({ nivel, descricao })).sort((a, b) => a.nivel - b.nivel);
}

function nearestReferenceLabels(data, currentLevel) {
  const refs = allReferences(data);
  const below = refs.filter((item) => item.nivel <= currentLevel).at(-1);
  const above = refs.find((item) => item.nivel >= currentLevel);
  const selected = new Map();
  if (below) selected.set(below.nivel, below);
  if (above) selected.set(above.nivel, above);
  if (selected.size === 1) {
    const only = [...selected.values()][0];
    const nextAbove = refs.find((item) => item.nivel > only.nivel);
    const nextBelow = refs.filter((item) => item.nivel < only.nivel).at(-1);
    if (nextAbove) selected.set(nextAbove.nivel, nextAbove);
    else if (nextBelow) selected.set(nextBelow.nivel, nextBelow);
  }
  return selected;
}

function chartBounds(data) {
  const currentLevel = data.ultima.regua_m;
  const hist = data.historico.map((d) => d.regua_m);
  const forecast = data.previsao
    .map((d) => d.regua_com_chuva_m)
    .filter((v) => typeof v === "number");
  const values = [...hist, ...forecast, currentLevel];
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);

  // Distância mínima necessária para a linha inteira caber no gráfico.
  const distAcimaDados = Math.max(maxValue - currentLevel, 0);
  const distAbaixoDados = Math.max(currentLevel - minValue, 0);

  // Reserva espaço para pelo menos as duas próximas cotas de ALERTA (não
  // cotas históricas distantes, como recordes de estiagem ou enchentes
  // antigas) acima e abaixo do nível atual, para dar contexto sem esticar
  // demais a escala vertical e achatar a variação real do gráfico.
  const refs = data.cotas_alerta.map((item) => Number(item.nivel));
  const refsAcima = refs.filter((v) => v > currentLevel).sort((a, b) => a - b);
  const refsAbaixo = refs.filter((v) => v < currentLevel).sort((a, b) => b - a);
  const folgaRefAcima = refsAcima.length
    ? refsAcima[Math.min(1, refsAcima.length - 1)] - currentLevel
    : 1;
  const folgaRefAbaixo = refsAbaixo.length
    ? currentLevel - refsAbaixo[Math.min(1, refsAbaixo.length - 1)]
    : 1;

  let halfSpan = Math.max(distAcimaDados, distAbaixoDados, folgaRefAcima, folgaRefAbaixo, 0.6) + 0.3;

  let minY = currentLevel - halfSpan;
  let maxY = currentLevel + halfSpan;

  if (minY < 0) {
    // Régua não é negativa: em vez de cortar embaixo, empurra a folga para cima
    // (o nível atual deixa de ficar exatamente no centro só quando está bem perto de zero).
    maxY += -minY;
    minY = 0;
  }

  return { minY, maxY };
}

function severityClass(situacao) {
  const texto = situacao || "";
  if (texto.startsWith("ALERTA CRÍTICO")) return "badge-critico";
  if (texto.startsWith("ATENÇÃO MUITO ALTA")) return "badge-muito-alta";
  if (texto.startsWith("ATENÇÃO ALTA")) return "badge-alta";
  if (texto.startsWith("ATENÇÃO MODERADA")) return "badge-moderada";
  return "badge-normal";
}

function renderCards(data) {
  const last = data.ultima;
  const level = Number(last.regua_m);
  $("lastTime").textContent = formatDateTime(last.data_hora);
  $("levelValue").textContent = `${fmt.format(level)} m`;

  const badgeClass = severityClass(data.situacao);
  const levelBadge = $("levelBadge");
  levelBadge.className = `level-badge ${badgeClass}`;
  levelBadge.innerHTML = badgeClass === "badge-critico"
    ? `<i class="siren-dot"></i>${data.situacao}`
    : data.situacao;

  $("situationText").textContent = `Situação do rio: ${data.situacao}`;
  $("flowValue").textContent = `${last.vazao_m3s} m³/s`;
  $("rainValue").textContent = `${fmt1.format(last.chuva_mm)} mm`;
  $("rainAccum").textContent = `acumulada ${fmt1.format(last.chuva_acumulada_mm)} mm`;
  $("trendValue").textContent = data.tendencia.texto;
  $("forecastAlert").textContent = data.alerta_previsao;
  $("forecastAlert").className = data.previsao_disponivel ? "" : "warning";
  $("sourceLink").href = data.url_historico || "#";
  const fonteCurta = (data.fonte || "").split(/[–-]/)[0].trim();
  $("sourceLabel").textContent = fonteCurta ? `(${fonteCurta})` : "";

  const marker = Math.max(0, Math.min(100, (level / NIVEL_MAX_ESCALA) * 100));
  $("gaugeMarker").style.left = `calc(${marker}% - 2px)`;
  $("levelValue").style.color = colorForLevel(level);
}

function renderReferences(data) {
  const currentLevel = data.ultima.regua_m;
  const referencias = data.cotas_bairros
    .map((item) => ({ ...item, isCurrent: false }))
    .concat([{ nivel: currentLevel, descricao: "", isCurrent: true }])
    .sort((a, b) => b.nivel - a.nivel);

  $("referenceList").innerHTML = referencias
    .map((item) => {
      if (item.isCurrent) {
        return `
          <div class="ref-row ref-row-current">
            <i class="swatch current-dot" style="color:${colorForLevel(item.nivel)}; background:${colorForLevel(item.nivel)}"></i>
            <strong>${item.nivel.toFixed(2)} m</strong>
            <span>🡒 O rio está aqui agora!</span>
          </div>
        `;
      }
      return `
        <div class="ref-row">
          <i class="swatch" style="color:${colorForLevel(item.nivel)}; background:${colorForLevel(item.nivel)}"></i>
          <strong>${item.nivel.toFixed(2)} m</strong>
          <span>${item.descricao}</span>
        </div>
      `;
    }).join("");

  $("alertList").innerHTML = data.cotas_alerta
    .slice()
    .sort((a, b) => b.nivel - a.nivel)
    .map((item) => `
      <div class="alert-row">
        <i class="alert-icon" style="background:${colorForLevel(item.nivel)}">!</i>
        <strong>${item.nivel.toFixed(2)} m</strong>
        <span>${item.descricao}</span>
      </div>
    `).join("");
}

function renderTable(data) {
  $("dataRows").innerHTML = data.historico
    .slice()
    .reverse()
    .map((item) => `
      <tr>
        <td>${formatDateTime(item.data_hora)}</td>
        <td>${fmt.format(item.regua_m)} m</td>
        <td>${item.vazao_m3s} m³/s</td>
        <td>${fmt1.format(item.chuva_mm)} mm</td>
        <td>${fmt1.format(item.chuva_acumulada_mm)} mm</td>
      </tr>
    `).join("");
}

function makePath(points, x, y) {
  return points.map((p, idx) => `${idx ? "L" : "M"} ${x(parseDate(p.data_hora))} ${y(p.value)}`).join(" ");
}

function renderChart(data) {
  const el = $("chart");
  const containerWidth = el.clientWidth || 900;
  const isNarrow = containerWidth < 640;
  const width = isNarrow ? Math.max(280, containerWidth) : Math.max(760, containerWidth);
  const height = isNarrow ? Math.round(Math.min(360, Math.max(300, width * 0.92))) : 485;
  // Painel pequeno de precipitação, anexado abaixo do gráfico principal (mesmo eixo X).
  const rain = isNarrow
    ? { gap: 10, titleH: 14, barsH: 50, marginBottom: 6 }
    : { gap: 14, titleH: 16, barsH: 70, marginBottom: 8 };
  const rainExtra = rain.gap + rain.titleH + rain.barsH + rain.marginBottom;
  const totalHeight = height + rainExtra;
  el.style.height = `${totalHeight}px`;
  const pad = isNarrow
    ? { left: 40, right: 10, top: 18, bottom: 36 }
    : { left: 58, right: 28, top: 28, bottom: 50 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;
  const rainSectionTop = height + rain.gap;
  const rainTitleY = rainSectionTop + (isNarrow ? 10 : 12);
  const rainPlotTop = rainSectionTop + rain.titleH;
  const rainPlotBottom = rainPlotTop + rain.barsH;
  const fs = isNarrow ? { tick: 10, tickSmall: 9, label: 10, refLabel: 10, refNum: 8, current: 10, axisTitle: 10 }
    : { tick: 12, tickSmall: 11, label: 12, refLabel: 12, refNum: 9, current: 11, axisTitle: 12 };
  const labelBoxWidth = isNarrow ? Math.max(150, width - pad.left - pad.right - 20) : 320;
  const lastTime = parseDate(data.ultima.data_hora);
  const start = new Date(lastTime.getTime() - data.janela_historico_horas * 3600 * 1000);
  const forecastEnd = data.previsao.length
    ? parseDate(data.previsao.at(-1).data_hora)
    : new Date(lastTime.getTime() + 24 * 3600 * 1000);
  const end = new Date(Math.max(start.getTime() + 48 * 3600 * 1000, forecastEnd.getTime() + 2 * 3600 * 1000));
  const { minY, maxY } = chartBounds(data);

  const x = (d) => pad.left + ((d.getTime() - start.getTime()) / (end.getTime() - start.getTime())) * plotW;
  const y = (v) => pad.top + (1 - ((v - minY) / (maxY - minY))) * plotH;
  const refs = allReferences(data).filter((item) => item.nivel >= minY && item.nivel <= maxY);
  const labels = nearestReferenceLabels(data, data.ultima.regua_m);

  // Evita sobreposição de caixas de legenda quando duas cotas de referência
  // estão muito próximas em altura (ex.: 4.30 m e 4.50 m).
  const labelBoxHeight = 20;
  const labelPositions = new Map();
  const sortedLabels = [...labels.values()].sort((a, b) => y(a.nivel) - y(b.nivel));
  let previousLabelY = null;
  sortedLabels.forEach((item) => {
    let labelY = y(item.nivel);
    if (previousLabelY !== null && labelY - previousLabelY < labelBoxHeight) {
      labelY = previousLabelY + labelBoxHeight;
    }
    labelPositions.set(item.nivel, labelY);
    previousLabelY = labelY;
  });

  const histPoints = data.historico
    .map((item) => ({ ...item, value: item.regua_m }))
    .filter((item) => parseDate(item.data_hora) >= start && parseDate(item.data_hora) <= end);

  const wetPoints = [
    { data_hora: data.ultima.data_hora, value: data.ultima.regua_m },
    ...data.previsao.filter((item) => item.regua_com_chuva_m !== null).map((item) => ({ data_hora: item.data_hora, value: item.regua_com_chuva_m })),
  ];

  const yTicks = Array.from({ length: 6 }, (_, i) => minY + ((maxY - minY) / 5) * i);
  const xTicks = Array.from({ length: 5 }, (_, i) => new Date(start.getTime() + ((end.getTime() - start.getTime()) / 4) * i));

  // Barras de precipitação horária (mm), mesma janela de tempo do histórico.
  const rainPoints = histPoints.filter((item) => typeof item.chuva_mm === "number");
  const rainMaxRaw = rainPoints.length ? Math.max(...rainPoints.map((p) => p.chuva_mm)) : 0;
  const rainMax = Math.max(5, rainMaxRaw * 1.15);
  const oneHourPx = plotW * (3600 * 1000) / (end.getTime() - start.getTime());
  const rainBarW = Math.max(2, Math.min(14, oneHourPx * 0.55));
  const rainBarY = (mm) => rainPlotBottom - (Math.max(0, mm) / rainMax) * rain.barsH;
  const rainTicks = [0, rainMax];

  el.innerHTML = `
    <svg viewBox="0 0 ${width} ${totalHeight}" role="img" aria-label="Gráfico da cota do Rio Iguaçu e precipitação">
      <defs>
        <linearGradient id="waterLine" x1="0" x2="1">
          <stop offset="0%" stop-color="#18d9d2"/>
          <stop offset="55%" stop-color="#39f46b"/>
          <stop offset="100%" stop-color="#ffdf4a"/>
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      <rect x="${pad.left}" y="${pad.top}" width="${plotW}" height="${plotH}" rx="8" fill="rgba(217,255,238,.045)" stroke="rgba(180,215,230,.18)"/>
      ${yTicks.map((tick) => `
        <line x1="${pad.left}" x2="${width - pad.right}" y1="${y(tick)}" y2="${y(tick)}" stroke="rgba(180,215,230,.12)" stroke-dasharray="2 5"/>
        <text x="${pad.left - (isNarrow ? 8 : 12)}" y="${y(tick) + 4}" text-anchor="end" fill="#8aa3b0" font-size="${fs.tick}">${tick.toFixed(2)}</text>
      `).join("")}
      ${xTicks.map((tick) => `
        <line x1="${x(tick)}" x2="${x(tick)}" y1="${pad.top}" y2="${rainPlotBottom}" stroke="rgba(180,215,230,.10)" stroke-dasharray="2 5"/>
        <text x="${x(tick)}" y="${height - (isNarrow ? 18 : 22)}" text-anchor="middle" fill="#8aa3b0" font-size="${fs.tick}">${tick.toLocaleDateString("pt-BR", {day: "2-digit", month: "2-digit"})}</text>
        <text x="${x(tick)}" y="${height - (isNarrow ? 5 : 8)}" text-anchor="middle" fill="#6f8795" font-size="${fs.tickSmall}">${tick.toLocaleTimeString("pt-BR", {hour: "2-digit", minute: "2-digit"})}</text>
      `).join("")}
      ${refs.map((item) => {
        const isAlert = data.cotas_alerta.some((alert) => Number(alert.nivel) === item.nivel);
        const label = labels.get(item.nivel);
        const labelY = labelPositions.get(item.nivel);
        return `
          <line x1="${pad.left}" x2="${width - pad.right}" y1="${y(item.nivel)}" y2="${y(item.nivel)}" stroke="${colorForLevel(item.nivel)}" stroke-width="${isAlert ? 2 : 1.2}" stroke-dasharray="${isAlert ? "3 5" : "8 5"}" opacity=".95"/>
          ${label ? `
            <g>
              <rect x="${pad.left + 8}" y="${labelY - 19}" width="${labelBoxWidth}" height="18" rx="5" fill="rgba(8,16,22,.78)" stroke="rgba(255,255,255,.10)"/>
              <text x="${pad.left + 16}" y="${labelY - 6}" fill="${isAlert ? "#eef7fb" : colorForLevel(item.nivel)}" font-size="${fs.refLabel}" font-weight="800">${item.nivel.toFixed(2)} m - ${label.descricao}</text>
            </g>
          ` : `
            <text x="${width - pad.right - 5}" y="${y(item.nivel) - 3}" text-anchor="end" fill="${colorForLevel(item.nivel)}" font-size="${fs.refNum}" opacity=".8">${item.nivel.toFixed(2)}</text>
          `}
        `;
      }).join("")}
      ${wetPoints.length > 1 ? `<path d="${makePath(wetPoints, x, y)}" fill="none" stroke="#ff3d42" stroke-width="2.4" stroke-dasharray="8 7" opacity=".95"/>` : ""}
      <path d="${makePath(histPoints, x, y)}" fill="none" stroke="url(#waterLine)" stroke-width="4" stroke-linecap="round" filter="url(#glow)"/>
      ${histPoints.slice(0, -1).map((p) => `<circle cx="${x(parseDate(p.data_hora))}" cy="${y(p.value)}" r="3" fill="#18d9d2" stroke="#071019" stroke-width="1.5"/>`).join("")}
      ${histPoints.length ? (() => {
        const last = histPoints[histPoints.length - 1];
        const cx = x(parseDate(last.data_hora));
        const cy = y(last.value);
        const color = colorForLevel(last.value);
        const labelY = Math.min(cy + (isNarrow ? 18 : 22), height - pad.bottom - 6);
        return `
          <circle class="current-point-ring" cx="${cx}" cy="${cy}" r="5" fill="none" stroke="${color}" stroke-width="2"/>
          <circle class="current-point-dot" cx="${cx}" cy="${cy}" r="5" fill="${color}" stroke="#071019" stroke-width="1.5"/>
          <text class="current-point-label" x="${cx}" y="${labelY}" text-anchor="middle" fill="#eef7fb" font-size="${fs.current}" font-weight="800">Cota atual</text>
        `;
      })() : ""}
      ${wetPoints.slice(1).map((p) => `<circle cx="${x(parseDate(p.data_hora))}" cy="${y(p.value)}" r="4" fill="#ff3d42"/>`).join("")}
      <text x="${pad.left}" y="${isNarrow ? 14 : 18}" fill="#9fb4c1" font-size="${fs.axisTitle}">Leitura da régua (m)</text>
      ${histPoints.map((p, idx) => `<circle class="chart-hit" cx="${x(parseDate(p.data_hora))}" cy="${y(p.value)}" r="10" fill="rgba(0,0,0,0.001)" pointer-events="all" data-cota="${fmt.format(p.value)}" data-time="${formatDateTime(p.data_hora)}" data-kind="${idx === histPoints.length - 1 ? "Cota atual" : "Histórico"}"/>`).join("")}
      ${wetPoints.slice(1).map((p) => `<circle class="chart-hit" cx="${x(parseDate(p.data_hora))}" cy="${y(p.value)}" r="10" fill="rgba(0,0,0,0.001)" pointer-events="all" data-cota="${fmt.format(p.value)}" data-time="${formatDateTime(p.data_hora)}" data-kind="Previsão"/>`).join("")}
      <rect x="${pad.left}" y="${rainPlotTop}" width="${plotW}" height="${rain.barsH}" rx="6" fill="rgba(72,167,255,.05)" stroke="rgba(180,215,230,.14)"/>
      <text x="${pad.left}" y="${rainTitleY}" fill="#9fb4c1" font-size="${fs.axisTitle}">Chuva (mm)</text>
      ${rainTicks.map((tick) => `
        <text x="${pad.left - (isNarrow ? 8 : 12)}" y="${rainBarY(tick) + 3}" text-anchor="end" fill="#8aa3b0" font-size="${fs.tick}">${tick.toFixed(tick === 0 ? 0 : 1)}</text>
      `).join("")}
      ${rainPoints.map((p) => {
        const cx = x(parseDate(p.data_hora));
        const barTop = rainBarY(p.chuva_mm);
        const barH = Math.max(0, rainPlotBottom - barTop);
        return `<rect x="${cx - rainBarW / 2}" y="${barTop}" width="${rainBarW}" height="${barH}" rx="1.5" fill="rgba(72,167,255,.85)" stroke="rgba(255,255,255,.15)"/>`;
      }).join("")}
      ${rainPoints.map((p) => `<rect class="chart-hit" x="${x(parseDate(p.data_hora)) - Math.max(rainBarW, 10) / 2}" y="${rainPlotTop}" width="${Math.max(rainBarW, 10)}" height="${rain.barsH}" fill="rgba(0,0,0,0.001)" pointer-events="all" data-cota="${fmt1.format(p.chuva_mm)}" data-time="${formatDateTime(p.data_hora)}" data-kind="Chuva horária" data-unit="mm"/>`).join("")}
    </svg>
  `;
}

function renderAll(data) {
  renderCards(data);
  renderReferences(data);
  renderTable(data);
  renderChart(data);
}

async function refresh(force = false) {
  if (state.loading) return;
  state.loading = true;
  $("syncStatus").textContent = "Coletando dados do rio...";
  $("syncStatus").classList.remove("error");
  $("syncStatus").classList.remove("warning");
  $("diagnosticBox").hidden = true;

  try {
    const response = await fetch(`data.json?t=${Date.now()}`);
    if (!response.ok) {
      throw new Error("Não foi possível carregar data.json");
    }
    const payload = await response.json();
    if (!payload.ok && !payload.dados) {
      throw new Error(payload.erro || "Falha ao coletar os dados.");
    }
    if (!payload.ok) {
      $("syncStatus").textContent = `Usando último dado salvo: ${payload.erro}`;
      $("syncStatus").classList.add("error");
      $("diagnosticBox").hidden = false;
      $("diagnosticBox").textContent = payload.erro;
    } else if (payload.dados && !payload.dados.previsao_disponivel) {
      const proxima = new Date(parseDate(payload.dados.atualizado_em).getTime() + 5 * 60 * 1000);
      $("syncStatus").textContent = `Atualizado em ${formatDateTime(payload.dados.atualizado_em)} · previsão indisponível · próxima atualização às ${formatTime(proxima)}`;
      $("syncStatus").classList.add("warning");
    } else {
      const proxima = new Date(parseDate(payload.dados.atualizado_em).getTime() + 5 * 60 * 1000);
      $("syncStatus").textContent = `Atualizado em ${formatDateTime(payload.dados.atualizado_em)} · próxima atualização às ${formatTime(proxima)}`;
    }
    state.data = payload.dados;
    renderAll(payload.dados);
  } catch (error) {
    $("syncStatus").textContent = error.message;
    $("syncStatus").classList.add("error");
    $("diagnosticBox").hidden = false;
    $("diagnosticBox").textContent = "Não foi possível carregar data.json. O GitHub Actions atualiza esse arquivo a cada hora; tente novamente em instantes.";
  } finally {
    state.loading = false;
  }
}

function setupChartTooltip() {
  const chartEl = $("chart");
  const tooltipEl = $("chartTooltip");

  function showTooltip(clientX, clientY, target) {
    const rect = chartEl.getBoundingClientRect();
    const offsetX = clientX - rect.left;
    const offsetY = clientY - rect.top;
    const cota = target.getAttribute("data-cota");
    const time = target.getAttribute("data-time");
    const kind = target.getAttribute("data-kind");
    const unit = target.getAttribute("data-unit") || "m";
    tooltipEl.innerHTML = `<strong>${cota} ${unit}</strong><br><span>${time} · ${kind}</span>`;
    tooltipEl.style.left = `${offsetX}px`;
    tooltipEl.style.top = `${Math.max(offsetY - 12, 0)}px`;
    tooltipEl.hidden = false;
  }

  function hideTooltip() {
    tooltipEl.hidden = true;
  }

  chartEl.addEventListener("mousemove", (evt) => {
    const target = evt.target.closest(".chart-hit");
    if (target) {
      showTooltip(evt.clientX, evt.clientY, target);
    } else {
      hideTooltip();
    }
  });
  chartEl.addEventListener("mouseleave", hideTooltip);

  chartEl.addEventListener("touchstart", (evt) => {
    const touch = evt.touches[0];
    if (!touch) return;
    const el2 = document.elementFromPoint(touch.clientX, touch.clientY);
    const target = el2 && el2.closest(".chart-hit");
    if (target) showTooltip(touch.clientX, touch.clientY, target);
    else hideTooltip();
  }, { passive: true });
}

// Contador de visitas via Worker + KV do próprio Cloudflare (sem depender de terceiros).
// Falha silenciosamente se o serviço estiver fora do ar: é só um número informativo
// no rodapé, não deve afetar o resto do site. Conta acessos (hits), não visitantes únicos.
async function trackVisit() {
  const counterEl = $("visitCounter");
  if (!counterEl) return;
  const nf = new Intl.NumberFormat("pt-BR");
  try {
    const r = await fetch("https://rioiguacu-counter.thiago-dff.workers.dev/track");
    const { total, week, day } = await r.json();
    counterEl.textContent = `· ${nf.format(total)} visitas · ${nf.format(week)} na semana · ${nf.format(day)} hoje`;
  } catch (error) {
    // silencioso
  }
}

window.addEventListener("resize", () => state.data && renderChart(state.data));
setupChartTooltip();
refresh(false);
trackVisit();
setInterval(() => refresh(false), 5 * 60 * 1000);
