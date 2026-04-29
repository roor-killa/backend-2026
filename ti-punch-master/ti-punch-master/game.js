/* =============================================
   Ti Punch Master – game.js
   Version 2.0 · Martinique 2026
   ============================================= */

// ─── DATA ────────────────────────────────────

const CLIENTS = [
  { id:'madeleine',  name:'Madeleine',   avatar:'👵', bg:'#fde8c8', cocktail:'tipunch',       diff:'Facile',    dialogue:'"Un bon ti punch bien dosé, siouplé !"' },
  { id:'jean_claude',name:'Jean-Claude', avatar:'👨‍🍳', bg:'#c8e8fd', cocktail:'mojito',        diff:'Facile',    dialogue:'"Donne-moi un mojito rafraîchissant !"' },
  { id:'marie',      name:'Marie-Hélène',avatar:'👩',  bg:'#fdc8e8', cocktail:'planteur',      diff:'Moyen',     dialogue:'"Je voudrais un planteur bien fruité."' },
  { id:'theo',       name:'Théo',        avatar:'🧑',  bg:'#c8fde8', cocktail:'daiquiri',      diff:'Moyen',     dialogue:'"Un daïquiri fraise s\'il te plaît !"' },
  { id:'cecile',     name:'Cécile',      avatar:'👩‍🦰', bg:'#fdfdc8', cocktail:'sangria',       diff:'Facile',    dialogue:'"Une sangria légère pour moi."' },
  { id:'mamie_rose', name:'Mamie Rose',  avatar:'👴',  bg:'#f0c8fd', cocktail:'punchcoco',     diff:'Facile',    dialogue:'"Un punch coco comme autrefois !"' },
  { id:'baptiste',   name:'Baptiste',    avatar:'🧔',  bg:'#c8fdfd', cocktail:'gintonic',      diff:'Moyen',     dialogue:'"Gin tonic bien équilibré merci."' },
  { id:'sylvie',     name:'Sylvie',      avatar:'👩‍💼', bg:'#fdc8c8', cocktail:'spritz',        diff:'Moyen',     dialogue:'"Un spritz pour l\'apéro !"' },
  { id:'marco',      name:'Marco',       avatar:'👦',  bg:'#c8c8fd', cocktail:'tipunch_hard',  diff:'Difficile', dialogue:'"Ti punch fort, comme un vrai martiniquais !"' },
  { id:'laure',      name:'Laure',       avatar:'👩‍🎤', bg:'#fde8d0', cocktail:'mojito_hard',   diff:'Difficile', dialogue:'"Mojito parfait, chaque millilitre compte !"' },
  { id:'remy',       name:'Rémy',        avatar:'🧑‍🍳', bg:'#c8fdc8', cocktail:'daiquiri_hard', diff:'Difficile', dialogue:'"Daïquiri parfait, soyez précis !"' },
  { id:'isabelle',   name:'Isabelle',    avatar:'👩‍🦳', bg:'#fdc8fd', cocktail:'punchcoco',     diff:'Facile',    dialogue:'"Punch coco léger s\'il vous plaît."' },
];

