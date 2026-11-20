// F-DI-13.01 — ferramenta local de caixas e linhas. A página só edita; o servidor valida e grava.
'use strict';

const $ = (id) => document.getElementById(id);
const IDLE_MS = 60_000;
const HANDLE_PX = 9;
const MIN_BOX_PX = 6;
const BUCKET = { boxes: 'boxes', pass1: 'pass1', pass2: 'pass2' };

const state = {
  pages: [],
  pageId: null,
  doc: null,
  image: null,
  mode: 'boxes',
  pass2Mode: 'revisao',
  selected: null, // line_id
  dirty: false,
  saving: false,
  pending: { boxes: 0, pass1: 0, pass2: 0 },
  lastActivity: Date.now(),
  view: { scale: 1, ox: 0, oy: 0 },
  drag: null,
  spaceDown: false,
  saveTimer: null,
  editSeq: 0, // sobe a cada edição; detecta edição feita durante uma gravação em andamento
};

// ------------------------------------------------------------------ utilidades

function dollarBalanced(text) {
  return ((text.match(/(?<!\\)\$/g) || []).length % 2) === 0;
}

function nowIso() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

function lineId(n) {
  return `L${String(n).padStart(3, '0')}`;
}

function sortedLines() {
  return [...state.doc.lines].sort((a, b) => a.order - b.order);
}

function lineById(id) {
  return state.doc?.lines.find((l) => l.line_id === id) || null;
}

function renumber(lines) {
  lines.forEach((line, i) => { line.order = i + 1; });
}

function centroid(poly) {
  return [poly.reduce((s, p) => s + p[0], 0) / 4, poly.reduce((s, p) => s + p[1], 0) / 4];
}

function bounds(poly) {
  const xs = poly.map((p) => p[0]);
  const ys = poly.map((p) => p[1]);
  return { x0: Math.min(...xs), y0: Math.min(...ys), x1: Math.max(...xs), y1: Math.max(...ys) };
}

function pointInPoly([x, y], poly) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i];
    const [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}

function polyArea(poly) {
  let a = 0;
  for (let i = 0; i < poly.length; i++) {
    const [x1, y1] = poly[i];
    const [x2, y2] = poly[(i + 1) % poly.length];
    a += x1 * y2 - x2 * y1;
  }
  return Math.abs(a / 2);
}

function clampPoint([x, y]) {
  const { width, height } = state.doc.image;
  return [Math.round(Math.min(width, Math.max(0, x))), Math.round(Math.min(height, Math.max(0, y)))];
}

