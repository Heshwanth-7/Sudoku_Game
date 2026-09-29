"use strict";
const $ = (id) => document.getElementById(id);
let game = null;          // latest state from the backend (+ id)
let sel = null;           // [row, col] of selected cell
let wrong = new Set();    // cells flagged by "Check"
let clock = { base: 0, at: 0 };

async function api(path, method = "GET", body) {
  const res = await fetch("/api" + path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

function say(text, kind = "") { const m = $("msg"); m.textContent = text; m.className = kind; }
const key = (r, c) => r * 9 + c;

function setGame(data) {
  game = { ...game, ...data };
  clock = { base: data.elapsed, at: performance.now() };
  render();
}

async function newGame() {
  say("Generating puzzle...");
  try {
    const data = await api("/games", "POST", { difficulty: $("level").value });
    game = null; wrong.clear(); sel = null;
    setGame(data);
    try { localStorage.setItem("sudoku-id", data.id); } catch (e) {}
    $("analysis").innerHTML = '<dd class="muted">Click "Analyse" to load</dd>';
    say("Good luck!");
    refreshLog();
  } catch (e) { say(e.message, "err"); }
}

function render() {
  const board = $("board");
  board.innerHTML = "";
  const selVal = sel ? game.board[sel[0]][sel[1]] : 0;
  const conflicts = new Set(game.conflicts.map(([r, c]) => key(r, c)));
  for (let r = 0; r < 9; r++) {
    for (let c = 0; c < 9; c++) {
      const v = game.board[r][c];
      const b = document.createElement("button");
      b.className = "cell";
      b.textContent = v || "";
      b.setAttribute("role", "gridcell");
      b.setAttribute("aria-label", `Row ${r + 1} column ${c + 1}${v ? ", " + v : ", empty"}`);
      if (game.puzzle[r][c]) b.classList.add("given");
      if (c % 3 === 2 && c < 8) b.classList.add("bR");
      if (r % 3 === 2 && r < 8) b.classList.add("bB");
      if (sel) {
        const [sr, sc] = sel;
        const samebox = Math.floor(sr / 3) === Math.floor(r / 3) && Math.floor(sc / 3) === Math.floor(c / 3);
        if (sr === r || sc === c || samebox) b.classList.add("peer");
        if (selVal && v === selVal) b.classList.add("same");
        if (sr === r && sc === c) b.classList.add("sel");
      }
      if (conflicts.has(key(r, c)) && !game.puzzle[r][c]) b.classList.add("conflict");
      if (wrong.has(key(r, c))) b.classList.add("wrong");
      b.onclick = () => { sel = [r, c]; render(); };
      board.appendChild(b);
    }
  }
  $("undo").disabled = !game.can_undo || game.solved;
  $("redo").disabled = !game.can_redo || game.solved;
  $("hint").disabled = game.solved;
  $("check").disabled = game.solved;
  $("solve").disabled = game.solved;

  const rows = [["Difficulty", game.difficulty], ["Moves", game.moves], ["Mistakes", game.mistakes],
                ["Hints used", game.hints], ["Undos", game.undos]];
  $("stats").innerHTML = rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");

  if (game.solved && !game.finishedShown) {
    game.finishedShown = true;
    say(game.revealed ? "Solution revealed." : "Solved! Well done!", game.revealed ? "" : "ok");
    loadAnalysis();
  }
}

async function act(fn) {
  try { await fn(); } catch (e) { say(e.message, "err"); }
}

async function place(v) {
  if (!sel || game.solved) return;
  await act(async () => {
    const [r, c] = sel;
    if (game.puzzle[r][c]) throw new Error("That cell is part of the puzzle.");
    if (game.board[r][c] === v) return;
    wrong.delete(key(r, c));
    setGame(await api(`/games/${game.id}/move`, "POST", { row: r, col: c, value: v }));
    say("");
    refreshLog();
  });
}

async function simple(action, okText) {
  await act(async () => {
    wrong.clear();
    const data = await api(`/games/${game.id}/${action}`, "POST");
    setGame(data);
    if (data.hint) {
      sel = [data.hint.row, data.hint.col];
      render();
      say(`Hint: row ${data.hint.row + 1}, column ${data.hint.col + 1} is ${data.hint.value}`, "ok");
    } else say(okText);
    refreshLog();
  });
}

async function checkBoard() {
  await act(async () => {
    const { wrong: w } = await api(`/games/${game.id}/check`);
    wrong = new Set(w.map(([r, c]) => key(r, c)));
    render();
    say(w.length ? `${w.length} wrong cell(s) marked.` : "Everything filled in is correct so far.",
        w.length ? "err" : "ok");
  });
}

async function loadAnalysis() {
  await act(async () => {
    const a = await api(`/games/${game.id}/analysis`);
    $("analysis").innerHTML = Object.entries(a).map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
  });
}

async function refreshLog() {
  try {
    const log = await api(`/games/${game.id}/history`);
    $("log").innerHTML = log.slice().reverse().slice(0, 30).map((m) =>
      `<li>${m.kind}: r${m.row + 1} c${m.col + 1} ${m.old || "empty"} &rarr; ${m.new || "empty"}</li>`).join("");
  } catch (e) {}
}

function tick() {
  if (!game) return;
  const s = game.solved ? clock.base : clock.base + (performance.now() - clock.at) / 1000;
  const t = Math.floor(s);
  $("timer").textContent = String(Math.floor(t / 60)).padStart(2, "0") + ":" + String(t % 60).padStart(2, "0");
}

document.addEventListener("keydown", (e) => {
  if (!game || e.target.tagName === "SELECT") return;
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") { e.preventDefault(); $("undo").click(); return; }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y") { e.preventDefault(); $("redo").click(); return; }
  if (/^[1-9]$/.test(e.key)) place(Number(e.key));
  else if (["0", "Backspace", "Delete"].includes(e.key)) place(0);
  else if (e.key.startsWith("Arrow")) {
    e.preventDefault();
    const [r, c] = sel || [0, 0];
    const d = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] }[e.key];
    sel = [Math.min(8, Math.max(0, r + d[0])), Math.min(8, Math.max(0, c + d[1]))];
    render();
  }
});

// buttons
$("pad").innerHTML = [1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => `<button data-n="${n}">${n}</button>`).join("");
$("pad").onclick = (e) => { const n = e.target.dataset.n; if (n) place(Number(n)); };
$("new").onclick = newGame;
$("undo").onclick = () => simple("undo", "Undone.");
$("redo").onclick = () => simple("redo", "Redone.");
$("hint").onclick = () => simple("hint");
$("check").onclick = checkBoard;
$("analyse").onclick = loadAnalysis;
$("solve").onclick = () => confirm("Reveal the solution and end this game?") && simple("solve", "Solution revealed.");
setInterval(tick, 500);

// resume the last game if the server still has it
(async () => {
  let id = null;
  try { id = localStorage.getItem("sudoku-id"); } catch (e) {}
  if (id) {
    try {
      game = null;
      setGame({ id, ...(await api(`/games/${id}`)) });
      $("level").value = game.difficulty;
      refreshLog();
      return;
    } catch (e) {}
  }
  newGame();
})();
