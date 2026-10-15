"use strict";
const $ = (id) => document.getElementById(id);
const suits = {
  Copas: "♥",
  Ouros: "♦",
  Paus: "♣",
  Espadas: "♠",
  "Sem naipe": "◇",
};
const fmt = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });
const esc = (s) =>
  String(s ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const signed = (n) => `${n > 0 ? "+" : ""}${fmt.format(n)}`;
const names = {
  mesa: "Mesa",
  elite: "Elite",
  boss: "Boss",
  loja: "Empório",
  oficina: "Oficina",
  evento: "Evento",
  refugio: "Refúgio",
  sacrario: "Sacrário",
};
const glyph = {
  mesa: "♠",
  elite: "⚔",
  boss: "♛",
  loja: "♜",
  oficina: "✧",
  evento: "?",
  refugio: "☾",
  sacrario: "◇",
};
const phaseNames = {
  juramento: "UMA PROMESSA PARA A ESTRADA",
  mapa: "ESCOLHA SEU CAMINHO",
  encontro: "ANTES DE ATRAVESSAR",
  recompensa: "ESPÓLIOS DA VITÓRIA",
  loja: "O EMPÓRIO REAL",
  oficina: "REESCREVA SEU BARALHO",
  evento: "HISTÓRIAS DA ESTRADA",
  sacrario: "O PREÇO DO PODER",
  refugio: "UM MOMENTO DE RESPIRO",
  conclusao: "O ENCONTRO TERMINOU",
  fim: "O FIM DE UMA LENDA",
  contrato: "LEIA ANTES DE ASSINAR",
  cobranca: "O COBRADOR ESPERA",
  cobranca_real: "ATO II · O PREÇO DOS JURAMENTOS",
  consagrar: "UMA PROMESSA LIBERTA",
  destino: "ATO III · NÃO HÁ LUGAR PARA DOIS",
  pedagio: "UMA AUDIÊNCIA COM O REI",
};
const battlePhases = [
  "aposta",
  "jogando",
  "seguro",
  "oraculo",
  "revelacao",
  "resultado",
];
let state,
  busy = false,
  lastPhase = "",
  assetVersion;
const sigils = {
  manilha_sorte: "M4 5h8v6H4z M2 7h2v2H2z M12 7h2v2h-2z",
  moeda_peregrino: "M5 2h6v2h2v8h-2v2H5v-2H3V4h2z M7 5v6h2V5z",
  broche_prudencia: "M7 1h2v3h3v3h3v2h-3v3H9v3H7v-3H4V9H1V7h3V4h3z",
  dedal_costureira: "M5 3h6v2h1v8H4V5h1z M6 6h1v1H6z M9 8h1v1H9z",
  lente_escrivao: "M3 2h6v2h2v6H9v2H3v-2H1V4h2z M10 11h2v2h2v2h-3z",
  ficha_cobre: "M4 2h8v2h2v8h-2v2H4v-2H2V4h2z M5 5h6v6H5z",
  forca_sete: "M3 2h10v4h-2v3H9v3H7v3H4v-4h2V8h2V5H3z",
  bencao_reinos_v2: "M2 2h5v5H2z M9 2h5v5H9z M2 9h5v5H2z M9 9h5v5H9z",
  rosario_humildes:
    "M4 2h2v2H4z M10 2h2v2h-2z M2 5h2v2H2z M12 5h2v2h-2z M4 8h2v2H4z M10 8h2v2h-2z M7 9h2v3h3v2H9v2H7v-2H4v-2h3z",
  luvas_duelista: "M3 5h2V2h2v4h1V1h2v5h1V3h2v8h-2v3H5v-3H3z",
  bussola_contrabandista:
    "M6 1h4v2h3v3h2v4h-2v3h-3v2H6v-2H3v-3H1V6h2V3h3z M10 4H8v3H6v5h2V9h2z",
  selo_mercador: "M4 1h8v6H9v3h4v4H3v-4h4V7H4z",
  joias_gemeas: "M3 2h3v2h2v5H6v2H3V9H1V4h2z M10 5h3v2h2v5h-2v2h-3v-2H8V7h2z",
  pacto_tirano: "M3 1h10v14H3z M5 4h6v1H5z M5 7h6v1H5z M8 10h3v3H8z",
  espelho_tirano: "M5 1h6v2h2v7h-2v2H9v3H7v-3H5v-2H3V3h2z M6 4h4v5H6z",
  tesoura_destino:
    "M2 1h2v3h2v3h4V4h2V1h2v5h-2v3h-2v2h3v4H8v-4H7v4H2v-4h3V9H3V6H2z",
  mascara_impostor: "M2 2h12v9h-2v2h-2v2H6v-2H4v-2H2z M4 5h3v3H4z M9 5h3v3H9z",
  ampulheta_usurario:
    "M3 1h10v2h-1v3h-2v4h2v3h1v2H3v-2h1v-3h2V6H4V3H3z M6 3v2h4V3z M6 11v2h4v-2z",
  caleidoscopio_acaso:
    "M6 1h4v3h3v3h2v3h-3v3H9v2H6v-3H3V9H1V6h3V3h2z M6 6h4v4H6z",
  manto_nobreza: "M5 1h6v3h2v5h2v6H1V9h2V4h2z M7 4v8h2V4z",
  coroa_22: "M1 4h2v3h3V4h1V1h2v3h1v3h3V4h2v8H1z M3 14h10v2H3z",
  cetro_sentencas: "M6 1h4v2h2v4h-2v2H9v6H7V9H6V7H4V3h2z",
  coracao_exilada: "M2 2h4v2h4V2h4v2h2v5h-2v2h-2v2h-2v2H6v-2H4v-2H2V9H0V4h2z",
  trono_vazio: "M4 1h8v7h2v6h-2v2h-2v-3H6v3H4v-2H2V8h2z M6 3v5h4V3z",
};
function sigil(key) {
  return `<svg class="pixel-sigil" viewBox="0 0 16 16" aria-hidden="true" shape-rendering="crispEdges"><path fill="currentColor" fill-rule="evenodd" d="${sigils[key] || sigils.pacto_tirano}"/></svg>`;
}
const rarityLabels = {
  comum: "Comum",
  incomum: "Incomum",
  raro: "Rara",
  mitico: "Mítica",
};
function celebrate(key) {
  const item = state.catalog.relics[key];
  if (!item) return;
  const dialog = $("loot-dialog");
  dialog.className = `loot-dialog ${item.raridade}`;
  $("loot-content").innerHTML =
    `<div class="loot-rays" aria-hidden="true">${Array.from({ length: item.raridade === "mitico" ? 16 : item.raridade === "raro" ? 10 : 4 }, (_, i) => `<i style="--n:${i}"></i>`).join("")}</div><div class="eyebrow">RELÍQUIA ${rarityLabels[item.raridade].toUpperCase()} OBTIDA</div><div class="loot-art">${sigil(key)}</div><h2>${esc(item.nome)}</h2><p>${esc(item.descricao)}</p>`;
  dialog.showModal();
}
function button(
  label,
  action,
  value = null,
  extra = {},
  cls = "action-button",
  disabled = false,
) {
  const payload = encodeURIComponent(
    JSON.stringify({ acao: action, valor: value, ...extra }),
  );
  return `<button class="${cls}" data-command="${payload}" ${disabled ? "disabled" : ""}>${esc(label)}</button>`;
}
function cardHTML(c, i = 0) {
  if (c.oculta)
    return '<div class="card back" role="img" aria-label="Carta oculta"><svg><use href="#crown"/></svg></div>';
  if (c.ghost)
    return '<div class="card ghost" aria-hidden="true"><svg><use href="#crown"/></svg></div>';
  const red = ["Copas", "Ouros"].includes(c.naipe),
    face = ["J", "Q", "K"].includes(c.valor);
  const value = c.temporaria === "coroa" ? (c.pontos ?? 0) : c.valor;
  const label = `${value} de ${c.naipe}${c.marca ? " · " + c.marca : ""}${c.temporaria ? " · " + c.temporaria : ""}${c.pontos !== undefined ? " · vale " + c.pontos : ""}`;
  const corner = `<span>${esc(value)}</span><small>${suits[c.naipe] || "◇"}</small>`;
  return `<div class="card ${red ? "red" : ""} ${c.marca ? "marked" : ""}" style="--i:${i}" role="img" aria-label="${esc(label)}" title="${esc(label)}"><span class="card-corner">${corner}</span><span class="card-suit ${face ? "face" : ""}"><span>${face ? esc(value) : suits[c.naipe] || "◇"}</span></span><span class="card-corner bottom">${corner}</span>${c.marca ? `<span class="mark-tag">${esc(c.marca)}</span>` : ""}</div>`;
}
function cards(el, list) {
  const signature = JSON.stringify(list);
  if (el.dataset.cards === signature) return;
  const old = [...el.children],
    fragment = document.createDocumentFragment();
  list.forEach((c, i) => {
    const key = JSON.stringify(c);
    let node = old.find((n) => n.dataset.key === key);
    if (node) old.splice(old.indexOf(node), 1);
    else {
      const t = document.createElement("template");
      t.innerHTML = cardHTML(c, i);
      node = t.content.firstElementChild;
      node.dataset.key = key;
    }
    fragment.append(node);
  });
  el.replaceChildren(fragment);
  el.dataset.cards = signature;
  el.classList.toggle("many", list.length >= 5);
}
function info(title, html) {
  $("info-content").innerHTML =
    `<div class="eyebrow">COUNT & QUEEN</div><h2 id="info-title">${esc(title)}</h2>${html}`;
  if (!$("info-dialog").open) $("info-dialog").showModal();
}
function itemList(keys, catalog) {
  return keys
    .map(
      (k) =>
        `<article class="relic-detail">${catalog[k]?.raridade ? sigil(k) : ""}<span class="rarity ${catalog[k]?.raridade || ""}">${esc(catalog[k]?.raridade || "Juramento")}</span><h3>${esc(catalog[k]?.nome || k)}</h3><p>${esc(catalog[k]?.descricao)}</p></article>`,
    )
    .join("");
}
function inventory() {
  if (!state?.player) return;
  info(
    "Relíquias & juramentos",
    `<div class="help-copy"><h3>Suas relíquias</h3>${itemList(state.player.itens, state.catalog.relics) || "<p>Você ainda não carrega relíquias.</p>"}<h3>Seus juramentos</h3>${itemList(state.player.juramentos, state.catalog.oaths)}${state.player.consagrado ? `<p>Consagrado: ${esc(state.catalog.oaths[state.player.consagrado].nome)}. A contrapartida foi removida.</p>` : ""}<h3>Afinidades</h3>${
      Object.entries(state.player.afinidades)
        .map(([r, n]) => `<p>${esc(r)}: nível ${n} · +${15 * n}% de lucro.</p>`)
        .join("") ||
      "<p>Nenhuma afinidade. Os rituais do Empório podem criar uma.</p>"
    }<h3>Dívidas</h3><p>Juramento: ${fmt.format(state.player.debt)} fichas. Empréstimo: ${fmt.format(state.player.loan)} fichas.</p><details><summary>Catálogo completo · 24 relíquias e 12 juramentos</summary>${itemList(Object.keys(state.catalog.relics), state.catalog.relics)}${itemList(Object.keys(state.catalog.oaths), state.catalog.oaths)}</details></div>`,
  );
}
function deckView() {
  if (!state?.deck) return;
  info(
    "Seu baralho",
    `<div class="help-copy"><p>${state.deck.cards.length} cartas na jornada · ${state.deck.remaining} para comprar · ${state.deck.discard.length} no descarte · ${state.deck.shuffles} embaralhamentos.</p><p>Você e o adversário compram de baralhos separados. Esta lista está organizada por valor, não pela ordem de compra.</p>${
      state.deck.counts
        ? `<h3>Lente do Escrivão</h3><p>${Object.entries(state.deck.counts)
            .map(([v, n]) => `${esc(v)}: ${n}`)
            .join(" · ")}</p>`
        : ""
    }<div class="deck-grid">${state.deck.cards.map((c) => `<div>${cardHTML(c)}</div>`).join("")}</div><h3>Descarte</h3><p>${state.deck.discard.map((c) => `${esc(c.valor)}${suits[c.naipe] || "◇"}`).join(" · ") || "Ainda vazio."}</p><h3>Marcas</h3>${Object.values(
      state.catalog.marks,
    )
      .map((m) => `<p><strong>${esc(m.nome)}:</strong> ${esc(m.descricao)}</p>`)
      .join("")}</div>`,
  );
}
function historyHTML() {
  return (
    (state?.history || [])
      .map(
        (h) =>
          `<div class="history-entry"><div><span class="eyebrow">RODADA ${h.rodada}</span><strong class="${h.fichas >= 0 ? "positive" : "negative"}">${signed(h.fichas)} fichas</strong></div><small>${esc(h.adversario)} · ${signed(h.prestigio)} prestígio</small></div>`,
      )
      .join("") ||
    '<div class="history-empty">Sua primeira partida abre esta crônica.</div>'
  );
}
function combo(key) {
  const j = state.player.juramentos,
    items = state.player.itens;
  const links = {
    forca_sete: ["sete"],
    caleidoscopio_acaso: ["dobrar", "ultima"],
    rosario_humildes: ["humilde", "quinta"],
    joias_gemeas: ["lamina"],
    mascara_impostor: ["lamina"],
    broche_prudencia: ["lamina"],
    bussola_contrabandista: ["estrada"],
    luvas_duelista: ["dobrar"],
    selo_mercador: ["estrada"],
  };
  const active = (links[key] || []).filter((x) => j.includes(x));
  if (
    (key === "joias_gemeas" || key === "mascara_impostor") &&
    active.includes("lamina") &&
    state.player.consagrado !== "lamina"
  )
    return "Atenção: Uma Só Lâmina bloqueia divisões.";
  let text = active.length
    ? "Interage com " +
      active.map((k) => state.catalog.oaths[k].nome).join(", ") +
      "."
    : "";
  if (key === "mascara_impostor" && items.includes("joias_gemeas"))
    text += " Combina com Joias Gêmeas.";
  if (
    key === "lamina" &&
    items.some((i) => ["joias_gemeas", "mascara_impostor"].includes(i))
  )
    text += " Atenção: bloqueia suas relíquias de divisão.";
  return text;
}
function choiceCard(key, item, action, extra = "") {
  return `<article class="choice-card ${item.raridade || "oath-contract"}"><div class="eyebrow">${esc(rarityLabels[item.raridade] || "Contrato de juramento")}</div><span class="choice-emblem">${sigil(item.raridade ? key : "pacto_tirano")}</span><h3>${esc(item.nome)}</h3><p>${esc(item.descricao)}</p>${combo(key) ? `<p class="synergy">${esc(combo(key))}</p>` : ""}${extra}${button(item.raridade ? "Escolher" : "Assinar", action, key, {}, "primary")}</article>`;
}
function mapHTML() {
  const nodes = state.nodes,
    rows = Math.max(...nodes.map((n) => n.row)) + 1;
  const height = rows * 104 + 35;
  const x = (r) => 8 + (r * 84) / (rows - 1),
    y = (c) => 20 + c * 30;
  const mobileX = (c) => 15 + c * 35,
    mobileY = (r) => 92 - (r * 84) / (rows - 1);
  let paths = "",
    mobilePaths = "";
  for (const a of nodes)
    for (const b of nodes) {
      if (
        b.row === a.row + 1 &&
        (b.type === "boss" || Math.abs(a.col - b.col) <= 1)
      ) {
        const done =
          state.visited.includes(a.id) && state.visited.includes(b.id);
        const available =
          (state.visited.includes(a.id) && b.available) ||
          (a.available && b.row === a.row + 1);
        const cls = done ? "travelled" : available ? "next-road" : "";
        paths += `<path class="${cls}" d="M ${x(a.row)} ${y(a.col)} L ${x(b.row)} ${y(b.col)}"/>`;
        mobilePaths += `<path class="${cls}" d="M ${mobileX(a.col)} ${mobileY(a.row)} L ${mobileX(b.col)} ${mobileY(b.row)}"/>`;
      }
    }
  return `<div class="map-intro"><div><h3>Escolha a próxima parada</h3><p>Siga uma das rotas iluminadas até o boss.</p></div><span class="map-counter">REGIÃO ${state.region + 1} / 4</span></div><div class="map-board" style="--map-height:${height}px"><svg class="map-landscape" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">${paths}</svg><svg class="map-portrait" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">${mobilePaths}</svg>${nodes
    .map((n) => {
      const visited = state.visited.includes(n.id),
        next = n.available;
      return `<div class="map-node ${visited ? "visited" : ""} ${next ? "available" : ""} ${n.type === "boss" ? "boss-node" : ""}" style="--x:${x(n.row)}%;--y:${y(n.col)}%;--mx:${mobileX(n.col)}%;--my:${mobileY(n.row)}%"><button data-command="${encodeURIComponent(JSON.stringify({ acao: "no", valor: n.id }))}" ${!next ? "disabled" : ""} aria-label="${esc(n.name)}${next && !n.connected ? " · usar Bússola" : ""}" title="${esc(n.name)}"><span>${glyph[n.type]}</span></button><small>${esc(n.type === "boss" ? state.boss.nome : names[n.type])}${visited ? " · ✓" : ""}${next && !n.connected ? " · Bússola" : ""}</small></div>`;
    })
    .join("")}</div><div class="map-key">${Object.entries(names)
    .map(([k, v]) => `<span>${glyph[k]} ${v}</span>`)
    .join(
      "",
    )}</div><article class="boss-intel"><div class="eyebrow">ESPERANDO NO FIM DA REGIÃO</div><h3>${esc(state.boss.nome)}</h3><p>“${esc(state.boss.frase)}”</p><details><summary>Conhecer baralho e regras</summary><p>${esc(state.boss.descricao)}</p>${state.boss.style ? `<p>O Rei preparou uma resposta à sua estratégia: <strong>${esc(state.boss.style)}</strong>. Seu rosto é ${esc(state.boss.face)}.</p>` : ""}</details></article>`;
}
function workshop() {
  const options = state.deck.cards
    .filter((c) => !c.temporaria)
    .map(
      (c) =>
        `<option value="${c.id}">${esc(c.valor)} de ${esc(c.naipe)}${c.marca ? " · " + esc(c.marca) : ""} · #${c.id}</option>`,
    )
    .join("");
  const ranks = [
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "J",
    "Q",
    "K",
    "A",
  ];
  return `<h3>Oficina de cartas</h3><p>Escolha uma intervenção. As mudanças duram até o fim da jornada; a ordem do baralho é preservada.</p><form id="workshop-form" class="workshop-form"><label for="work-card">CARTA DO SEU BARALHO</label><select id="work-card">${options}</select><label for="work-kind">INTERVENÇÃO</label><select id="work-kind"><option value="marcar">Aplicar uma marca</option><option value="transformar">Transformar o valor</option><option value="remover">Remover a carta</option><option value="adicionar">Adicionar uma nova carta</option></select><div id="rank-field" hidden><label for="work-rank">VALOR</label><select id="work-rank">${ranks.map((r) => `<option>${r}</option>`).join("")}</select></div><div id="mark-field"><label for="work-mark">MARCA</label><select id="work-mark">${Object.entries(
    state.catalog.marks,
  )
    .map(
      ([id, m]) =>
        `<option value="${id}">${esc(m.nome)} — ${esc(m.descricao)}</option>`,
    )
    .join(
      "",
    )}</select></div><p class="note">Uma marca por carta. Mínimo de 16 cartas permanentes; máximo de 80 cartas.</p><button class="primary" type="submit">Confirmar alteração</button></form>${button("Sair da oficina", "sair", null, {}, "quiet")}`;
}
function renderAdventure() {
  const s = state,
    p = s.player,
    phase = s.phase,
    b = s.battle;
  let html = `<div class="eyebrow">${phaseNames[phase] || "A JORNADA"}</div>`;
  if (phase === "mapa") html += mapHTML();
  else if (phase === "juramento")
    html += `<h3>Assine um juramento</h3><p>Escolha um entre três juramentos. Ele se acumula com suas escolhas anteriores e dura até o fim da jornada.</p><div class="boss-teaser">Boss desta região: <strong>${esc(s.boss.nome)}</strong><details><summary>Preparar-se para o adversário</summary><p>${esc(s.boss.descricao)}</p>${s.boss.style ? `<p>Resposta do Rei: ${esc(s.boss.style)} · rosto ${esc(s.boss.face)}.</p>` : ""}</details></div><div class="choice-grid">${s.offers.map((k) => choiceCard(k, s.catalog.oaths[k], "juramento")).join("")}</div>`;
  else if (phase === "encontro") {
    const n = s.pending;
    const title =
      n.type === "boss" ? s.boss.nome : s.nodes.find((x) => x.id === n.id).name;
    const descriptions = {
      mesa: "Até três rodadas. Vença duas para ganhar +3 de prestígio, 20 fichas e escolher uma relíquia comum ou incomum. Perder permite seguir viagem, se houver fichas.",
      elite:
        "Duas vitórias antes de duas derrotas. Vitória: +7 de prestígio, 40 fichas e escolha de relíquia rara.",
      loja: "Até duas compras e um serviço. As ofertas ficam fixas durante a visita. Relíquias míticas não são vendidas.",
      oficina:
        "Uma alteração gratuita: remover, transformar, marcar ou adicionar uma carta.",
      evento:
        "Uma escolha pode mudar seus recursos, seu baralho ou sua influência.",
      refugio:
        "Escolha entre fichas, purificação de maldições ou uma bênção para o próximo encontro.",
      sacrario:
        "Faça um pacto, escolha seu caminho ou deixe uma oferenda. Cada consequência é mostrada antes da escolha.",
    };
    const eliteRules = {
      falsificador: "Baralho com muitas figuras. Para em 16.",
      novica: "Cartas pequenas; para em 17. Você começa com uma bênção.",
      escrivao:
        "Sem dobrar. +25% de lucro nas vitórias; adversário para em 17.",
      aprendiz:
        "Limite 19 na primeira rodada, 21 nas demais. Para três abaixo do limite.",
    };
    html += `<div class="encounter-emblem">${glyph[n.type]}</div><h3>${esc(title)}</h3><p>${esc(n.type === "boss" ? s.boss.descricao : descriptions[n.type])}</p>${n.elite ? `<p class="rule-callout">${eliteRules[n.elite]}</p>` : ""}${n.type === "boss" ? "<p>Vitória: recompensa mítica (regiões 1–3). Uma revanche paga se você perder. O Rei concede um desbloqueio permanente.</p>" : ""}<div class="actions">${button("Entrar no encontro", "entrar", null, {}, "primary")}${button("Voltar ao mapa", "voltar")}</div>`;
  } else if (phase === "recompensa")
    html += `<h3>Escolha sua relíquia</h3><p>Uma relíquia para acompanhar sua jornada. Bônus de lucro somam até o limite de ×3.</p><div class="choice-grid">${s.offers.map((k) => choiceCard(k, s.catalog.relics[k], "reliquia")).join("")}</div>`;
  else if (phase === "loja") {
    const sh = s.shop;
    html += `<h3>Empório</h3><p>${sh.bought.length}/2 compras · ${sh.services}/1 serviço usado. Saldo: ${fmt.format(p.fichas)} fichas.</p><div class="choice-grid shop-grid">${sh.offers
      .map((k) => {
        const i = s.catalog.relics[k],
          price = sh.prices[k],
          done = sh.bought.includes(k);
        return `<article class="choice-card ${i.raridade}"><span class="rarity ${i.raridade}">${rarityLabels[i.raridade]}</span><span class="choice-emblem">${sigil(k)}</span><h3>${esc(i.nome)}</h3><p>${esc(i.descricao)}</p><strong class="price">${price} fichas</strong>${combo(k) ? `<p class="synergy">${esc(combo(k))}</p>` : ""}${button(done ? "Adquirida" : "Comprar", "comprar", k, {}, "primary", done || sh.bought.length >= 2 || p.fichas < price)}${sh.credit ? button(`A prazo: ${fmt.format(price / 2)} agora`, "comprar", k, { credito: true }, "quiet", done || sh.bought.length >= 2 || p.fichas < price / 2) : ""}</article>`;
      })
      .join(
        "",
      )}</div><div class="shop-services"><h3>Serviços do Empório</h3>${button("Alterar baralho · 35 fichas", "servico", null, {}, "action-button", sh.services >= 1 || p.fichas < 35)}<form id="affinity-form"><label for="affinity-rank">RITUAL DE AFINIDADE · 40 × PRÓXIMO NÍVEL</label><select id="affinity-rank">${["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"].map((r) => `<option value="${r}">${r} · nível ${p.afinidades[r] || 0} · ${40 * ((p.afinidades[r] || 0) + 1)} fichas</option>`).join("")}</select><button class="action-button" ${sh.services >= 1 ? "disabled" : ""}>Realizar ritual</button></form></div>${button("Seguir viagem", "sair", null, {}, "primary")}`;
  } else if (phase === "oficina") html += workshop();
  else if (["evento", "sacrario", "refugio"].includes(phase)) {
    const title = {
      ponte: "O guarda da ponte cobra seu preço.",
      biblioteca: "Um livro sobreviveu ao incêndio.",
      audiencia: "Seu nome chegou antes de você.",
    }[s.event];
    html += `<h3>${phase === "evento" ? title : phase === "refugio" ? "A estrada pode esperar." : "Quem você pretende se tornar?"}</h3><div class="story-choices">${s.options.map((o) => `<article class="story-choice"><div><h4>${esc(o.nome)}</h4><p>${esc(o.descricao)}</p></div>${button("Escolher", "escolha", o.id, {}, "primary")}</article>`).join("")}</div>`;
  } else if (phase === "conclusao") {
    const r = s.result;
    html += `<div class="encounter-emblem">${r.won ? "♛" : "◇"}</div><h3>${r.won ? "Vitória" : "Derrota"}</h3><p>${esc(r.name)} · ${r.won ? "Recompensas recebidas." : "Sem recompensa de vitória; prestígio reduzido."}</p>${r.boss && !r.won ? `<p>${r.retry ? `Uma revanche está disponível por ${r.cost} fichas.` : "Sua revanche já foi usada."} Encerrar o desafio termina a jornada.</p>` : ""}<div class="actions">${r.retry ? button(`Revanche · ${r.cost} fichas`, "revanche", null, {}, "primary", p.fichas < r.cost) : ""}${button(r.boss && !r.won ? "Encerrar jornada" : r.boss ? "Próxima região" : "Voltar ao mapa", "seguir", null, {}, "primary")}</div>`;
  } else if (phase === "fim")
    html += `<div class="encounter-emblem">${s.victory ? "♛" : "◇"}</div><h3>${s.victory ? "O reino pronuncia seu nome." : "Toda lenda deixa uma marca."}</h3><p>${esc(s.epilogue)}</p><p>${fmt.format(p.fichas)} fichas · ${p.prestigio} de prestígio · ${s.round_count} rodadas</p><button class="primary" id="new-legend">Começar outra lenda</button><details><summary>Salão das Lendas</summary>${s.legends.map((l) => `<p>${esc(l.nome)} · ${l.vitoria ? "Coroado" : "Caído"} · região ${l.regiao} · ${l.prestigio} prestígio</p>`).join("")}</details>`;
  else if (phase === "contrato")
    html += `<h3>Escolha a cláusula desta rodada.</h3><div class="story-choices">${s.offers
      .map((k) => {
        const c = {
          firme: ["Mão Firme", "Sem dobrar. O rival compra até 18."],
          individual: ["Conta Individual", "Sem dividir. +25% de lucro."],
          testemunhas: [
            "Sem Testemunhas",
            "Sem desistir. Veja a carta aberta antes de apostar.",
          ],
          curta: [
            "Assinatura Curta",
            "Até dois pedidos por mão. Blackjack natural vencedor conta duas vitórias.",
          ],
        }[k];
        return `<article class="story-choice"><div><h4>${c[0]}</h4><p>${c[1]}</p></div>${button("Assinar", "contrato", k, {}, "primary")}</article>`;
      })
      .join("")}</div>`;
  else if (phase === "cobranca")
    html += `<h3>“Seu nome ainda tem valor.”</h3><p>Escolha como pagar pela rodada perdida.</p><div class="actions">${button("Pagar 8 fichas", "cobranca", "fichas", {}, "primary", p.fichas < 8)}${button("Perder 2 de prestígio", "cobranca", "prestigio")}</div>`;
  else if (phase === "cobranca_real")
    html += `<h3>“Cada promessa foi feita diante de mim.”</h3><p>Escolha a cobrança que valerá durante o segundo ato. Suas relíquias e os benefícios dos juramentos permanecem ativos.</p><div class="choice-grid">${s.offers.map((k) => `<article class="choice-card"><h3>${esc(s.catalog.oaths[k].nome)}</h3><p>${esc(b.charge_descriptions[k])}</p>${button("Aceitar cobrança", "cobranca_real", k, {}, "primary")}</article>`).join("")}</div>`;
  else if (phase === "consagrar")
    html += `<h3>Uma promessa sem correntes.</h3><p>Escolha um juramento. Seu benefício permanece, mas a contrapartida deixa de valer durante o restante do duelo.</p><div class="choice-grid">${p.juramentos.map((k) => choiceCard(k, s.catalog.oaths[k], "consagrar")).join("")}</div>`;
  else if (phase === "destino")
    html += `<h3>Governar o reino ou possuir a coroa?</h3><p>Esta escolha define as regras do último ato e o seu epílogo.</p><div class="choice-grid"><article class="choice-card"><h3>Governar</h3><p>Limite 21. O Rei compra até 19. Sacrifique uma relíquia por rodada para prever a próxima carta antes de pedir ou parar.</p>${button("Governar", "destino", "governar", {}, "primary")}</article><article class="choice-card"><h3>Usurpar</h3><p>Limite 22. Sua Carta da Coroa começa em 0 e pode ser fixada de 1 a 11 uma vez por rodada. O Rei vence empates comuns.</p>${button("Usurpar", "destino", "usurpar", {}, "primary")}</article></div>`;
  else if (phase === "pedagio")
    html += `<h3>O Rei exige uma audiência.</h3><p>Pague 8 fichas ou revele sua carta inicial. Se revelar, o Rei comprará até 19 nesta rodada.</p><div class="actions">${button("Pagar 8 fichas", "pedagio", "pagar", {}, "primary", p.fichas < 8)}${button("Revelar a carta", "pedagio", "revelar")}</div>`;
  $("adventure-panel").innerHTML = html;
  if (
    lastPhase !== phase &&
    !matchMedia("(prefers-reduced-motion: reduce)").matches
  ) {
    $("adventure-panel").animate(
      [
        { opacity: 0, transform: "translateY(10px)" },
        { opacity: 1, transform: "none" },
      ],
      { duration: 220, easing: "steps(5)" },
    );
  }
  $("new-legend")?.addEventListener("click", () => $("welcome").showModal());
  $("affinity-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    act("afinidade", $("affinity-rank").value);
  });
  $("work-kind")?.addEventListener("change", () => {
    const k = $("work-kind").value;
    $("rank-field").hidden = !["transformar", "adicionar"].includes(k);
    $("mark-field").hidden = k !== "marcar";
    $("work-card").disabled = k === "adicionar";
  });
  $("workshop-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const k = $("work-kind").value;
    act(k, k === "marcar" ? $("work-mark").value : $("work-rank").value, {
      carta: $("work-card").value,
    });
  });
}
function renderBattle() {
  const b = state.battle,
    p = state.player,
    phase = state.phase;
  $("battle-rules").innerHTML =
    `<div class="battle-score"><strong>${esc(b.name)}${b.identity === "rei" ? ` · Ato ${b.act}/3` : ""}</strong><span>${b.wins}/${b.target} vitórias · ${b.losses}/${b.max_losses} derrotas${b.kind === "mesa" ? ` · rodada ${Math.min(3, b.rounds + 1)}/3` : ""}</span><b>LIMITE ${b.limit}</b></div><details><summary>Regras, baralho e efeitos ativos</summary><p>${esc(b.description)}</p><p>Composição: ${Object.entries(
      b.composition,
    )
      .map(([v, n]) => `${esc(v)} ×${n}`)
      .join(
        " · ",
      )}. ${b.remaining} cartas para comprar.</p><p>Bênçãos: ${b.blessings}. ${b.draws >= 2 ? "DESEMPATE ATIVO: em empate comum, vence a mão válida com menos cartas; igualdade favorece você." : ""}</p>${b.contract ? `<p>Contrato: ${esc(b.contract)}.</p>` : ""}${b.charge ? `<p>Cobrança: ${esc(b.charge_descriptions[b.charge])}</p>` : ""}${b.identity === "gemeas" ? `<p>Defesas já gastas: ${b.sisters_saved.map((x) => (x === "a" ? "Íris" : "Véspera")).join(", ") || "nenhuma"}.</p>` : ""}${b.identity === "sinos" ? `<p>Sinos: ${b.bells}/7.</p>` : ""}</details>`;
  $("table").dataset.chapter = state.region;
  $("table").dataset.outcome = b.result
    ? b.result.score > 0
      ? "win"
      : b.result.score < 0
        ? "loss"
        : "draw"
    : "";
  $("dealer-name").textContent =
    b.name + (b.identity === "rei" ? ` · Ato ${b.act}/3` : "");
  $("dealer-rule").textContent = `Para em ${b.dealer_stop}`;
  const showing = b.hands.length > 0;
  cards(
    $("dealer-cards"),
    showing
      ? b.dealer
      : b.preview
        ? [b.preview, { ghost: true }]
        : [{ ghost: true }, { ghost: true }],
  );
  $("dealer-score").textContent =
    b.dealer_total !== null
      ? `${b.dealer_total} / ${b.limit}`
      : b.preview
        ? "CARTA REVELADA PELO CONTRATO"
        : "CARTA OCULTA";
  const hands = showing
    ? b.hands
    : [{ cards: [{ ghost: true }, { ghost: true }], total: 0 }];
  $("player-hands").classList.toggle("split", hands.length > 1);
  while ($("player-hands").children.length > hands.length)
    $("player-hands").lastElementChild.remove();
  hands.forEach((h, i) => {
    let el = $("player-hands").children[i];
    if (!el) {
      el = document.createElement("div");
      el.className = "player-hand";
      el.innerHTML = '<div class="cards"></div><div class="hand-score"></div>';
      $("player-hands").append(el);
    }
    cards(el.querySelector(".cards"), h.cards);
    el.classList.toggle("active", phase === "jogando" && b.current === i);
    el.querySelector(".hand-score").textContent = showing
      ? `${hands.length > 1 ? "MÃO " + (i + 1) + " · " : ""}${h.surrender ? "DESISTÊNCIA" : h.total + " / " + b.limit}${h.natural ? " · BLACKJACK" : ""}${b.result ? " · " + b.result.hands[i].texto.toUpperCase() : ""}`
      : "SUA PRÓXIMA MÃO";
  });
  $("table-bet").hidden = !showing;
  $("table-bet").textContent =
    `♜ ${fmt.format(b.hands.reduce((n, h) => n + h.bet, 0))} em jogo`;
  document.querySelector(".table-center>span").textContent =
    b.limit === 21
      ? "BLACKJACK PAGA 3:2"
      : `LIMITE ${b.limit} · SEM BLACKJACK NATURAL`;
  $("bet-form").hidden = phase !== "aposta";
  $("actions").hidden = !["jogando", "seguro", "revelacao"].includes(phase);
  $("result").hidden = phase !== "resultado";
  $("oracle").hidden = phase !== "oraculo";
  if (phase === "aposta") {
    $("status").textContent = "Faça sua aposta.";
    $("bet").max = Math.floor(p.fichas);
    if (lastPhase !== phase || Number($("bet").value) > p.fichas)
      $("bet").value = Math.max(
        1,
        Math.min(p.ultima_aposta, Math.floor(p.fichas)),
      );
    $("bet-form")
      .querySelectorAll("[data-bet]")
      .forEach((btn) => {
        btn.disabled =
          btn.dataset.bet !== "all" && Number(btn.dataset.bet) > p.fichas;
        btn.classList.toggle(
          "selected",
          btn.dataset.bet === String($("bet").value),
        );
      });
  } else if (phase === "jogando") {
    $("status").textContent =
      `Sua vez · mão ${b.current + 1} de ${b.hands.length}.${b.peek ? " Previsão: " + b.peek.valor + " de " + b.peek.naipe + "." : ""}`;
    const labels = {
      pedir: "Pedir carta [P]",
      parar: "Parar [S]",
      dobrar: `Dobrar · ${fmt.format(b.double_cost)} [D]`,
      dividir: "Dividir",
      desistir: "Desistir",
      trono: "Trocar mãos · Trono",
      bencao: "Usar bênção",
      brasa: "Atiçar a Brasa",
    };
    $("actions").innerHTML = Object.entries(labels)
      .filter(
        ([k]) =>
          ["pedir", "parar", "dobrar", "dividir", "desistir"].includes(k) ||
          b.actions.includes(k),
      )
      .map(([k, l]) =>
        button(
          l,
          k,
          null,
          {},
          "action-button " + (k === "pedir" ? "primary" : ""),
          !b.actions.includes(k),
        ),
      )
      .join("");
    if (b.actions.includes("coroa"))
      $("actions").innerHTML +=
        '<form id="crown-form" class="inline-form"><label for="crown-value">CARTA DA COROA</label><input id="crown-value" type="number" min="1" max="11" value="1" required><button class="action-button">Fixar valor</button></form>';
    if (b.actions.includes("sacrificar"))
      $("actions").innerHTML +=
        `<form id="sacrifice-form" class="inline-form"><label for="sacrifice-relic">SACRIFICAR PARA PREVER</label><select id="sacrifice-relic">${p.itens.map((k) => `<option value="${k}">${esc(state.catalog.relics[k].nome)}</option>`).join("")}</select><button class="action-button">Sacrificar relíquia</button></form>`;
    $("crown-form")?.addEventListener("submit", (e) => {
      e.preventDefault();
      act("coroa", Number($("crown-value").value));
    });
    $("sacrifice-form")?.addEventListener("submit", (e) => {
      e.preventDefault();
      act("sacrificar", $("sacrifice-relic").value);
    });
  } else if (phase === "seguro") {
    $("status").textContent =
      `O rival mostra um Ás. Seguro custa ${fmt.format(b.hands[0].bet / 2)} fichas.`;
    $("actions").innerHTML =
      button("Comprar seguro", "segurar") +
      button("Sem seguro", "recusar_seguro");
  } else if (phase === "oraculo") {
    $("status").textContent =
      "O Caleidoscópio mostra três caminhos. Escolha uma carta.";
    $("oracle").innerHTML =
      `<div class="cards">${b.choices.map((c, i) => `<button class="oracle-choice" data-command="${encodeURIComponent(JSON.stringify({ acao: "escolher", valor: i }))}" aria-label="Escolher ${esc(c.valor)} de ${esc(c.naipe)}">${cardHTML(c)}</button>`).join("")}</div>`;
  } else if (phase === "revelacao") {
    $("status").textContent =
      "O Cetro pode obrigar o adversário a comprar mais uma carta.";
    $("actions").innerHTML =
      button("Usar Cetro", "cetro", null, {}, "primary") +
      button("Manter resultado", "liquidar");
  } else if (phase === "resultado") {
    $("status").textContent = "Rodada encerrada.";
    const r = b.result;
    $("result").innerHTML =
      `<div><h3>${r.score > 0 ? "Vitória" : r.score < 0 ? "Derrota" : "Empate"}</h3><p><span class="${r.fichas >= 0 ? "positive" : "negative"}">${signed(r.fichas)} fichas</span> · ${signed(r.prestigio)} de prestígio</p></div>${button("Continuar", "continuar", null, {}, "primary")}`;
  }
}
function render() {
  if (!state) return;
  document.body.dataset.phase = state.phase || "inicio";
  document.body.dataset.region = state.region ?? 0;
  const p = state.player;
  $("table").hidden = true;
  $("control-panel").hidden = true;
  $("battle-rules").hidden = true;
  $("adventure-panel").hidden = false;
  if (!p) {
    document.body.classList.remove("in-battle");
    $("adventure-panel").innerHTML =
      '<div class="encounter-emblem">♛</div><h3>Quatro regiões. Uma coroa.</h3><p>Escolha caminhos, construa seu baralho e enfrente o Rei Sem Rosto.</p>';
    if (!$("welcome").open) $("welcome").showModal();
    return;
  }
  if ($("welcome").open) $("welcome").close();
  $("player-name").textContent = p.nome;
  $("player-title").textContent = p.titulo;
  $("balance").textContent = fmt.format(p.fichas);
  $("prestige").innerHTML = `${p.prestigio} <small>/ 100</small>`;
  $("deck-count").textContent = state.deck.cards.length;
  $("draw-count").textContent = state.deck.remaining;
  $("relic-count").textContent = p.itens.length;
  $("chapter-label").textContent =
    `REGIÃO ${state.region + 1} · ${phaseNames[state.phase] || "À MESA"}`;
  $("chapter").textContent = state.regions[state.region];
  $("round").textContent = String(
    state.round_count + (state.phase === "resultado" ? 0 : 1),
  ).padStart(2, "0");
  $("relics").innerHTML = p.itens
    .map((k) => {
      const item = state.catalog.relics[k];
      return `<button class="relic ${item.raridade}" data-relic="${k}" aria-label="${esc(item.nome)} · ${rarityLabels[item.raridade]}" title="${esc(item.nome)}">${sigil(k)}</button>`;
    })
    .join("");
  $("global-notice").hidden = !state.notice;
  $("global-notice").textContent = state.notice;
  const combat = battlePhases.includes(state.phase);
  $("adventure-panel").hidden = combat;
  $("table").hidden = !combat;
  $("control-panel").hidden = !combat;
  $("battle-rules").hidden = !combat;
  document.body.classList.toggle("in-battle", combat);
  if (combat) renderBattle();
  else renderAdventure();
  lastPhase = state.phase;
}
async function act(acao, valor = null, extra = {}) {
  if (busy || !state) return;
  let acquired = null;
  const previousItems = new Set(state.player?.itens || []);
  busy = true;
  $("global-error").hidden = true;
  $("welcome-error").hidden = true;
  const disabled = [...document.querySelectorAll("button")].map((b) => [
    b,
    b.disabled,
  ]);
  disabled.forEach(([b]) => (b.disabled = true));
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
    acquired = state.player?.itens.find((k) => !previousItems.has(k)) || null;
  } catch (e) {
    const el = $("welcome").open ? $("welcome-error") : $("global-error");
    el.textContent =
      e.message === "Failed to fetch"
        ? "A conexão foi interrompida. Reinicie o jogo e retome seu último movimento salvo."
        : e.message;
    el.hidden = false;
    try {
      const r = await fetch("/api/estado");
      if (r.ok) state = await r.json();
    } catch (_) {}
  } finally {
    busy = false;
    disabled.forEach(([b, d]) => (b.disabled = d));
    render();
    if (acquired) celebrate(acquired);
  }
}
$("loot-close").addEventListener("click", () => $("loot-dialog").close());
document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-command]");
  if (b && !b.disabled) {
    const { acao, valor, ...extra } = JSON.parse(
      decodeURIComponent(b.dataset.command),
    );
    act(acao, valor, extra);
  }
  if (e.target.closest("[data-inventory]")) inventory();
  const relic = e.target.closest("[data-relic]");
  if (relic) {
    const key = relic.dataset.relic;
    info(state.catalog.relics[key].nome, itemList([key], state.catalog.relics));
  }
});
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
          ? Math.floor(state.player.fichas)
          : b.dataset.bet;
    }),
  );
