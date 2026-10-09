import "./style.css";

const API_BASE = (import.meta.env.VITE_API_BASE || window.location.origin).replace(/\/$/, "");
const WS_BASE = API_BASE.replace(/^http/, "ws");

const state = {
  screen: "login",
  username: "",
  token: "",
  socket: null,
  socketOpen: false,
  board: Array.from({ length: 3 }, () => Array(3).fill(null)),
  wins: {},
  winner: null,
  winState: null,
  mySymbol: null,
  lastMoverSymbol: null,
  pendingMove: null,
  status: "",
  reconnecting: false,
};

const app = document.querySelector("#app");

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}

function render() {
  if (state.screen === "login") return renderLogin();
  if (state.screen === "waiting") return renderWaiting();
  if (state.screen === "game") return renderGame();
  if (state.screen === "finished") return renderFinished();
}

function shell(content) {
  app.innerHTML = `<main class="layout"><header class="topbar"><a class="brand" href="#" aria-label="Playroom home"><span class="brand-mark"><i></i><i></i><i></i><i></i></span><span>playroom</span></a><div class="top-meta"><span class="online-dot"></span> Multiplayer <span class="meta-divider">·</span> Tic Tac Toe</div></header>${content}<footer>Made for good games <span>✳</span></footer></main>`;
}

function renderLogin(error = "") {
  state.screen = "login";
  shell(`<section class="login-wrap"><div class="login-art"><div class="art-label">THE CLASSIC, REMIXED</div><h1>A little<br>friendly<br><em>competition.</em></h1><p>Three in a row. One worthy rival.<br>Let’s see what you’ve got.</p><div class="art-board"><span class="art-x">×</span><span></span><span class="art-o">○</span><span></span><span class="art-x">×</span><span></span><span></span><span class="art-o">○</span><span></span></div><span class="art-spark spark-one">✳</span><span class="art-spark spark-two">✳</span></div><div class="login-card"><div class="eyebrow">YOUR NEXT REMATCH STARTS HERE</div><h2>Welcome back</h2><p class="muted">Sign in and find someone to play.</p><form id="login-form"><label for="identifier">Username or email</label><input id="identifier" name="identifier" autocomplete="username" placeholder="e.g. alex" required><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" placeholder="Your password" required>${error ? `<div class="form-error" role="alert">${escapeHtml(error)}</div>` : ""}<button class="button primary full" type="submit"><span>Let’s play</span><span>↗</span></button></form><div class="secure-note"><span>✳</span> Your game, your move. Always.</div></div></section>`);
  document.querySelector("#login-form").addEventListener("submit", login);
}

