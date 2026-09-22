# 🎴 Count & Queen — Blackjack RPG

Conquiste prestígio nas mesas de blackjack, forme afinidades com cartas e escolha
entre a Nobreza e a Tirania. A jornada termina numa disputa pela coroa.

**Atualização 0.3.0:** campanha mais curta, economia revisada, modo rápido e um
adversário final. Veja todas as mudanças em [CHANGELOG.md](CHANGELOG.md).

## Instalação

Requer Python 3.10 ou superior e um terminal com suporte a UTF-8.

```bash
git clone https://github.com/GustaGol0/count-queen.git
cd count-queen
python -m pip install -r requirements.txt
python main.py
```

No Windows, você também pode usar `py` no lugar de `python`.
O comando antigo `python count_queen.py` continua funcionando.

## Como jogar

Chegue o mais perto possível de 21 sem ultrapassar. Figuras valem 10; o Ás vale
11 ou 1. Um Ás com uma carta de valor 10 na distribuição inicial é blackjack e
paga 3:2. Blackjack vence um 21 com mais cartas; dois blackjacks empatam.

| Momento | Comandos |
| --- | --- |
| Entre rodadas | `j` ou Enter: jogar; `m`: mochila; `r`: modo rápido; `s`: salvar e sair |
| Aposta | Número inteiro positivo; Enter repete a última aposta, limitada ao saldo |
| Sua vez | `p`: pedir; `s`: parar; `d`: dobrar; `sp`: dividir; `des`: desistir |
| Encontro com loja | Enter: visitar; `s`: ignorar |

O jogo mostra apenas as ações permitidas. Dobrar compra uma carta final. Dividir
exige um par e permite até quatro mãos; um 21 após divisão não é blackjack natural.
Desistir devolve metade da aposta. O seguro, disponível com a Manilha da Sorte,
custa metade da aposta e retorna três vezes esse custo se o dealer tiver blackjack.

O modo rápido remove pausas e esperas artificiais, mantendo as escolhas. Você
continua podendo ler os resultados no histórico do terminal.

## A campanha

Cada jornada começa com 200 fichas. Vitórias avançam seu caminho e derrotas
retiram progresso. Apostar uma proporção maior do saldo aumenta o risco e o
prestígio envolvido. Ases, mãos fortes e blackjack influenciam as recompensas.

- **Nobreza:** alcance +10.000 de prestígio para desafiar o Regente.
- **Tirania:** um pacto no Sacrário muda seu caminho; alcance -10.000 para desafiar o Regente.
- **Coroação:** vença três rodadas antes de perder três. Empates não contam.
  Em um split, o saldo de mãos vencidas e perdidas determina o resultado da rodada.
  O Regente compra até chegar a 18; os outros adversários param em 17.
- **Nova tentativa:** perder a disputa sem falir devolve o progresso a ±9.000.
- **Derrota da jornada:** ficar com menos de uma ficha encerra a partida.

O cenário e o adversário mudam conforme o progresso: Taverna da Fronteira,
Torneio do Castelo, Salão dos Nobres, Corte Real e Disputa pela Coroa. A disputa
final não é interrompida por lojas ou eventos. Cada caminho tem seu próprio epílogo.

| Prestígio positivo | Título masculino / feminino |
| --- | --- |
| 0–9 | Plebeu / Plebeia |
| 10–49 | Cavaleiro / Dama |
| 50–149 | Barão / Baronesa |
| 150–499 | Visconde / Viscondessa |
| 500–1.499 | Conde / Condessa |
| 1.500–4.999 | Duque / Duquesa |
| 5.000–9.999 | Príncipe / Princesa |
| 10.000 e disputa vencida | Rei / Rainha |

Na Tirania, as faixas negativas correspondentes levam de Malandro/Malandra a
Flagelo do Reino. Vencer a disputa concede o título de Tirano/Tirana.

## Itens e afinidades