$("new-game-form").addEventListener("submit", (e) => {
  e.preventDefault();
  act("nova", null, { nome: $("name").value, genero: $("gender").value });
});
$("welcome").addEventListener("cancel", (e) => {
  if (!state?.player) e.preventDefault();
});
$("inventory-button").addEventListener("click", inventory);
$("deck-button").addEventListener("click", deckView);
$("table-deck-button").addEventListener("click", deckView);
$("journey-button").addEventListener("click", () => {
  if (!state?.player) return;
  const p = state.player;
  info(
    "Sua jornada",
    `<p>${esc(p.nome)} · ${esc(p.titulo)} · ${p.caminho === "tirania" ? "Tirania" : "Nobreza"}</p><ol class="route">${state.regions.map((name, i) => `<li class="${i === state.region ? "current" : i < state.region ? "passed" : ""}"><span>${["I", "II", "III", "IV"][i]}</span><div>${esc(name)}<small>${i === state.region ? "Você está aqui" : i < state.region ? "Concluída" : "Por descobrir"}</small></div></li>`).join("")}</ol><p class="note">Jornada salva automaticamente.</p>`,
  );
});
$("history-button").addEventListener("click", () =>
  info("Crônica da jornada", historyHTML()),
);
$("info-dialog")
  .querySelector(".dialog-close")
  .addEventListener("click", () => $("info-dialog").close());