async function login(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const button = event.currentTarget.querySelector("button");
  button.disabled = true;
  button.innerHTML = '<span>Signing in…</span><span class="spinner"></span>';
  try {
    const response = await fetch(`${API_BASE}/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier: form.get("identifier"), password: form.get("password") }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Could not sign in. Check your details and try again.");
    state.token = data.access_token;
    state.username = String(form.get("identifier"));
    connect();
  } catch (error) {
    renderLogin(error.message || "Could not reach the game server.");
  }
}

function connect() {
  state.screen = "waiting";
  state.status = "Connecting to matchmaking…";
  renderWaiting();
  const socket = new WebSocket(`${WS_BASE}/v1/play/join?token=${encodeURIComponent(state.token)}`);
  state.socket = socket;
  socket.addEventListener("open", () => {
    state.socketOpen = true;
    state.status = "You’re in the queue. We’ll show the board as soon as the server sends a game update.";
    if (state.screen === "waiting") renderWaiting();
  });
  socket.addEventListener("message", (event) => {
    let data;
    try { data = JSON.parse(event.data); } catch { return; }
    if (data.event === "board_update" || data.event === "finished") {
      const previousBoard = state.board.map((row) => [...row]);
      state.board = Array.isArray(data.board) ? data.board : state.board;
      const occupied = state.board.flat().filter(Boolean).length;
      if (data.wins) state.wins = data.wins;
      if (state.pendingMove) {
        const [row, col] = state.pendingMove;
        const symbol = state.board[row]?.[col];
        if (symbol) {
          state.mySymbol = symbol;
          state.lastMoverSymbol = symbol;
        }
        state.pendingMove = null;
      } else if (occupied) {
        let changedSymbol = null;
        for (let row = 0; row < 3; row++) for (let col = 0; col < 3; col++) {
          if (state.board[row]?.[col] && state.board[row][col] !== previousBoard[row]?.[col]) changedSymbol = state.board[row][col];
        }
        state.lastMoverSymbol = changedSymbol || state.lastMoverSymbol;
        if (!state.mySymbol && changedSymbol) state.mySymbol = changedSymbol === "X" ? "O" : "X";
      }
      if (data.event === "finished") {
        state.winner = data.winner;
        state.winState = data.win_state;
        if (data.winner && data.winner !== "draw") state.wins[data.winner] = (state.wins[data.winner] || 0) + 1;
        state.screen = "finished";
        renderFinished();
      } else {
        state.screen = "game";
        renderGame();
      }
    }
  });
  socket.addEventListener("error", () => {
    state.status = "Couldn’t connect to the game server. Check that it’s running and try again.";
    if (state.screen === "waiting") renderWaiting();
  });
  socket.addEventListener("close", (event) => {
    state.socketOpen = false;
    if (state.screen === "login") return;
    if (event.code === 1008) {
      state.socket = null;
      renderLogin("Your session was rejected. Please sign in again.");
      return;
    }
    state.reconnecting = true;
    state.status = "Connection lost. Your opponent may have left, or the server may be unavailable.";
    if (state.screen === "game" || state.screen === "waiting") renderConnectionIssue();
  });
}

function renderWaiting() {
  state.screen = "waiting";
  shell(`<section class="state-card"><div class="waiting-icon"><span class="orbit orbit-a"></span><span class="orbit orbit-b"></span><span class="waiting-mark">×<small>○</small></span></div><div class="eyebrow">MATCHMAKING</div><h1>Finding your rival</h1><p class="muted">${escapeHtml(state.status)}</p><div class="waiting-pill"><span class="pulse"></span> Looking for a player</div>${state.socketOpen ? '<button class="button primary" id="open-board">Open the board <span>↗</span></button>' : ""}<button class="button quiet" id="cancel-queue">Cancel</button><p class="series-note">The server doesn’t send a match-found notice. Open the board when you’re ready; the server will validate your move.</p></section>`);
  document.querySelector("#open-board")?.addEventListener("click", () => { state.screen = "game"; renderGame(); });
  document.querySelector("#cancel-queue").addEventListener("click", disconnectToLogin);
}

function scoreEntries() {
  const entries = Object.entries(state.wins);
  return entries.length ? entries : [[state.username, 0], ["Opponent", 0]];
}

function currentTurn() {
  if (!state.mySymbol) return "Waiting for the first move";
  const toMove = state.lastMoverSymbol === "X" ? "O" : state.lastMoverSymbol === "O" ? "X" : state.mySymbol;
  return toMove ? (toMove === state.mySymbol ? "Your turn" : "Opponent’s turn") : "Your turn";
}

function boardHtml(disabled = false) {
  return `<div class="board" role="grid" aria-label="Tic Tac Toe board">${state.board.flatMap((row, r) => row.map((cell, c) => {
    const winning = isWinningCell(r, c);
    return `<button class="cell ${cell ? `symbol-${cell.toLowerCase()}` : ""} ${winning ? "winning" : ""}" role="gridcell" aria-label="Row ${r + 1}, column ${c + 1}${cell ? `, ${cell}` : ", empty"}" data-row="${r}" data-col="${c}" ${disabled || cell ? "disabled" : ""}>${cell === "X" ? "×" : cell === "O" ? "○" : ""}</button>`;
  })).join("")}</div>`;
}

function isWinningCell(row, col) {
  const win = state.winState;
  if (!win || !win.direction) return false;
  if (win.direction === "H") return row === win.idx;
  if (win.direction === "V") return col === win.idx;
  if (win.direction === "RD") return row === col;
  if (win.direction === "LD") return row + col === 2;
  return false;
}

function renderGame() {
  state.screen = "game";
  const scores = scoreEntries();
  const turn = currentTurn();
  shell(`<section class="game-shell"><div class="game-heading"><div><div class="eyebrow">SERIES IN PROGRESS</div><h1>Make your move.</h1></div><div class="live-badge"><span class="pulse"></span> LIVE MATCH</div></div><div class="match-layout"><aside class="score-panel"><div class="score-title">SERIES SCORE <span>↗</span></div>${scores.map(([name, score], index) => `<div class="player-row"><div class="player-avatar ${index ? "avatar-coral" : "avatar-lilac"}">${escapeHtml(String(name).slice(0, 1).toUpperCase())}</div><div class="player-info"><strong>${escapeHtml(name)}</strong><small>Series player</small></div><b class="score-number">${score}</b></div>`).join("")}<div class="score-footnote">Wins are counted from completed games.</div></aside><div class="board-panel"><div class="turn-label"><span class="turn-dot"></span>${escapeHtml(turn)}</div>${boardHtml(false)}<div class="board-hint">Choose an empty square to play</div></div><aside class="game-note"><span class="note-icon">✳</span><h3>Good games<br>start here.</h3><p>The server confirms every move and keeps the official score.</p><button class="text-button" id="leave-game">Leave game <span>↗</span></button></aside></div></section>`);
  document.querySelectorAll(".cell:not(:disabled)").forEach((button) => button.addEventListener("click", sendMove));
  document.querySelector("#leave-game").addEventListener("click", disconnectToLogin);
}

function sendMove(event) {
  if (!state.socket || state.socket.readyState !== WebSocket.OPEN) return;
  const row = Number(event.currentTarget.dataset.row);
  const col = Number(event.currentTarget.dataset.col);
  state.pendingMove = [row, col];
  state.socket.send(JSON.stringify({ row, col }));
  state.status = "Move sent. Waiting for the server…";
  event.currentTarget.disabled = true;
  event.currentTarget.classList.add("pending");
}

function renderFinished() {
  state.screen = "finished";
  const draw = !state.winner || state.winner === "draw";
  shell(`<section class="state-card finished-card"><div class="finish-stamp ${draw ? "stamp-draw" : "stamp-win"}">${draw ? "↔" : "✳"}</div><div class="eyebrow">GAME COMPLETE</div><h1>${draw ? "A perfect draw." : "Game complete."}</h1><p class="muted">${draw ? "No one takes this round. Ready for another?" : `${escapeHtml(state.winner)} takes this round.`}</p><div class="final-score">${scoreEntries().map(([name, score]) => `<div><span>${escapeHtml(name)}</span><strong>${score}</strong></div>`).join("")}</div><div class="finish-actions"><button class="button primary" id="next-match">Find another match <span>↗</span></button><button class="button quiet" id="finish-leave">Done for now</button></div><p class="series-note">Your series score is shown from server game results.</p></section>`);
  document.querySelector("#next-match").addEventListener("click", startNextGame);
  document.querySelector("#finish-leave").addEventListener("click", disconnectToLogin);
}

function renderConnectionIssue() {
  shell(`<section class="state-card"><div class="finish-stamp stamp-draw">!</div><div class="eyebrow">CONNECTION INTERRUPTED</div><h1>Game paused</h1><p class="muted">${escapeHtml(state.status)}</p><div class="finish-actions"><button class="button primary" id="reconnect">Reconnect</button><button class="button quiet" id="back-login">Back to sign in</button></div></section>`);
  document.querySelector("#reconnect").addEventListener("click", reconnect);
  document.querySelector("#back-login").addEventListener("click", disconnectToLogin);
}

function reconnect() {
  if (state.socket && state.socket.readyState < WebSocket.CLOSING) state.socket.close();
  state.board = Array.from({ length: 3 }, () => Array(3).fill(null));
  state.winner = null;
  state.winState = null;
  state.mySymbol = null;
  state.lastMoverSymbol = null;
  state.pendingMove = null;
  connect();
}

function startNextGame() {
  state.board = Array.from({ length: 3 }, () => Array(3).fill(null));
  state.winner = null;
  state.winState = null;
  state.mySymbol = null;
  state.lastMoverSymbol = null;
  state.pendingMove = null;
  state.screen = "game";
  renderGame();
}

function disconnectToLogin() {
  if (state.socket && state.socket.readyState < WebSocket.CLOSING) state.socket.close();
  state.socket = null;
  state.token = "";
  state.wins = {};
  renderLogin();
}

renderLogin();
