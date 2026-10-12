"use strict";
const $ = (id) => document.getElementById(id);
const suits = { Copas: "♥", Ouros: "♦", Paus: "♣", Espadas: "♠" };
const fmt = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });
const signed = (n) => `${n > 0 ? "+" : ""}${fmt.format(n)}`;
const esc = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
let state = null,
  busy = false,
  assetVersion = null;
const actions = {
  pedir: ["Pedir carta", "P"],
  parar: ["Parar", "S"],
  dobrar: ["Dobrar", "D"],
  dividir: ["Dividir", ""],
  desistir: ["Desistir", ""],
  segurar: ["Fazer seguro", ""],
  recusar_seguro: ["Sem seguro", ""],
};
function cardHTML(c, i = 0) {
  if (c.oculta)
    return `<div class="card back" style="--i:${i}" role="img" aria-label="Carta oculta"><svg><use href="#crown"/></svg></div>`;
  if (c.ghost)
    return '<div class="card ghost" aria-hidden="true"><svg><use href="#crown"/></svg></div>';
  const red = ["Copas", "Ouros"].includes(c.naipe);
  const face = ["J", "Q", "K"].includes(c.valor);
  const corner = `<span>${esc(c.valor)}</span><small>${suits[c.naipe]}</small>`;
  return `<div class="card${red ? " red" : ""}" style="--i:${i}" role="img" aria-label="${esc(c.valor)} de ${esc(c.naipe)}"><span class="card-corner">${corner}</span><span class="card-suit${face ? " face" : ""}"><span>${face ? esc(c.valor) : suits[c.naipe]}</span></span><span class="card-corner bottom">${corner}</span></div>`;
}
function cards(container, list) {
  const signature = JSON.stringify(list);
  if (container.dataset.cards === signature) return;
  const old = [...container.children];
  const fragment = document.createDocumentFragment();
  list.forEach((c, i) => {
    const key = JSON.stringify(c);
    let node = old.find((el) => el.dataset.key === key);
    if (node) old.splice(old.indexOf(node), 1);
    else {
      const template = document.createElement("template");
      template.innerHTML = cardHTML(c, i);
      node = template.content.firstElementChild;
      node.dataset.key = key;
    }
    fragment.append(node);
  });
  container.replaceChildren(fragment);
  container.dataset.cards = signature;
  container.classList.toggle("many", list.length >= 5);
}
function historyHTML() {
  if (!state?.historico?.length)
    return '<div class="history-empty">As cartas ainda guardam seus segredos.<br>Sua primeira rodada abre esta crônica.</div>';
  return state.historico
    .map(
      (h) =>
        `<div class="history-entry"><div><span class="eyebrow">RODADA ${String(h.rodada).padStart(2, "0")}</span><strong class="${h.fichas >= 0 ? "positive" : "negative"}">${signed(h.fichas)} fichas</strong></div><small>${h.placar > 0 ? "Vitória" : h.placar < 0 ? "Derrota" : "Empate"} · ${signed(h.prestigio)} de prestígio</small></div>`,
    )
    .join("");
}
function info(title, content) {
  $("info-content").innerHTML =
    `<div class="eyebrow">COUNT & QUEEN</div><h2>${esc(title)}</h2>${content}`;
  if (!$("info-dialog").open) $("info-dialog").showModal();
}
function inventory() {
  const items = state?.jogador?.itens || [];
  const affinity = Object.entries(state?.jogador?.afinidades || {});
  info(
    "Relíquias & afinidades",
    `<div class="help-copy">${items.length ? items.map((i) => `<article class="relic-detail"><h3>${esc(i.nome)}</h3><p>${esc(i.descricao)}</p></article>`).join("") : "<p>Seu inventário ainda está vazio.</p>"}<h3>Afinidades</h3>${affinity.length ? affinity.map(([c, n]) => `<p>Carta ${esc(c)} · nível ${Math.min(5, n)} · +${Math.min(5, n) * 15}% de lucro</p>`).join("") : "<p>Você ainda não formou uma afinidade com as cartas.</p>"}<p class="note">Esta primeira mesa visual inclui as rodadas e a progressão até a coroa. As visitas às lojas e os eventos da campanha ainda serão trazidos para esta interface.</p></div>`,
  );
}
function render() {
  if (!state) return;
  const j = state.jogador;
  $("history").innerHTML = historyHTML();
  $("relics").innerHTML = j?.itens.length
    ? j.itens
        .map(
          (i) =>
            `<button class="relic" title="${esc(i.descricao)}">◇ &nbsp; ${esc(i.nome)}</button>`,
        )
        .join("")
    : '<div class="relic-empty"><svg><use href="#diamond"/></svg><p>Um destino por descobrir</p><small>As relíquias que acompanham<br>sua jornada aparecem aqui.</small></div>';
  $("relics")
    .querySelectorAll("button")
    .forEach((b) => b.addEventListener("click", inventory));
  if (!j) {
    cards($("dealer-cards"), [{ ghost: true }, { ghost: true }]);
    $("player-hands").innerHTML =
      `<div class="player-hand"><div class="cards">${cardHTML({ ghost: true })}${cardHTML({ ghost: true })}</div><div class="hand-score">SEU LUGAR À MESA</div></div>`;
    $("deal").disabled = true;
    if (!$("welcome").open) $("welcome").showModal();
    return;
  }
  if ($("welcome").open) $("welcome").close();
  $("player-name").textContent = j.nome;
  $("player-title").textContent = j.titulo;
  $("path-label").innerHTML =
    `<span></span> Caminho da ${j.caminho === "tirania" ? "Tirania" : "Nobreza"}`;
  $("balance").textContent = fmt.format(j.fichas);
  $("prestige").innerHTML =
    `${fmt.format(j.prestigio)} <small>/ 10.000</small>`;
  $("progress").value = Math.max(
    0,
    j.caminho === "tirania" ? -j.prestigio : j.prestigio,
  );
  $("progress-caption").textContent = j.coroacao_ativa
    ? `Coroação: ${j.vitorias}/3 vitórias · ${j.derrotas}/3 derrotas`
    : "Cada vitória escreve a sua lenda.";
  $("save-status").textContent = busy
    ? "Salvando sua jornada…"
    : "Jornada salva automaticamente";
  $("chapter").textContent = state.cenario[0];
  $("dealer-name").textContent = state.cenario[1];
  $("dealer-rule").textContent = `Para em ${state.cenario[2]}`;
  const chapters = [
    "Taverna da Fronteira",
    "Torneio do Castelo",
    "Salão dos Nobres",
    "Corte Real",
    "Disputa pela Coroa",
  ];
  const chapter = chapters.indexOf(state.cenario[0]);
  $("table").dataset.chapter = chapter;
  $("chapter-label").textContent = [
    "CAPÍTULO I · A FRONTEIRA",
    "CAPÍTULO II · O CASTELO",
    "CAPÍTULO III · A NOBREZA",
    "CAPÍTULO IV · A CORTE",
    "CAPÍTULO V · A COROA",
  ][chapter];
  [...$("route").children].forEach((li, i) => {
    li.classList.toggle("current", i === chapter);
    li.classList.toggle("passed", i < chapter);
  });
  $("round").textContent = String(
    state.contador + (state.fase === "resultado" ? 0 : 1),
  ).padStart(2, "0");
  const betting = state.fase === "aposta";
  const showCards = !betting && state.dealer.length;
  cards(
    $("dealer-cards"),
    showCards ? state.dealer : [{ ghost: true }, { ghost: true }],
  );
  $("dealer-score").textContent = showCards
    ? state.dealer_valor === null
      ? "CARTA OCULTA"
      : `${state.dealer_valor} PONTOS${state.dealer_valor > 21 ? " · ESTOUROU" : ""}`
    : "UMA CARTA, UM DESTINO";
  $("player-hands").classList.toggle(
    "split",
    showCards && state.maos.length > 1,
  );
  const hands = showCards
    ? state.maos
    : [{ cartas: [{ ghost: true }, { ghost: true }], valor: 0 }];
  while ($("player-hands").children.length > hands.length)
    $("player-hands").lastElementChild.remove();
  hands.forEach((m, i) => {
    let el = $("player-hands").children[i];
    if (!el) {
      el = document.createElement("div");
      el.className = "player-hand";
      el.innerHTML = '<div class="cards"></div><div class="hand-score"></div>';
      $("player-hands").append(el);
    }
    el.classList.toggle(
      "active",
      state.fase === "jogando" && state.indice === i,
    );
    cards(el.querySelector(".cards"), m.cartas);
    let score = showCards
      ? m.valor === -1
        ? "DESISTÊNCIA"
        : `${m.valor} PONTOS${m.e_blackjack ? " · BLACKJACK" : m.valor > 21 ? " · ESTOUROU" : ""}`
      : "SUA PRÓXIMA MÃO";
    if (hands.length > 1) score = `MÃO ${i + 1} · ${score}`;
    if (state.fase === "resultado" && state.resultados[i])
      score += ` · ${state.resultados[i].texto.toUpperCase()}`;
    el.querySelector(".hand-score").textContent = score;
  });
  $("table-bet").hidden = !showCards;
  $("table-bet").textContent =
    `♜ ${fmt.format(state.maos.reduce((n, m) => n + m.aposta, 0))} em jogo`;
  $("bet-form").hidden = !betting || !!state.fim;
  $("actions").hidden = !["jogando", "seguro"].includes(state.fase);
  $("result").hidden = state.fase !== "resultado" && !state.fim;
  $("oracle").hidden = state.fase !== "oraculo";
  $("bet").max = Math.floor(j.fichas);
  if (betting && (!Number($("bet").value) || Number($("bet").value) > j.fichas))
    $("bet").value = Math.max(
      1,
      Math.min(j.ultima_aposta, Math.floor(j.fichas)),
    );
  $("deal").disabled = busy;
  $("bet").disabled = busy;
  $("bet-form")
    .querySelectorAll("[data-bet]")
    .forEach((b) => {
      b.disabled =
        busy || (b.dataset.bet !== "all" && Number(b.dataset.bet) > j.fichas);
      b.classList.toggle("selected", b.dataset.bet === String($("bet").value));
    });
  if (state.fase === "jogando") {
    $("status").textContent =
      state.maos.length > 1
        ? `Sua vez · mão ${state.indice + 1} de ${state.maos.length}.`
        : "Sua vez. A próxima carta pode mudar tudo.";
    $("actions").innerHTML = Object.entries(actions)
      .filter(([a]) => !["segurar", "recusar_seguro"].includes(a))
      .map(
        ([a, [label, key]]) =>
          `<button class="action-button ${a === "pedir" ? "primary" : a === "desistir" ? "secondary" : ""}" data-action="${a}" ${busy || !state.acoes.includes(a) ? "disabled" : ""}>${label}${key ? `<kbd>${key}</kbd>` : ""}</button>`,
      )
      .join("");
  } else if (state.fase === "seguro") {
    $("status").textContent =
      `O adversário mostra um Ás. Seguro: ${fmt.format(state.maos[0].aposta / 2)} fichas.`;
    $("actions").innerHTML = ["segurar", "recusar_seguro"]
      .map(
        (a) =>
          `<button class="action-button" data-action="${a}" ${busy ? "disabled" : ""}>${actions[a][0]}</button>`,
      )
      .join("");
  } else if (state.fase === "oraculo") {
    $("status").textContent =
      "O Caleidoscópio revela três caminhos. Escolha sua carta.";
    $("oracle").innerHTML =
      `<div class="cards">${state.escolhas.map((c, i) => `<button class="oracle-choice" data-choice="${i}" aria-label="Escolher ${esc(c.valor)} de ${esc(c.naipe)}" ${busy ? "disabled" : ""}>${cardHTML(c, i)}</button>`).join("")}</div>`;
    $("oracle")
      .querySelectorAll("button")
      .forEach((b) =>
        b.addEventListener("click", () =>
          act("escolher", Number(b.dataset.choice)),
        ),
      );
  } else if (state.fase === "resultado" || state.fim) {
    const r = state.resumo;
    let title =
      state.resultados.length === 1
        ? state.resultados[0].texto
        : r?.placar > 0
          ? "A rodada é sua."
          : r?.placar < 0
            ? "A mesa levou a melhor."
            : "Honras divididas.";
    if (state.fim === "vitoria") title = "A coroa é sua.";
    if (state.fim === "falencia") title = "Uma lenda chega ao fim.";
    $("status").textContent =
      state.fim === "vitoria"
        ? "O Regente entrega a coroa. Seu reinado começa."
        : state.fim === "falencia"
          ? "Suas fichas acabaram. Uma nova história espera por você."
          : "Rodada encerrada. Seu destino segue em suas mãos.";
    let detail = r
      ? `<span class="${r.fichas >= 0 ? "positive" : "negative"}">${signed(r.fichas)} fichas</span> &nbsp;·&nbsp; ${signed(r.prestigio)} de prestígio`
      : "";
    if (r?.tributo)
      detail += `<br>Inclui ${fmt.format(r.tributo)} fichas do Manto da Nobreza.`;
    if (r?.desfecho === "inicio")
      detail +=
        "<br>O Regente aceita seu desafio: vença três rodadas antes de perder três.";
    if (r?.desfecho === "recuo")
      detail +=
        "<br>O Regente defendeu a coroa. Reúna prestígio e tente novamente.";
    $("result").innerHTML =
      `<div><h3>${title}</h3><p>${detail}</p></div><button class="primary" id="next" ${busy ? "disabled" : ""}>${state.fim ? "Nova lenda" : "Próxima rodada"} <span>→</span></button>`;
    $("next").addEventListener("click", () =>
      state.fim ? $("welcome").showModal() : act("continuar"),
    );
  } else
    $("status").textContent =
      "Escolha sua aposta. A sorte espera pelo primeiro movimento.";
  $("actions")
    .querySelectorAll("[data-action]")
    .forEach((b) => b.addEventListener("click", () => act(b.dataset.action)));
}
async function act(acao, valor, extra = {}) {
  if (busy || !state) return;
  busy = true;
  $("error").hidden = true;
  $("welcome-error").hidden = true;
  document.querySelectorAll("button").forEach((b) => (b.disabled = true));
  try {
    const response = await fetch("/api/acao", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ acao, valor, revisao: state.revisao, ...extra }),
    });
    const data = await response.json();
    if (!response.ok)
      throw new Error(data.erro || "Não foi possível concluir a ação.");
    state = data;
  } catch (e) {
    const target = $("welcome").open ? $("welcome-error") : $("error");
    target.textContent =
      e.message === "Failed to fetch"
        ? "A conexão com a mesa foi interrompida. Seu último movimento salvo será retomado ao reconectar."
        : e.message;
    target.hidden = false;
    try {
      const response = await fetch("/api/estado");
      if (response.ok) state = await response.json();
    } catch (_) {}
  } finally {
    busy = false;
    document.querySelectorAll("button").forEach((b) => (b.disabled = false));
    render();
  }
}
$("bet-form").addEventListener("submit", (e) => {
  e.preventDefault();
  act("apostar", Number($("bet").value));
});
$("bet-form")
  .querySelectorAll("[data-bet]")
  .forEach((b) =>
    b.addEventListener("click", () => {
      $("bet").value =
        b.dataset.bet === "all"
          ? Math.floor(state.jogador.fichas)
          : b.dataset.bet;
      render();
    }),
  );
