const SIZE = 5;
const MAX_TURNS = 12;
const TARGET_SCORE = 6;
const TILE = 100;
const CONTROL_POINTS = [
  [2, 2],
  [1, 3],
  [3, 1],
];

function createUnit(owner, type, x, y) {
  if (type === 'scout') return { owner, type, hp: 6, attack: 2, move: 2, x, y, skillUsed: false };
  return { owner, type, hp: 10, attack: 3, move: 1, x, y, skillUsed: false };
}

function newState() {
  return {
    turn: 1,
    winner: null,
    score: { you: 0, bot: 0 },
    players: {
      you: [createUnit('you', 'scout', 0, 0), createUnit('you', 'bruiser', 0, 1)],
      bot: [createUnit('bot', 'scout', 4, 4), createUnit('bot', 'bruiser', 4, 3)],
    },
    selectedUnit: null,
    selectedTarget: null,
    skillOn: false,
    events: [],
  };
}

const state = newState();
const board = document.getElementById('board');
const ctx = board.getContext('2d');
const scoreEl = document.getElementById('score');
const turnEl = document.getElementById('turn');
const statusEl = document.getElementById('status');
const eventsEl = document.getElementById('events');
const skillBtn = document.getElementById('toggleSkill');

function dist(a, b, x, y) {
  return Math.abs(a - x) + Math.abs(b - y);
}

function legalMoves(unit) {
  const moves = [];
  for (let x = 0; x < SIZE; x += 1) {
    for (let y = 0; y < SIZE; y += 1) {
      if (dist(unit.x, unit.y, x, y) <= unit.move) moves.push([x, y]);
    }
  }
  return moves;
}

function unitAt(owner, x, y) {
  return state.players[owner].find((u) => u.x === x && u.y === y);
}

function enemy(owner) {
  return owner === 'you' ? 'bot' : 'you';
}

function addEvent(text, cls = '') {
  state.events.unshift({ text, cls });
  state.events = state.events.slice(0, 16);
}

function draw() {
  ctx.clearRect(0, 0, board.width, board.height);

  for (let x = 0; x < SIZE; x += 1) {
    for (let y = 0; y < SIZE; y += 1) {
      ctx.fillStyle = (x + y) % 2 === 0 ? '#1a2140' : '#141a33';
      ctx.fillRect(x * TILE, y * TILE, TILE, TILE);
      ctx.strokeStyle = '#33407a';
      ctx.strokeRect(x * TILE, y * TILE, TILE, TILE);
    }
  }

  for (const [x, y] of CONTROL_POINTS) {
    ctx.fillStyle = '#3cc07c';
    ctx.beginPath();
    ctx.arc(x * TILE + TILE / 2, y * TILE + TILE / 2, 12, 0, Math.PI * 2);
    ctx.fill();
  }

  if (state.selectedTarget) {
    const [x, y] = state.selectedTarget;
    ctx.strokeStyle = '#ffd66e';
    ctx.lineWidth = 4;
    ctx.strokeRect(x * TILE + 4, y * TILE + 4, TILE - 8, TILE - 8);
    ctx.lineWidth = 1;
  }

  for (const unit of state.players.you) drawUnit(unit, '#58b7ff');
  for (const unit of state.players.bot) drawUnit(unit, '#ff8c66');

  if (state.selectedUnit != null) {
    const unit = state.players.you[state.selectedUnit];
    if (unit) {
      const moves = legalMoves(unit);
      ctx.fillStyle = 'rgba(255,255,255,0.13)';
      for (const [mx, my] of moves) ctx.fillRect(mx * TILE + 2, my * TILE + 2, TILE - 4, TILE - 4);
      drawUnit(unit, '#8fd2ff');
    }
  }

  scoreEl.textContent = `比分: 你 ${state.score.you} - ${state.score.bot} 机器人`;
  turnEl.textContent = `回合: ${Math.min(state.turn, MAX_TURNS)} / ${MAX_TURNS}`;
  renderEvents();
}