const COCKTAILS = {
  tipunch:      { name:'Ti Punch',        emoji:'🥃', tol:1,   ingrs:[{n:'Rhum agricole', cl:4, color:'#d4a030'},{n:'Citron vert',  cl:3, color:'#88cc22'},{n:'Sucre canne',  cl:3, color:'#ffe8a0'}] },
  tipunch_hard: { name:'Ti Punch Fort',   emoji:'🥃', tol:0.5, ingrs:[{n:'Rhum agricole', cl:6, color:'#d4a030'},{n:'Citron vert',  cl:2, color:'#88cc22'},{n:'Sucre canne',  cl:2, color:'#ffe8a0'}] },
  mojito:       { name:'Mojito',          emoji:'🍃', tol:1,   ingrs:[{n:'Rhum blanc',    cl:4, color:'#f0e0a0'},{n:'Citron vert',  cl:3, color:'#88cc22'},{n:'Sirop menthe', cl:2, color:'#22bb66'}] },
  mojito_hard:  { name:'Mojito Précis',   emoji:'🍃', tol:0.5, ingrs:[{n:'Rhum blanc',    cl:5, color:'#f0e0a0'},{n:'Citron vert',  cl:3, color:'#88cc22'},{n:'Sirop menthe', cl:2, color:'#22bb66'}] },
  planteur:     { name:'Planteur',        emoji:'🍊', tol:1,   ingrs:[{n:'Rhum vieux',    cl:4, color:'#c07020'},{n:'Jus orange',   cl:5, color:'#ff8820'},{n:'Grenadine',    cl:2, color:'#cc1144'}] },
  daiquiri:     { name:'Daïquiri Fraise', emoji:'🍓', tol:1,   ingrs:[{n:'Rhum blanc',    cl:4, color:'#f0e0a0'},{n:'Citron vert',  cl:3, color:'#88cc22'},{n:'Sirop fraise', cl:3, color:'#ee3366'}] },
  daiquiri_hard:{ name:'Daïquiri Parfait',emoji:'🍓', tol:0.5, ingrs:[{n:'Rhum blanc',    cl:5, color:'#f0e0a0'},{n:'Citron vert',  cl:3, color:'#88cc22'},{n:'Sirop fraise', cl:2, color:'#ee3366'}] },
  sangria:      { name:'Sangria',         emoji:'🍷', tol:1,   ingrs:[{n:'Vin rouge',     cl:6, color:'#881133'},{n:'Jus orange',   cl:4, color:'#ff8820'},{n:'Sirop pêche',  cl:2, color:'#ffaa66'}] },
  punchcoco:    { name:'Punch Coco',      emoji:'🥥', tol:1,   ingrs:[{n:'Rhum agricole', cl:4, color:'#d4a030'},{n:'Lait de coco', cl:4, color:'#f0ecd8'},{n:'Jus ananas',   cl:3, color:'#ffe040'}] },
  gintonic:     { name:'Gin Tonic',       emoji:'🍸', tol:1,   ingrs:[{n:'Gin',           cl:4, color:'#c8e8ff'},{n:'Citron vert',  cl:2, color:'#88cc22'},{n:'Tonic',        cl:6, color:'#d8f0ff'}] },
  spritz:       { name:'Spritz',          emoji:'🍊', tol:1,   ingrs:[{n:'Aperol',        cl:4, color:'#ff6620'},{n:'Prosecco',     cl:5, color:'#ffe8a0'},{n:'Soda',          cl:2, color:'#d0f4ff'}] },
};

const FEEDBACK_MSGS = {
  100: { emoji:'🤩', text:'PARFAIT ! Exactement ce qu\'il me fallait ! Merci infiniment !' },
   85: { emoji:'😄', text:'Très bon, bravo ! C\'est presque parfait, tu es doué !' },
   65: { emoji:'😊', text:'Pas mal, ça passe... mais on peut faire mieux !' },
   40: { emoji:'😐', text:'Mouais... le dosage est un peu approximatif.' },
   20: { emoji:'😞', text:'Bof, c\'est raté mon ami. Essaie encore.' },
    5: { emoji:'😤', text:'Non, non, non... c\'est quoi ça ?! Tu appelles ça un cocktail ?!' },
};

// ─── STATE ───────────────────────────────────

let state = {
  manche: 0,
  totalScore: 0,
  clients: [],
  currentClient: null,
  currentCocktail: null,
  dosages: [0, 0, 0],
  served: false,
  leaderboard: [],
};

// ─── INIT ────────────────────────────────────

function init() {
  try {
    const saved = localStorage.getItem('tpm_leaderboard_v2');
    state.leaderboard = saved ? JSON.parse(saved) : [];
  } catch(e) {
    state.leaderboard = [];
  }
}

// ─── SCREENS ─────────────────────────────────

function show(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const el = document.getElementById(id);
  if (el) el.classList.add('active');
}

function goMenu()    { show('menu-screen'); }
function showCredits() { show('credits-screen'); }