$("new-game-form").addEventListener("submit", (e) => {
  e.preventDefault();
  act("nova", null, { nome: $("name").value, genero: $("gender").value });
});
$("welcome").addEventListener("cancel", (e) => {
  if (!state?.jogador) e.preventDefault();
});
$("inventory-button").addEventListener("click", inventory);
$("history-button").addEventListener("click", () =>
  info("Crônica da mesa", historyHTML()),
);
$("help-button").addEventListener("click", () =>
  info(
    "A arte do vinte e um",
    `<div class="help-copy"><p>Chegue o mais perto de <strong>21</strong> sem ultrapassar. Figuras valem 10; o Ás vale 1 ou 11.</p><ul><li><strong>Pedir (P):</strong> receba outra carta.</li><li><strong>Parar (S):</strong> mantenha sua mão e passe a vez.</li><li><strong>Dobrar (D):</strong> dobre a aposta, receba uma carta e encerre sua mão.</li><li><strong>Dividir:</strong> transforme um par em duas mãos, pagando outra aposta. Até quatro mãos.</li><li><strong>Desistir:</strong> devolve metade da aposta inicial e custa prestígio.</li></ul><p>Um Ás e uma carta de valor 10 na distribuição inicial formam <strong>blackjack</strong> e pagam 3:2. Um 21 após divisão é uma mão comum. Empates devolvem a aposta.</p><p>Alcance <strong>10.000 de prestígio</strong> e vença três rodadas contra o Regente antes de perder três para conquistar a coroa.</p><p class="note">Primeira versão visual: mesa, ações e coroação. Lojas e eventos da campanha serão adicionados em uma próxima etapa. A jornada visual tem seu próprio salvamento.</p></div>`,
  ),
);
$("info-dialog")
  .querySelector(".dialog-close")
  .addEventListener("click", () => $("info-dialog").close());
document.addEventListener("keydown", (e) => {
  if (
    e.ctrlKey ||
    e.metaKey ||
    e.altKey ||
    e.repeat ||
    busy ||
    document.querySelector("dialog[open]") ||
    ["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement.tagName)
  )
    return;
  const action = { p: "pedir", s: "parar", d: "dobrar" }[e.key.toLowerCase()];
  if (action && state?.acoes?.includes(action)) {
    e.preventDefault();
    act(action);
  }
  if (e.key === "?") $("help-button").click();
});
async function init() {
  try {
    const response = await fetch("/api/estado");
    if (!response.ok) throw new Error();
    state = await response.json();
    render();
  } catch (e) {
    $("status").textContent =
      "Não foi possível conectar à mesa. Verifique o servidor e atualize a página.";
  }
}
init();
// A prévia acompanha alterações nos arquivos sem perder a rodada salva no servidor.
setInterval(async () => {
  try {
    const v = (await (await fetch("/api/versao")).json()).versao;
    if (assetVersion && assetVersion !== v && !busy) location.reload();
    assetVersion = v;
  } catch (_) {}
}, 3000);