function drawUnit(unit, color) {
  const cx = unit.x * TILE + TILE / 2;
  const cy = unit.y * TILE + TILE / 2;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(cx, cy, 24, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#0f1220';
  ctx.font = 'bold 14px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(unit.type[0].toUpperCase(), cx, cy + 5);
  ctx.fillStyle = '#ffffff';
  ctx.font = '12px sans-serif';
  ctx.fillText(String(unit.hp), cx, cy - 30);
}

function resolveOneAction(owner, unitIndex, tx, ty, useSkill) {
  const units = state.players[owner];
  if (unitIndex < 0 || unitIndex >= units.length) {
    addEvent(`${owner} 行动无效，跳过`, owner);
    return;
  }
  const actor = units[unitIndex];
  if (dist(actor.x, actor.y, tx, ty) <= actor.move) {
    actor.x = tx;
    actor.y = ty;
    addEvent(`${owner} 移动到 (${tx}, ${ty})`, owner);
  } else {
    addEvent(`${owner} 移动失败`, owner);
  }

  const enemyId = enemy(owner);
  const target = unitAt(enemyId, actor.x, actor.y);
  if (target) {
    const bonus = useSkill && !actor.skillUsed ? 1 : 0;
    const damage = actor.attack + bonus;
    target.hp -= damage;
    if (bonus) actor.skillUsed = true;
    addEvent(`${owner} 造成 ${damage} 伤害`, owner);
  }
}

function cleanupDead() {
  for (const pid of ['you', 'bot']) {
    const before = state.players[pid].length;
    state.players[pid] = state.players[pid].filter((u) => u.hp > 0);
    const dead = before - state.players[pid].length;
    if (dead > 0) addEvent(`${pid} 损失 ${dead} 个单位`, pid);
  }
}

function scorePoints() {
  for (const [x, y] of CONTROL_POINTS) {
    const youHold = !!unitAt('you', x, y);
    const botHold = !!unitAt('bot', x, y);
    if (youHold && !botHold) {
      state.score.you += 1;
      addEvent(`你占领据点 (${x}, ${y}) +1`, 'player');
    }
    if (botHold && !youHold) {
      state.score.bot += 1;
      addEvent(`机器人占领据点 (${x}, ${y}) +1`, 'bot');
    }
  }
}

function evaluateWinner() {
  if (state.players.you.length === 0) state.winner = 'bot';
  else if (state.players.bot.length === 0) state.winner = 'you';
  else if (state.score.you >= TARGET_SCORE) state.winner = 'you';
  else if (state.score.bot >= TARGET_SCORE) state.winner = 'bot';
  else if (state.turn > MAX_TURNS) {
    state.winner = state.score.you >= state.score.bot ? 'you' : 'bot';
  }

  if (state.winner) {
    addEvent(`对局结束，胜者：${state.winner === 'you' ? '你' : '机器人'}`, 'win');
    statusEl.textContent = `状态: 游戏结束，${state.winner === 'you' ? '你赢了' : '你输了'}。点击“重新开始”再来一局。`;
  }
}

function botAction() {
  let best = null;
  state.players.bot.forEach((u, i) => {
    legalMoves(u).forEach(([tx, ty]) => {
      let score = 0;
      if (CONTROL_POINTS.some(([cx, cy]) => cx === tx && cy === ty)) score += 6;
      state.players.you.forEach((e) => {
        if (e.x === tx && e.y === ty) score += 7;
        score += Math.max(0, 3 - dist(e.x, e.y, tx, ty));
      });
      if (!best || score > best.score) {
        best = { score, action: { unitIndex: i, tx, ty, useSkill: score >= 8 && !u.skillUsed } };
      }
    });
  });
  return best.action;
}

function renderEvents() {
  eventsEl.innerHTML = '';
  state.events.forEach((e) => {
    const li = document.createElement('li');
    if (e.cls) li.className = e.cls;
    li.textContent = e.text;
    eventsEl.appendChild(li);
  });
}

board.addEventListener('click', (ev) => {
  if (state.winner) return;
  const rect = board.getBoundingClientRect();
  const x = Math.floor(((ev.clientX - rect.left) / rect.width) * SIZE);
  const y = Math.floor(((ev.clientY - rect.top) / rect.height) * SIZE);

  const unitIndex = state.players.you.findIndex((u) => u.x === x && u.y === y);
  if (unitIndex >= 0) {
    state.selectedUnit = unitIndex;
    state.selectedTarget = [x, y];
    statusEl.textContent = `状态: 已选择单位 ${unitIndex}，请点击目标格。`;
    draw();
    return;
  }

  if (state.selectedUnit != null) {
    state.selectedTarget = [x, y];
    statusEl.textContent = `状态: 目标已选择 (${x}, ${y})，点击“确认行动并结束回合”。`;
    draw();
  }
});

document.getElementById('toggleSkill').addEventListener('click', () => {
  state.skillOn = !state.skillOn;
  skillBtn.textContent = `技能加伤: ${state.skillOn ? '开启' : '关闭'}`;
});

document.getElementById('endTurn').addEventListener('click', () => {
  if (state.winner) return;
  if (state.selectedUnit == null || !state.selectedTarget) {
    statusEl.textContent = '状态: 请先选单位和目标格。';
    return;
  }

  addEvent(`第 ${state.turn} 回合结算`, '');
  const [tx, ty] = state.selectedTarget;
  resolveOneAction('you', state.selectedUnit, tx, ty, state.skillOn);
  const bot = botAction();
  resolveOneAction('bot', bot.unitIndex, bot.tx, bot.ty, bot.useSkill);

  cleanupDead();
  scorePoints();

  state.turn += 1;
  state.selectedUnit = null;
  state.selectedTarget = null;
  evaluateWinner();

  if (!state.winner) {
    statusEl.textContent = '状态: 选择一个你的单位，再点击目标格。';
  }
  draw();
});

document.getElementById('restart').addEventListener('click', () => {
  Object.assign(state, newState());
  statusEl.textContent = '状态: 选择一个你的单位，再点击目标格。';
  skillBtn.textContent = '技能加伤: 关闭';
  draw();
});

draw();