$("help-button").addEventListener("click", () =>
  info(
    "A estrada da coroa",
    `<div class="help-copy"><p>Atravesse quatro regiões escolhendo caminhos. No início de cada uma, escolha um dos três juramentos: efeitos permanentes até o fim da jornada.</p><p>Seu baralho é separado do rival e permanece entre encontros. Oficinas alteram cartas; lojas vendem relíquias e afinidades. Míticas só vêm de bosses.</p><p>Chegue perto do limite sem ultrapassar. Normalmente 21; o Astrônomo e o último ato podem mudar esse número. Figuras valem 10; Ás vale 1 ou 11. Blackjack natural paga 3:2 somente com limite 21.</p><ul><li>Pedir (P): compre do seu baralho.</li><li>Parar (S): mantenha sua mão.</li><li>Dobrar (D): pague o adicional indicado e compre uma carta final.</li><li>Dividir: separe pares em até quatro mãos, se permitido.</li><li>Desistir: receba metade da aposta, se permitido.</li></ul><p>Mesas comuns: duas vitórias em até três rodadas. Elites: duas vitórias antes de duas derrotas. Bosses: consulte as regras antes de entrar. Após dois empates seguidos, menos cartas desempata a próxima rodada; igualdade favorece você, exceto regras explícitas do Rei.</p><p>Fichas sustentam a jornada. Prestígio vai de 0 a 100 e abre oportunidades, sem bloquear o mapa. Nobreza e Tirania são escolhidas no Sacrário.</p><p>Apenas um save por servidor. Atualizar a página não refaz cartas nem sorteios. Os atalhos ficam desativados ao preencher campos ou abrir janelas.</p></div>`,
  ),
);
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
  const a = { p: "pedir", s: "parar", d: "dobrar" }[e.key.toLowerCase()];
  if (a && state?.battle?.actions?.includes(a)) {
    e.preventDefault();
    act(a);
  }
  if (e.key === "?") $("help-button").click();
});
(async () => {
  try {
    const r = await fetch("/api/estado");
    if (!r.ok) throw new Error();
    state = await r.json();
    render();
  } catch (_) {
    $("global-error").hidden = false;
    $("global-error").textContent =
      "Não foi possível conectar à jornada. Inicie jogar_visual.py e atualize a página.";
  }
})();
setInterval(async () => {
  try {
    const v = (await (await fetch("/api/versao")).json()).versao;
    if (assetVersion && assetVersion !== v && !busy) location.reload();
    assetVersion = v;
  } catch (_) {}
}, 5000);

const fullscreenButton = $("fullscreen-button");
fullscreenButton.hidden = !document.fullscreenEnabled;
fullscreenButton.addEventListener("click", async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
  } catch (_) {
    $("global-error").textContent =
      "O navegador não permitiu abrir a tela cheia.";
    $("global-error").hidden = false;
  }
});
document.addEventListener("fullscreenchange", () => {
  const active = Boolean(document.fullscreenElement);
  fullscreenButton.textContent = active ? "Sair da tela cheia" : "Tela cheia";
  fullscreenButton.setAttribute("aria-pressed", String(active));
});