function showLeaderboard() {
  document.getElementById('end-title').textContent = '🏆 Classement';
  document.getElementById('final-score-div').style.display = 'none';
  renderLeaderboard();
  show('end-screen');
}

// ─── GAME FLOW ────────────────────────────────

function startGame() {
  state.manche = 0;
  state.totalScore = 0;
  state.clients = shuffleAndPick(CLIENTS, 5);
  show('game-screen');
  loadClient();
}

function loadClient() {
  const client = state.clients[state.manche];
  state.currentClient = client;
  state.currentCocktail = COCKTAILS[client.cocktail];
  state.dosages = [0, 0, 0];
  state.served = false;

  // HUD
  buildMancheDots();
  document.getElementById('score-display').textContent = state.totalScore;

  // Client card
  const av = document.getElementById('client-avatar');
  av.textContent = client.avatar;
  av.style.background = client.bg;
  document.getElementById('client-name').textContent = client.name;
  document.getElementById('client-dialogue').textContent = client.dialogue;

  const badge = document.getElementById('diff-badge');
  badge.textContent = client.diff;
  badge.className = 'badge-diff diff-' + client.diff.toLowerCase();

  // Cocktail label
  const ck = state.currentCocktail;
  document.getElementById('cocktail-label').textContent = ck.emoji + '  ' + ck.name;

  // Reset glass
  updateGlass();

  // Sliders
  buildSliders(ck);

  // Pour button
  const pourBtn = document.getElementById('pour-btn');
  pourBtn.disabled = false;
  pourBtn.textContent = 'Servir 🍹';
}

function buildMancheDots() {
  const container = document.getElementById('manche-dots');
  container.innerHTML = '';
  for (let i = 0; i < 5; i++) {
    const d = document.createElement('div');
    d.className = 'dot' + (i < state.manche ? ' done' : i === state.manche ? ' active' : '');
    container.appendChild(d);
  }
}

function buildSliders(ck) {
  const wrap = document.getElementById('sliders-wrap');
  wrap.innerHTML = '';
  ck.ingrs.forEach((ing, i) => {
    const div = document.createElement('div');
    div.className = 'slider-group';
    div.innerHTML = `
      <div class="slider-label">
        <span class="slider-name">${ing.n}</span>
        <span class="slider-val" id="val${i}" style="background:${ing.color}">0 cl</span>
      </div>
      <input type="range" min="0" max="10" step="1" value="0" id="sl${i}"
             oninput="onSlider(${i}, this.value)">
    `;
    wrap.appendChild(div);
  });
}

function onSlider(i, v) {
  state.dosages[i] = parseInt(v, 10);
  document.getElementById('val' + i).textContent = v + ' cl';
  updateGlass();
}

// ─── GLASS ───────────────────────────────────

function updateGlass() {
  const ck  = state.currentCocktail;
  const dos = state.dosages;
  const tot = dos.reduce((a, b) => a + b, 0);
  const maxExpected = ck.ingrs.reduce((a, b) => a + b.cl, 0) * 1.4;
  const fillPct = Math.min(tot / maxExpected, 1);

  const glassTop = 12, glassBot = 158;
  const glassH   = glassBot - glassTop;
  const fillH    = fillPct * glassH;

  const layers = ['liq1', 'liq2', 'liq3'];
  const colors  = ck.ingrs.map(i => i.color);
  const totSafe = tot || 1;

  let yOff = glassBot;
  for (let j = 0; j < 3; j++) {
    const h  = (dos[j] / totSafe) * fillH;
    yOff -= h;
    const el = document.getElementById(layers[j]);
    el.setAttribute('y',       yOff.toFixed(1));
    el.setAttribute('height',  h.toFixed(1));
    el.setAttribute('fill',    colors[j]);
    el.setAttribute('opacity', h > 0.5 ? '0.88' : '0');
  }
}

// ─── SERVE / SCORE ───────────────────────────