function fmtTime(seconds) {
  const s = Math.floor(seconds);
  const m = Math.floor(s / 60);
  return `${String(m).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
}

function words(text) {
  return (text || '').split(/\s+/).filter(Boolean);
}

// Palavras de a que não entram na maior subsequência comum com b.
function unmatched(a, b) {
  const n = a.length;
  const m = b.length;
  const dp = Array.from({ length: n + 1 }, () => new Uint16Array(m + 1));
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
    }
  }
  const out = new Set();
  let i = 0;
  let j = 0;
  while (i < n && j < m) {
    if (a[i] === b[j]) { i++; j++; } else if (dp[i + 1][j] >= dp[i][j + 1]) { out.add(i); i++; } else { j++; }
  }
  for (; i < n; i++) out.add(i);
  return out;
}

function renderWords(el, list, marked) {
  el.replaceChildren();
  list.forEach((word, i) => {
    if (i) el.append(' ');
    if (marked.has(i)) {
      const mark = document.createElement('mark');
      mark.textContent = word;
      el.append(mark);
    } else {
      el.append(word);
    }
  });
  if (!list.length) el.append('—');
}

// ------------------------------------------------------------------ servidor

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  });
  let body = null;
  try { body = await response.json(); } catch { body = null; }
  return { status: response.status, body };
}

async function loadPages() {
  const { status, body } = await api('/api/pages');
  if (status !== 200) return;
  state.pages = body.pages;
  renderPages();
}

async function openPage(pageId) {
  if (state.dirty && !(await save())) return;
  const { status, body } = await api(`/api/pages/${pageId}`);
  if (status !== 200) {
    setSaveState(body?.error || `erro ${status}`, true);
    return;
  }
  state.pageId = pageId;
  state.doc = body;
  state.dirty = false;
  state.pending = { boxes: 0, pass1: 0, pass2: 0 };
  state.selected = sortedLines()[0]?.line_id || null;
  showErrors([]);
  const image = new Image();
  image.decoding = 'async';
  image.src = `/img/${pageId}.jpg?v=${encodeURIComponent(body.image.sha256.slice(0, 12))}`;
  await image.decode().catch(() => null);
  state.image = image;
  renderAll();
  fitView();
  draw();
  if (state.mode !== 'boxes') focusLine(state.selected, true);
}

async function save() {
  if (!state.doc || state.saving) return false;
  commitInput(false);
  state.saving = true;
  setSaveState('gravando…');
  const seq = state.editSeq;
  const delta = { ...state.pending };
  const { status, body } = await api(`/api/pages/${state.pageId}`, {
    method: 'PUT',
    body: JSON.stringify({ version: state.doc.version, doc: state.doc, seconds_delta: delta }),
  });
  state.saving = false;
  if (status === 200) {
    const keep = state.selected;
    for (const key of Object.keys(delta)) state.pending[key] = Math.max(0, state.pending[key] - delta[key]);
    if (seq !== state.editSeq) {
      // Houve edição durante a gravação: mantém o que está na tela e grava de novo em seguida.
      state.doc.version = body.doc.version;
      state.doc.seconds = body.doc.seconds;
      setSaveState('não gravada');
      scheduleSave();
      return true;
    }
    state.doc = body.doc;
    state.dirty = false;
    state.selected = lineById(keep) ? keep : sortedLines()[0]?.line_id || null;
    showErrors([]);
    setSaveState(`gravada (versão ${state.doc.version})`);
    await loadPages();
    renderAll();
    return true;
  }
  if (status === 409) {
    setSaveState('conflito', true);
    showErrors([`${body.error} (versão no disco: ${body.current_version}). Recarregue a página para continuar; as edições desta aba não foram gravadas.`]);
  } else if (status === 422) {
    setSaveState('não gravada', true);
    showErrors(body.errors || [body.error]);
  } else {
    setSaveState(body?.error || `erro ${status}`, true);
  }
  return false;
}

function scheduleSave() {
  clearTimeout(state.saveTimer);
  state.saveTimer = setTimeout(() => { if (state.dirty) save(); }, 1500);
}

function markDirty(autosave = false) {
  state.dirty = true;
  state.editSeq += 1;
  $('save').disabled = false;
  setSaveState('não gravada');
  if (autosave) scheduleSave();
}

function setSaveState(text, error = false) {
  const el = $('save-state');
  el.textContent = text;
  el.classList.toggle('error', error);
}

function showErrors(list) {
  const el = $('errors');
  el.hidden = !list.length;
  el.textContent = list.length ? `Não gravado:\n${list.join('\n')}` : '';
}

// ------------------------------------------------------------------ visualização

const canvas = $('canvas');
const ctx = canvas.getContext('2d');

// Mantém o tamanho interno do canvas igual ao tamanho na tela (sem esticar), preservando o
// ponto da foto que está no canto superior esquerdo.
function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  const width = Math.max(1, Math.round(rect.width * dpr));
  const height = Math.max(1, Math.round(rect.height * dpr));
  if (width === canvas.width && height === canvas.height) return false;
  canvas.width = width;
  canvas.height = height;
  return true;
}

function fitView() {
  resizeCanvas();
  if (!state.doc) return;
  const { width, height } = state.doc.image;
  const scale = Math.min(canvas.width / width, canvas.height / height) * 0.96;
  state.view = { scale, ox: (canvas.width - width * scale) / 2, oy: (canvas.height - height * scale) / 2 };
}

function toImage(clientX, clientY) {
  const rect = canvas.getBoundingClientRect();
  const sx = (clientX - rect.left) * (canvas.width / rect.width);
  const sy = (clientY - rect.top) * (canvas.height / rect.height);
  return [(sx - state.view.ox) / state.view.scale, (sy - state.view.oy) / state.view.scale];
}

function toScreen([x, y]) {
  return [x * state.view.scale + state.view.ox, y * state.view.scale + state.view.oy];
}

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function draw() {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (!state.doc) return;
  const { scale, ox, oy } = state.view;
  if (state.image?.complete) {
    ctx.setTransform(scale, 0, 0, scale, ox, oy);
    ctx.drawImage(state.image, 0, 0, state.doc.image.width, state.doc.image.height);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
  }
  const dpr = window.devicePixelRatio || 1;
  const textMode = state.mode !== 'boxes';
  for (const line of sortedLines()) {
    const selected = line.line_id === state.selected;
    const pts = line.polygon.map(toScreen);
    const done = textMode && line[state.mode];
    ctx.beginPath();
    pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
    ctx.closePath();
    ctx.lineWidth = (selected ? 3 : 1.5) * dpr;
    ctx.strokeStyle = cssVar(`--${line.box_origin}`);
    ctx.globalAlpha = textMode && !selected ? 0.45 : 1;
    if (selected) {
      ctx.fillStyle = 'rgba(255, 214, 0, 0.18)';
      ctx.fill();
    } else if (done) {
      ctx.fillStyle = 'rgba(21, 128, 61, 0.12)';
      ctx.fill();
    }
    ctx.stroke();
    ctx.globalAlpha = 1;
    const [lx, ly] = pts[0];
    const label = String(line.order);
    ctx.font = `${11 * dpr}px system-ui, sans-serif`;
    const w = ctx.measureText(label).width + 6 * dpr;
    ctx.fillStyle = cssVar(`--${line.box_origin}`);
    ctx.fillRect(lx - w, ly, w, 14 * dpr);
    ctx.fillStyle = '#fff';
    ctx.fillText(label, lx - w + 3 * dpr, ly + 11 * dpr);
    if (selected && state.mode === 'boxes') {
      for (const [x, y] of pts) {
        ctx.fillStyle = '#fff';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 1 * dpr;
        ctx.fillRect(x - 4 * dpr, y - 4 * dpr, 8 * dpr, 8 * dpr);
        ctx.strokeRect(x - 4 * dpr, y - 4 * dpr, 8 * dpr, 8 * dpr);
      }
    }
  }
  if (state.drag?.kind === 'create') {
    const [x0, y0] = toScreen(state.drag.start);
    const [x1, y1] = toScreen(state.drag.current);
    ctx.setLineDash([6 * dpr, 4 * dpr]);
    ctx.strokeStyle = cssVar('--criada');
    ctx.lineWidth = 2 * dpr;
    ctx.strokeRect(x0, y0, x1 - x0, y1 - y0);
    ctx.setLineDash([]);
  }
}

function centerOn(line) {
  if (!line) return;
  const b = bounds(line.polygon);
  const [sx0, sy0] = toScreen([b.x0, b.y0]);
  const [sx1, sy1] = toScreen([b.x1, b.y1]);
  const margin = 40 * (window.devicePixelRatio || 1);
  if (sx0 >= margin && sy0 >= margin && sx1 <= canvas.width - margin && sy1 <= canvas.height - margin) return;
  const [cx, cy] = centroid(line.polygon);
  state.view.ox = canvas.width / 2 - cx * state.view.scale;
  state.view.oy = canvas.height / 2 - cy * state.view.scale;
}

// ------------------------------------------------------------------ interação na foto

function hitHandle(point) {
  const line = lineById(state.selected);
  if (!line || state.mode !== 'boxes') return -1;
  const tolerance = (HANDLE_PX * (window.devicePixelRatio || 1)) / state.view.scale;
  return line.polygon.findIndex(([x, y]) => Math.abs(x - point[0]) <= tolerance && Math.abs(y - point[1]) <= tolerance);
}

function hitLine(point) {
  const hits = state.doc.lines.filter((l) => pointInPoly(point, l.polygon));
  hits.sort((a, b) => polyArea(a.polygon) - polyArea(b.polygon));
  return hits[0] || null;
}

canvas.addEventListener('wheel', (event) => {
  if (!state.doc) return;
  event.preventDefault();
  const [ix, iy] = toImage(event.clientX, event.clientY);
  const factor = Math.exp(-event.deltaY * 0.0015);
  const scale = Math.min(8, Math.max(0.05, state.view.scale * factor));
  const rect = canvas.getBoundingClientRect();
  const sx = (event.clientX - rect.left) * (canvas.width / rect.width);
  const sy = (event.clientY - rect.top) * (canvas.height / rect.height);
  state.view = { scale, ox: sx - ix * scale, oy: sy - iy * scale };
  draw();
}, { passive: false });

canvas.addEventListener('pointerdown', (event) => {
  if (!state.doc) return;
  canvas.setPointerCapture(event.pointerId);
  const point = toImage(event.clientX, event.clientY);
  if (event.button === 1 || state.spaceDown || event.button === 2) {
    state.drag = { kind: 'pan', last: [event.clientX, event.clientY] };
    return;
  }
  if (event.button !== 0) return;
  if (state.mode !== 'boxes') {
    const hit = hitLine(point);
    if (hit) { commitInput(false); state.selected = hit.line_id; focusLine(hit.line_id, false); renderAll(); }
    return;
  }
  const handle = hitHandle(point);
  if (handle >= 0) {
    state.drag = { kind: 'corner', index: handle, line: state.selected };
    return;
  }
  const hit = hitLine(point);
  if (hit) {
    state.selected = hit.line_id;
    state.drag = { kind: 'move', line: hit.line_id, last: point, moved: false };
    renderAll();
    return;
  }
  state.drag = { kind: 'create', start: clampPoint(point), current: clampPoint(point) };
});

canvas.addEventListener('pointermove', (event) => {
  const drag = state.drag;
  if (!drag || !state.doc) return;
  if (drag.kind === 'pan') {
    const rect = canvas.getBoundingClientRect();
    state.view.ox += (event.clientX - drag.last[0]) * (canvas.width / rect.width);
    state.view.oy += (event.clientY - drag.last[1]) * (canvas.height / rect.height);
    drag.last = [event.clientX, event.clientY];
  } else if (drag.kind === 'corner') {
    const line = lineById(drag.line);
    line.polygon[drag.index] = clampPoint(toImage(event.clientX, event.clientY));
    if (line.box_origin === 'motor') line.box_origin = 'ajustada';
    markDirty();
  } else if (drag.kind === 'move') {
    const point = toImage(event.clientX, event.clientY);
    const line = lineById(drag.line);
    const dx = point[0] - drag.last[0];
    const dy = point[1] - drag.last[1];
    if (Math.abs(dx) + Math.abs(dy) < 0.5) return;
    line.polygon = line.polygon.map(([x, y]) => clampPoint([x + dx, y + dy]));
    if (line.box_origin === 'motor') line.box_origin = 'ajustada';
    drag.last = point;
    drag.moved = true;
    markDirty();
  } else if (drag.kind === 'create') {
    drag.current = clampPoint(toImage(event.clientX, event.clientY));
  }
  draw();
});

function endDrag() {
  const drag = state.drag;
  state.drag = null;
  if (!drag) return;
  if (drag.kind === 'create') {
    const [x0, y0] = drag.start;
    const [x1, y1] = drag.current;
    const minPx = MIN_BOX_PX / state.view.scale;
    if (Math.abs(x1 - x0) >= minPx && Math.abs(y1 - y0) >= minPx) {
      const [l, r] = [Math.min(x0, x1), Math.max(x0, x1)];
      const [t, b] = [Math.min(y0, y1), Math.max(y0, y1)];
      const line = {
        line_id: lineId(state.doc.next_line_id),
        order: 0,
        polygon: [[l, t], [r, t], [r, b], [l, b]],
        box_origin: 'criada',
        motor_text: null,
        draft: null,
        pass1: null,
        pass2: null,
      };
      state.doc.next_line_id += 1;
      const lines = sortedLines();
      const cy = (t + b) / 2;
      let at = lines.findIndex((other) => centroid(other.polygon)[1] > cy);
      if (at < 0) at = lines.length;
      lines.splice(at, 0, line);
      renumber(lines);
      state.doc.lines = lines;
      state.selected = line.line_id;
      markDirty();
    }
  }
  renderAll();
}

canvas.addEventListener('pointerup', endDrag);
canvas.addEventListener('pointercancel', endDrag);
canvas.addEventListener('contextmenu', (event) => event.preventDefault());

function deleteSelected() {
  const line = lineById(state.selected);
  if (!line) return;
  const lines = sortedLines().filter((l) => l.line_id !== line.line_id);
  const next = lines.find((l) => l.order > line.order) || lines[lines.length - 1];
  renumber(lines);
  state.doc.lines = lines;
  state.selected = next?.line_id || null;
  markDirty();
  renderAll();
}

function moveSelected(delta) {
  const lines = sortedLines();
  const i = lines.findIndex((l) => l.line_id === state.selected);
  const j = i + delta;
  if (i < 0 || j < 0 || j >= lines.length) return;
  [lines[i], lines[j]] = [lines[j], lines[i]];
  renumber(lines);
  state.doc.lines = lines;
  markDirty();
  renderAll();
}

function sortTopDown() {
  const lines = sortedLines().sort((a, b) => {
    const [ax, ay] = centroid(a.polygon);
    const [bx, by] = centroid(b.polygon);
    return ay - by || ax - bx;
  });
  renumber(lines);
  state.doc.lines = lines;
  markDirty();
  renderAll();
}

// ------------------------------------------------------------------ texto

const input = $('line-input');

function passValue(line) {
  if (state.mode === 'pass1') return line.pass1?.text ?? line.draft ?? '';
  if (line.pass2) return line.pass2.text;
  return state.pass2Mode === 'revisao' ? line.pass1?.text ?? '' : '';
}

function focusLine(id, center) {
  const line = lineById(id);
  state.selected = id;
  if (!line) { input.value = ''; return; }
  input.value = passValue(line);
  input.dataset.lineId = id;
  input.dataset.original = input.value;
  validateInput();
  if (center) centerOn(line);
  renderText();
  $('crop').scrollIntoView({ block: 'nearest' });
  draw();
  input.focus();
  input.setSelectionRange(input.value.length, input.value.length);
}

function validateInput() {
  const text = input.value;
  const warning = $('line-warning');
  let message = '';
  if (!dollarBalanced(text)) message = 'Fórmula sem fechar: o número de $ precisa ser par (use \\$ para cifrão).';
  input.classList.toggle('invalid', Boolean(message));
  warning.hidden = !message;
  warning.textContent = message;
  return !message;
}

// Confirma o campo na passada atual; devolve false se não deu.
function commitInput(explicit) {
  if (state.mode === 'boxes' || !state.doc) return true;
  const line = lineById(input.dataset.lineId);
  if (!line) return true;
  const text = input.value.trim();
  const changed = input.value !== input.dataset.original;
  const already = line[state.mode];
  if (!explicit && !changed) return true;
  if (!text) {
    if (explicit) {
      const warning = $('line-warning');
      warning.hidden = false;
      warning.textContent = 'Linha sem texto: escreva [?] se for ilegível, ou apague a caixa na etapa 1.';
    }
    return false;
  }
  if (!validateInput()) return false;
  if (already && already.text === text && !explicit) return true;
  const value = { text, at: nowIso() };
  if (state.mode === 'pass2') value.mode = state.pass2Mode;
  if (!(already && already.text === text)) {
    line[state.mode] = value;
    markDirty(true);
  }
  input.dataset.original = input.value;
  return true;
}

function step(delta) {
  const lines = sortedLines();
  const i = lines.findIndex((l) => l.line_id === state.selected);
  const next = lines[Math.min(lines.length - 1, Math.max(0, i + delta))];
  if (next) focusLine(next.line_id, true);
  renderAll();
}

input.addEventListener('input', validateInput);
input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    event.preventDefault();
    if (event.shiftKey) { commitInput(false); step(-1); return; }
    if (commitInput(true)) {
      const lines = sortedLines();
      const last = lines[lines.length - 1]?.line_id === state.selected;
      if (!last) { step(1); return; }
      // Na última linha: volta para a primeira que ainda falta, ou grava a página completa.
      const pending = lines.find((l) => !l[state.mode]);
      if (pending) {
        focusLine(pending.line_id, true);
        renderAll();
        setSaveState(`falta(m) ${lines.filter((l) => !l[state.mode]).length} linha(s)`);
      } else {
        renderAll();
        save();
      }
    }
  } else if (event.key === 'Escape') {
    input.value = input.dataset.original || '';
    validateInput();
  } else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'm') {
    event.preventDefault();
    const { selectionStart: s, selectionEnd: e, value } = input;
    input.value = `${value.slice(0, s)}$${value.slice(s, e)}$${value.slice(e)}`;
    input.setSelectionRange(s + 1, e + 1);
    validateInput();
  }
});

$('draft-import').addEventListener('click', async () => {
  const text = $('draft-text').value;
  if (!text.trim()) return;
  commitInput(false);
  const { status, body } = await api(`/api/pages/${state.pageId}/draft`, {
    method: 'POST',
    body: JSON.stringify({ text, label: $('draft-label').value, doc: state.doc }),
  });
  if (status !== 200) { setSaveState(body?.error || `erro ${status}`, true); return; }
  state.doc = body.doc;
  markDirty();
  focusLine(state.selected, false);
  renderAll();
});

// ------------------------------------------------------------------ painéis

function renderPages() {
  const list = $('page-list');
  list.replaceChildren();
  $('pages-empty').hidden = state.pages.length > 0;
  for (const page of state.pages) {
    const li = document.createElement('li');
    const button = document.createElement('button');
    button.type = 'button';
    button.disabled = !page.hash_ok;
    button.setAttribute('aria-current', String(page.id === state.pageId));
    const id = document.createElement('span');
    id.className = 'page-id';
    id.textContent = page.id + (page.hash_ok ? '' : ' 🔒');
    const badge = document.createElement('span');
    badge.className = `badge ${page.split === 'test' ? 'test' : ''}`;
    badge.textContent = { test: 'teste', 'dev-val': 'dev-val', 'dev-train': 'treino', 'sem-split': 'dev' }[page.split];
    const steps = document.createElement('span');
    steps.className = 'steps';
    const s = page.status || {};
    for (const [key, label] of [['boxes_done', 'caixas'], ['pass1_done', '1ª'], ['pass2_done', '2ª']]) {
      const span = document.createElement('span');
      span.className = s[key] ? 'on' : '';
      span.textContent = `${s[key] ? '✓' : '·'} ${label} `;
      steps.append(span);
    }
    if (page.seconds) {
      const total = page.seconds.boxes + page.seconds.pass1 + page.seconds.pass2;
      steps.append(` ${fmtTime(total)}`);
    }
    if (!page.hash_ok) button.title = 'Foto sem hash conferido com o EXP-027: bloqueada';
    button.append(id, badge, steps);
    button.addEventListener('click', () => openPage(page.id));
    li.append(button);
    list.append(li);
  }
}

function renderBoxesPanel() {
  const list = $('line-list');
  list.replaceChildren();
  $('boxes-done').checked = Boolean(state.doc?.status.boxes_done);
  if (!state.doc) return;
  for (const line of sortedLines()) {
    const li = document.createElement('li');
    li.setAttribute('aria-selected', String(line.line_id === state.selected));
    const order = document.createElement('span');
    order.textContent = `${line.order}.`;
    const id = document.createElement('span');
    id.className = `origin-${line.box_origin}`;
    id.textContent = line.line_id;
    const preview = document.createElement('span');
    preview.className = 'preview';
    preview.textContent = line.pass1?.text ?? line.draft ?? '';
    const actions = document.createElement('span');
    actions.className = 'actions';
    if (line.line_id === state.selected) {
      for (const [label, title, fn] of [['↑', 'Subir', () => moveSelected(-1)], ['↓', 'Descer', () => moveSelected(1)], ['✕', 'Apagar caixa', deleteSelected]]) {
        const b = document.createElement('button');
        b.type = 'button';
        b.textContent = label;
        b.title = title;
        b.setAttribute('aria-label', `${title} ${line.line_id}`);
        b.addEventListener('click', (event) => { event.stopPropagation(); fn(); });
        actions.append(b);
      }
    }
    li.append(order, id, preview, actions);
    li.addEventListener('click', () => { state.selected = line.line_id; centerOn(line); renderAll(); });
    list.append(li);
  }
}

function renderCrop(line) {
  const crop = $('crop');
  const cctx = crop.getContext('2d');
  const rect = crop.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  crop.width = Math.max(1, Math.round(rect.width * dpr));
  crop.height = Math.max(1, Math.round(rect.height * dpr));
  cctx.clearRect(0, 0, crop.width, crop.height);
  if (!line || !state.image?.complete) return;
  const b = bounds(line.polygon);
  const pad = Math.max(6, (b.y1 - b.y0) * 0.25);
  const sx = Math.max(0, b.x0 - pad);
  const sy = Math.max(0, b.y0 - pad);
  const sw = Math.min(state.doc.image.width, b.x1 + pad) - sx;
  const sh = Math.min(state.doc.image.height, b.y1 + pad) - sy;
  const scale = Math.min(crop.width / sw, crop.height / sh);
  const dw = sw * scale;
  const dh = sh * scale;
  const dx = (crop.width - dw) / 2;
  const dy = (crop.height - dh) / 2;
  cctx.drawImage(state.image, sx, sy, sw, sh, dx, dy, dw, dh);
  cctx.beginPath();
  line.polygon.forEach(([x, y], i) => {
    const px = dx + (x - sx) * scale;
    const py = dy + (y - sy) * scale;
    if (i) cctx.lineTo(px, py); else cctx.moveTo(px, py);
  });
  cctx.closePath();
  cctx.strokeStyle = 'rgba(255, 196, 0, 0.9)';
  cctx.lineWidth = 1.5 * dpr;
  cctx.stroke();
}

function renderText() {
  if (!state.doc) return;
  const lines = sortedLines();
  const line = lineById(state.selected);
  const i = lines.indexOf(line);
  const field = state.mode;
  const done = lines.filter((l) => l[field]).length;
  $('text-heading').textContent = field === 'pass1' ? '1ª passada' : `2ª passada (${state.pass2Mode === 'cego' ? 'cega' : 'revisão'})`;
  $('line-pos').textContent = line ? `Linha ${i + 1} de ${lines.length}` : 'Sem linhas';
  $('line-meta').textContent = line ? `${line.line_id} · ${done}/${lines.length} confirmadas${line[field] ? ' · esta já confirmada' : ''}` : '';
  const pendingBox = !state.doc.status.boxes_done;
  const pendingLines = lines.length - done;
  const notes = [];
  if (pendingBox) notes.push('A etapa 1 ainda não foi marcada como "Caixas prontas".');
  // Depois de chegar ao fim da página, lembra quantas linhas ficaram para trás.
  if (pendingLines && lines[lines.length - 1]?.[field]) notes.push(`Faltam ${pendingLines} linha(s) nesta passada.`);
  $('page-pending').hidden = !notes.length;
  $('page-pending').textContent = notes.join(' ');
  input.disabled = !line;
  renderCrop(line);
  const imported = state.doc.draft_source !== 'motor';
  const showDiff = Boolean(line && imported && field === 'pass1' && line.draft && line.motor_text);
  $('diff').hidden = !showDiff;
  if (showDiff) {
    const draftWords = words(line.draft);
    const motorWords = words(line.motor_text);
    renderWords($('diff-draft'), draftWords, unmatched(draftWords, motorWords));
    renderWords($('diff-motor'), motorWords, unmatched(motorWords, draftWords));
  }
  // Rascunho e sobras só na 1ª passada: a 2ª (sobretudo a cega) não pode ver o rascunho.
  document.querySelector('.draft-import').hidden = field !== 'pass1';
  const leftovers = field === 'pass1' ? state.doc.draft_leftover || [] : [];
  $('leftover').hidden = !leftovers.length;
  const list = $('leftover-list');
  list.replaceChildren();
  for (const text of leftovers) {
    const li = document.createElement('li');
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = 'copiar';
    button.addEventListener('click', () => navigator.clipboard?.writeText(text));
    li.append(`${text} `, button);
    list.append(li);
  }
}

function renderAll() {
  const hasDoc = Boolean(state.doc);
  $('page-title').textContent = hasDoc ? `${state.pageId} · ${state.doc.lines.length} linhas` : '—';
  for (const mode of ['boxes', 'pass1', 'pass2']) {
    $(`tab-${mode}`).setAttribute('aria-selected', String(state.mode === mode));
  }
  $('pass2-mode-wrap').hidden = state.mode !== 'pass2';
  $('panel-boxes').hidden = state.mode !== 'boxes';
  $('panel-text').hidden = state.mode === 'boxes';
  $('save').disabled = !state.dirty;
  const banner = $('banner');
  const test = hasDoc && state.doc.split === 'test';
  const lowRes = hasDoc && state.pages.find((p) => p.id === state.pageId)?.low_resolution;
  const notes = [];
  if (test) notes.push('Página do teste congelado: anotar só para medir (EXP-028A). Nunca usar em treino, ajuste de limiar ou dicionário.');
  if (lowRes) notes.push(`Imagem reduzida (${state.doc.image.width}×${state.doc.image.height} px), não a foto original: serve para treinar a anotação e medir o tempo, não como referência nem treino.`);
  banner.hidden = !notes.length;
  banner.textContent = notes.join(' ');
  $('viewer-help').textContent = state.mode === 'boxes'
    ? 'Arraste: criar · canto: ajustar · dentro: mover · Delete: apagar · roda: zoom · espaço+arrastar: mover a foto'
    : 'Clique numa caixa para ir à linha · roda: zoom · espaço+arrastar: mover a foto';
  renderPages();
  if (state.mode === 'boxes') renderBoxesPanel(); else renderText();
  draw();
  updateTimer();
}

function setMode(mode) {
  commitInput(false);
  state.mode = mode;
  renderAll();
  if (mode !== 'boxes' && state.doc) {
    const lines = sortedLines();
    const firstOpen = lines.find((l) => !l[mode]) || lines.find((l) => l.line_id === state.selected) || lines[0];
    if (firstOpen) focusLine(firstOpen.line_id, true);
  }
}

// ------------------------------------------------------------------ tempo ativo

function updateTimer() {
  if (!state.doc) { $('timer').textContent = '00:00'; return; }
  const bucket = BUCKET[state.mode];
  const here = state.doc.seconds[bucket] + state.pending[bucket];
  const total = ['boxes', 'pass1', 'pass2'].reduce((s, k) => s + state.doc.seconds[k] + state.pending[k], 0);
  $('timer').textContent = `etapa ${fmtTime(here)} · página ${fmtTime(total)}`;
}

setInterval(() => {
  if (!state.doc || document.visibilityState !== 'visible') return;
  if (Date.now() - state.lastActivity > IDLE_MS) return;
  state.pending[BUCKET[state.mode]] += 1;
  updateTimer();
}, 1000);

for (const kind of ['pointermove', 'pointerdown', 'keydown', 'wheel']) {
  document.addEventListener(kind, () => { state.lastActivity = Date.now(); }, { passive: true });
}

// ------------------------------------------------------------------ teclado e botões

document.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
    event.preventDefault();
    save();
    return;
  }
  const typing = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName);
  if (typing) return;
  if (event.key === ' ') { state.spaceDown = true; event.preventDefault(); }
  if (state.mode === 'boxes' && (event.key === 'Delete' || event.key === 'Backspace')) {
    event.preventDefault();
    deleteSelected();
  }
});
document.addEventListener('keyup', (event) => { if (event.key === ' ') state.spaceDown = false; });

for (const mode of ['boxes', 'pass1', 'pass2']) $(`tab-${mode}`).addEventListener('click', () => setMode(mode));
$('pass2-mode').addEventListener('change', (event) => {
  state.pass2Mode = event.target.value;
  if (state.doc) focusLine(state.selected, false);
  renderAll();
});
$('save').addEventListener('click', save);
$('sort-top').addEventListener('click', sortTopDown);
$('boxes-done').addEventListener('change', (event) => {
  state.doc.status.boxes_done = event.target.checked;
  markDirty(true);
});
new ResizeObserver(() => { if (resizeCanvas()) draw(); }).observe(canvas);
window.addEventListener('resize', () => { if (state.mode !== 'boxes') renderText(); });
window.addEventListener('beforeunload', (event) => {
  if (state.dirty) { event.preventDefault(); event.returnValue = ''; }
});

resizeCanvas();
loadPages().then(() => {
  const first = state.pages.find((p) => p.hash_ok);
  if (first) openPage(first.id);
});