| Item | Efeito |
| --- | --- |
| Bênção dos Quatro Reinos | +25% de lucro por naipe além do primeiro |
| Força do Sete | +75% de lucro ao vencer com um 7 |
| Joias Gêmeas | Novas divisões grátis após o primeiro split pago; até quatro mãos |
| Manilha da Sorte | Habilita o seguro quando o dealer mostra um Ás |
| Caleidoscópio do Acaso | Escolha entre três cartas no primeiro pedido/dobra; um uso por rodada, compartilhado entre mãos |
| Pacto do Tirano | Amplifica o prestígio ganho e perdido |
| Espelho do Tirano | Concede fichas nas penalidades de derrota/desistência |
| Manto da Nobreza | Tributo por rodada de 25 fichas por nível, baseado no prestígio absoluto |

O Caleidoscópio não altera a distribuição inicial. Afinidades concedem +15% de lucro
por nível da melhor afinidade presente na mão, até nível 5. Os bônus de afinidades,
Força do Sete e Bênção são somados e nunca ultrapassam x3 do lucro base; não
multiplicam a devolução da aposta.

O Empório permite duas compras e um ritual por visita. Preços de itens e rituais
têm piso de 2% do saldo; o ritual também depende do nível da carta escolhida.
Ofertas e descontos ficam fixos durante a visita. Comprar uma relíquia no Sacrário
sela o caminho da Tirania; os serviços e requisitos são exibidos antes da escolha.

## Lojas e eventos

Encontros são verificados após cada rodada concluída, inclusive blackjack do dealer.

| Encontro | Primeira rodada elegível | Chance por tentativa | Garantido na tentativa |
| --- | --- | --- | --- |
| Empório Real | 3 | 20% | 8ª |
| Sacrário do Segredo | 5 | 15% | 15ª |
| Andarilho Misterioso | 6 | 5% | 20ª |
| Desafio de Alto Risco | 11 | 3% | 25ª |

Uma aparição zera a espera daquele encontro. Só uma loja aparece por rodada:
a diferente da última tem prioridade, e a outra é sorteada se a primeira não
aparecer. Rodadas bloqueadas não contam como tentativas. Retomar o jogo ou abrir
a mochila não refaz sorteios. Os contadores são salvos junto com a jornada.

O Andarilho oferece trocas e apostas opcionais. O Desafio requer pelo menos
500 de prestígio absoluto e 100 fichas. Sua aposta é 10% do saldo, com mínimo
de 100; vitória avança 150 de prestígio no caminho escolhido, derrota retira 60
e recusa retira 15. O evento não aparece durante a coroação.

## Saves e atualização

O arquivo `save.json` fica sempre na raiz do projeto. Partidas, encontros,
preferências e placar da coroação são salvos automaticamente, e também ao sair.
A gravação preserva o arquivo anterior se a substituição falhar.

**Iniciar Nova Lenda** zera rodadas e encontros, mantém o Salão das Lendas e salva
o novo personagem imediatamente. Saves anteriores à atualização continuam
carregando: saldo, inventário e histórico são mantidos. As novas regras passam
a valer, inclusive o limite de efeito das afinidades antigas acima de nível 5.
Não é necessário apagar seu save para atualizar. O save pessoal não vai ao GitHub.

## Desenvolvimento e testes

```bash
python -m unittest discover -s tests -v
python tools/playthrough.py 42 nobreza
python tools/playthrough.py 42 tirania
```

O playtest usa a interface textual real, automatiza decisões e remove esperas;
não modifica as regras. Seus saves e transcrições ficam numa pasta temporária
informada ao terminar. Não altera o save pessoal.

O GitHub Actions executa os testes em Python 3.10, 3.12 e 3.13.

```text
main.py                 Entrada principal
count_queen.py          Entrada compatível com a primeira versão
count_queen/models.py   Cartas, mãos, jogadores e dealer
count_queen/logic.py    Prestígio e títulos
count_queen/campaign.py Campanha e economia
count_queen/events.py   Sorteios e limites de espera
count_queen/game.py     Rodadas e encerramento da jornada
count_queen/persistence.py Salvamento
count_queen/ui/         Menus e terminal
tests/                 Testes automatizados
```

Se faltar o colorama, execute novamente `python -m pip install -r requirements.txt`.
No Windows, use um terminal com UTF-8 para exibir os símbolos e acentos.