function serve() {
  if (state.served) return;
  state.served = true;
  document.getElementById('pour-btn').disabled = true;

  const ck   = state.currentCocktail;
  const diffs = ck.ingrs.map((ing, i) => Math.abs(state.dosages[i] - ing.cl));
  const total = diffs.reduce((a, b) => a + b, 0);
  const tol   = ck.tol;

  let score;
  if      (total === 0)            score = 100;
  else if (total <= tol)           score = 85;
  else if (total <= tol * 2)       score = 65;
  else if (total <= tol * 3 + 1)   score = 40;
  else if (total <= tol * 4 + 2)   score = 20;
  else                             score = 5;

  state.totalScore += score;
  showFeedback(score, ck, diffs);
}

function showFeedback(score, ck, diffs) {
  show('feedback-screen');

  const fb = FEEDBACK_MSGS[score] || FEEDBACK_MSGS[5];
  document.getElementById('feedback-emoji').textContent = fb.emoji;
  document.getElementById('feedback-msg').textContent   = fb.text;
  document.getElementById('feedback-cocktail-name').textContent = ck.emoji + ' ' + ck.name;

  // Animated score counter
  animateCounter('feedback-score-anim', 0, score, 600);

  // Dosage comparison
  const dc = document.getElementById('dosage-compare');
  dc.innerHTML = ck.ingrs.map((ing, i) => {
    const isOk = diffs[i] === 0;
    return `
      <div class="dose-col">
        <div class="dc-name">${ing.n}</div>
        <div class="dc-yours">${state.dosages[i]} cl</div>
        <div class="${isOk ? 'dc-ok' : 'dc-target'}">${isOk ? '✓ Parfait' : 'Cible : ' + ing.cl + ' cl'}</div>
      </div>
    `;
  }).join('');

  const btn = document.getElementById('next-btn');
  btn.textContent = state.manche < 4 ? 'Client suivant →' : '🏆 Voir le classement';
  btn.disabled = true;
  setTimeout(() => { btn.disabled = false; }, 1400);
}

function nextClient() {
  state.manche++;
  if (state.manche >= 5) {
    endGame();
  } else {
    show('game-screen');
    loadClient();
  }
}

// ─── END GAME ────────────────────────────────

function endGame() {
  const total = state.totalScore;
  const entry = {
    score: total,
    date:  new Date().toLocaleDateString('fr-FR'),
    name:  'Barman',
  };

  state.leaderboard.push(entry);
  state.leaderboard.sort((a, b) => b.score - a.score);
  state.leaderboard = state.leaderboard.slice(0, 5);

  try { localStorage.setItem('tpm_leaderboard_v2', JSON.stringify(state.leaderboard)); }
  catch(e) {}

  document.getElementById('end-title').textContent = '🏆 Partie terminée !';

  const fs = document.getElementById('final-score-div');
  fs.style.display = 'block';
  fs.innerHTML = 'Score final<span>' + total + ' pts</span>';

  renderLeaderboard();
  show('end-screen');
}

function renderLeaderboard() {
  const ll = document.getElementById('lb-list');
  const lb = state.leaderboard;
  const medals = ['🥇', '🥈', '🥉', '4.', '5.'];

  if (lb.length === 0) {
    ll.innerHTML = '<p style="text-align:center;color:#aaa;font-size:13px;padding:20px 0">Aucun score encore.<br>Joue ta première partie !</p>';
    return;
  }

  ll.innerHTML = lb.map((e, i) => `
    <div class="lb-row">
      <span class="lb-rank">${medals[i] || (i + 1) + '.'}</span>
      <span class="lb-name">${e.name || 'Barman'}</span>
      <span class="lb-date">${e.date || ''}</span>
      <span class="lb-pts">${e.score} pts</span>
    </div>
  `).join('');
}

// ─── UTILITIES ───────────────────────────────

function shuffleAndPick(arr, n) {
  return [...arr].sort(() => Math.random() - 0.5).slice(0, n);
}

function animateCounter(id, from, to, duration) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = 'score-anim';
  const start = performance.now();
  function frame(now) {
    const t = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    el.textContent = Math.round(from + (to - from) * ease) + ' pts';
    if (t < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

// ─── START ───────────────────────────────────
init();
