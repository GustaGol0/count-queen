# 🎴 Count & Queen — A Estrada da Coroa

Um blackjack roguelite de fantasia medieval. Escolha caminhos em quatro regiões,
modifique seu próprio baralho, combine 27 relíquias com 12 juramentos e desafie
sete bosses — até o Rei Sem Rosto, que responde à história da sua jornada.

**Próxima atualização — Mesa Viva:** retratos de fantasia ilustrada, feltro com
acabamento em latão, cartas de papel e fichas animadas. Mesa em tela ampla,
menus sob demanda e mapa horizontal no computador. Leia os [patchnotes](CHANGELOG.md)
e o [catálogo de relíquias, juramentos e bosses](CATALOGO.md).

Valores das cartas e recursos usam números nítidos. Distribuição, compra,
revelação e recolhimento têm animações suaves, respeitando a preferência por
movimento reduzido do sistema. Os comandos continuam disponíveis durante os efeitos.

As cartas são distribuídas alternadamente entre jogador e rival. Fichas viajam
até a aposta e retornam ao saldo no resultado; vitórias recebem um brilho breve
e os retratos reagem ao duelo. A [direção de arte](ART-DIRECTION.md) registra
a origem da ilustração e o prompt usado.

Além do Viajante, três origens são desbloqueadas ao jogar: Herdeiro Arruinado
(vença um encontro), Exilada (termine uma jornada) e Trapaceiro (divida uma mão).
A tela inicial mostra o baralho, a relíquia e o custo de cada origem. A origem é
escolhida para uma nova jornada; o save atual continua com seus recursos.

Os sete bosses têm retratos, objetos e falas que reagem ao duelo. O Cobrador
reconhece sua dívida familiar, as Gêmeas alternam sua presença e o Frei mostra
os sete sinos. O som é opcional, desligado por padrão, e pode ser ativado no topo.

Bolso Falso, Balança do Carrasco e Última Palavra adicionam decisões durante a
rodada. Os botões aparecem quando as regras permitem usá-los. Os efeitos ativados
ficam registrados junto às ações; abra **Como esta rodada foi calculada** para
ver bônus, limite do multiplicador, lucro, dívidas e fichas creditadas por mão.

Lia, Baltasar e a mensageira podem reaparecer em regiões posteriores. Custos e
consequências são mostrados antes de escolher, e **Sua jornada** guarda o registro.
O desfecho da mensageira depende de proteger ou vender sua informação. Recusar
um encontro encerra essa história, sem perdoar dívidas existentes.

## Jogar

Requer **Python 3.10 ou superior** e um navegador moderno. A campanha visual usa
somente a biblioteca padrão: não precisa instalar dependências Python adicionais.

```bash
git clone https://github.com/GustaGol0/count-queen.git
cd count-queen
python jogar_visual.py
```

No Windows, abra **Jogar Count e Queen.bat** ou use `py jogar_visual.py`.
No macOS/Linux, use `python3 jogar_visual.py` quando necessário.
O inicializador abre o navegador e escolhe uma porta livre se 8000 estiver ocupada.
Mantenha a janela do terminal aberta enquanto joga; Ctrl+C encerra o servidor.

Durante o combate, use **P** para pedir, **S** para parar e **D** para dobrar.
O rodapé abre seu baralho, relíquias e histórico; clique no nome do personagem
para ver a jornada e em um símbolo de relíquia para consultar seu efeito.
As janelas fecham com **Esc**. O botão **Tela cheia** fica no topo.

Para iniciar sem abrir o navegador:

```bash
python -m count_queen.web --port 8000
```

Use o endereço informado no terminal. `localhost` e `127.0.0.1` funcionam somente
no computador que iniciou o jogo. O servidor atende uma única jornada local;
não há contas, multiplayer ou hospedagem pública automática.

## A jornada

A origem Viajante começa com 200 fichas e 52 cartas tradicionais. Seu adversário compra de outro
baralho. As cartas usadas vão para o descarte e a composição permanece entre
rodadas e encontros. Quando a pilha está curta, o descarte volta e é embaralhado;
nenhuma carta em uma mão volta à pilha durante a rodada.

Cada região oferece três juramentos: escolha um, com efeitos até o fim da jornada.
Juramentos não se repetem; os pares Fortuna/Glória e Lâmina/Quinta Carta não são
oferecidos juntos na mesma construção. Relíquias e outros juramentos podem se
combinar. As descrições avisam quando uma escolha bloqueia sua estratégia atual.

O mapa é um tabuleiro escuro com estradas douradas. Escolha um nó conectado da
próxima camada. A Bússola permite uma travessia lateral extra por região, sem
pular camadas ou bosses. O boss é sorteado uma vez e revelado antes do juramento.
Recarregar a página não refaz nenhuma dessas escolhas.

| Região | Bosses possíveis |
| --- | --- |
| Fronteira dos Esquecidos | Madame Ferrugem ou Frei Sete-Sinos, 50% cada |
| Cidade das Máscaras | Íris e Véspera ou O Cobrador de Nomes, 50% cada |
| Corte Sem Sol | A Duquesa das Cinzas ou O Astrônomo Cego, 50% cada |
| O Trono Vazio | O Rei Sem Rosto, sempre |

As três primeiras regiões têm cinco camadas de encontros e um boss. A última
oferece três camadas de preparação antes do Rei. Os pares de bosses têm a mesma
dificuldade-alvo; o balanceamento inicial ainda deve ser refinado com partidas humanas.

## Encontros e recursos

| Encontro | Objetivo e recompensa |
| --- | --- |
| Mesa comum | Duas vitórias em até três rodadas; +3 de prestígio, 20 fichas e escolha de relíquia comum/incomum. |
| Elite | Duas vitórias antes de duas derrotas; +7 de prestígio, 40 fichas e escolha de relíquia rara. |
| Boss das regiões 1–2 | Três vitórias antes de três derrotas; +12 de prestígio, 80 fichas e escolha mítica. |
| Boss da região 3 | Quatro vitórias antes de três derrotas; mesma categoria de recompensa. |
| Empório | Até duas compras e um serviço: oficina por 35 fichas ou ritual de afinidade. |
| Oficina | Uma intervenção gratuita: adicionar, remover, transformar ou marcar uma carta. |
| Evento | Escolhas que afetam fichas, prestígio ou baralho; juramentos e influência abrem alternativas. |
| Refúgio | 35 fichas, purificação de maldições ou uma bênção para o próximo encontro. |
| Sacrário | Escolher Nobreza/Tirania, fazer oferendas ou aceitar uma carta maldita por fichas. |

Pagamentos de apostas são separados das recompensas de encontro. Perder uma mesa
ou elite permite seguir com saldo suficiente, mas reduz o prestígio e não concede
recompensa. Bosses permitem uma revanche, custando 30 fichas por número da região.
Perder novamente ou desistir da revanche encerra a jornada.

Empates consomem uma rodada nas mesas comuns e não alteram o placar dos duelos.
Após dois empates consecutivos, o próximo empate comum é decidido pelo menor
número de cartas; persistindo a igualdade, você vence. Naturais e regras explícitas
do Rei têm precedência. Em split, o saldo de mãos vencidas e perdidas decide a rodada.

**Fichas** sustentam a sobrevivência: terminar sem ao menos uma ficha encerra a
jornada, salvo o Coração da Rainha. Gastar a última ficha na loja/evento também
pode encerrar a jornada. Apostas em andamento não contam como falência antecipada.

**Prestígio** vai de 0 a 100. Define influência e títulos, abre alternativas em eventos
a partir de 20 e desconto de 10% nas lojas a partir de 40. Ele não bloqueia o mapa.
Nobreza e Tirania são caminhos narrativos separados. Ganhos vêm principalmente de
encontros vencidos; perdas de mãos só custam prestígio quando um efeito explícito exige.

## Baralho, relíquias e juramentos

- Quatro raridades: seis comuns, seis incomuns, nove raras e seis míticas.
- Míticas só aparecem em recompensas de bosses; nunca nas lojas.
- Escolha até três opções de recompensa (quatro em elites com Caçador de Coroas),
  excluindo relíquias já possuídas. Se a categoria acabar, recebe 25 fichas extras.
- Bônus de lucro são aditivos e limitados a ×3, sem multiplicar a devolução da aposta.
- Afinidades concedem +15% de lucro por nível da melhor carta presente, até nível 5.
- Cartas recebem no máximo uma marca: Real, Dourada, Quebradiça ou Maldita.
- O baralho mantém ao menos 16 cartas permanentes e aceita até 80 cartas. No piso,
  a marca Quebradiça desaparece em vez de destruir a carta.
- Brasa e Carta da Coroa são cartas especiais temporárias dos respectivos bosses.
- O Trono troca mãos sem mudar a propriedade das cartas: elas voltam ao dono ao descartar.
- Dívida de juramento retém metade do lucro até ser paga. A Ampulheta cobra seu
  empréstimo na próxima região; não oferece crédito na região final.

O [catálogo](CATALOGO.md) descreve todos os efeitos e os ajustes para prestígio 0–100.

## O Rei Sem Rosto

O duelo tem três atos, duas vitórias por ato e um limite de quatro derrotas no total.
Você recupera 50 fichas entre atos.

1. **A Coroa se Lembra:** baralho adaptado à estratégia predominante da jornada,
   anunciado ao entrar na região final.
2. **O Preço dos Juramentos:** escolha uma entre duas cobranças baseadas nos seus
   juramentos. Ao vencer, consagre um juramento e remova sua contrapartida.
3. **Não Há Lugar Para Dois:** escolha Governar (limite 21; sacrifício de relíquia
   para prever uma carta, uma vez por rodada) ou Usurpar (limite 22; Carta da Coroa
   ajustável de 1 a 11, com empates comuns a favor do Rei).

O epílogo combina seu caminho anterior com a escolha final. A vitória registra seu
nome no Salão das Lendas e desbloqueia uma marca Real na primeira carta de cada
jornada futura. O desbloqueio é aplicado automaticamente e persiste no save.

## Controles e salvamento

Use os botões ou P (pedir), S (parar), D (dobrar) durante sua vez. ? abre a ajuda.
O botão Baralho mostra composição e descarte; a Lente exibe contagens exatas da
pilha restante. Relíquias e juramentos podem ser consultados a qualquer momento.
A interface respeita a preferência por movimento reduzido.

Cada ação grava `save_visual.json` atomicamente, incluindo os baralhos, mãos,
mapa, eventos, ofertas, juramentos, placares e estado do sorteador. Atualizar a
página ou reiniciar retoma exatamente dali. Ações de uma janela desatualizada
são rejeitadas; uma falha de gravação desfaz o movimento em memória.

Saves 0.4 são copiados para `save_visual.json.v1.bak` antes da migração. Nome,
fichas, itens, caminho e afinidades são preservados; prestígio antigo é convertido
por divisão por 100, limitado a 100. Apostas e seguro pendentes são devolvidos.
A campanha começa no mapa da primeira região, pois o save antigo não contém mapas.

Para testar sem tocar no save pessoal, use uma pasta existente:

```bash
python -m count_queen.web --save caminho/do/teste.json
```

A campanha de terminal continua disponível com `python main.py`, após instalar
`requirements.txt`. Suas [regras anteriores](LEGACY.md) e `save.json` são separados.

## Desenvolvimento e verificação

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python tools/playthrough_adventure.py 200
```

O playtest alterna as quatro origens, automatiza decisões em jornadas completas e verifica retomadas periódicas
por JSON. Ele não lê nem grava o save pessoal e não representa uma estratégia ótima.
Para QA visual opcional, com Playwright e Chromium já instalados:

```bash
python tools/check_adventure_ui.py
python tools/check_table_motion.py
python tools/check_journey_expansion.py
```

A ferramenta usa saves temporários e informa a pasta das capturas de tela.
O GitHub Actions executa os testes em Python 3.10, 3.12 e 3.13.

| Arquivo | Responsabilidade |
| --- | --- |
| `count_queen/adventure.py` | Mapa, combate, progressão, efeitos, bosses e persistência da campanha visual. |
| `count_queen/content.py` | Catálogo de relíquias, juramentos, marcas e adversários. |
| `count_queen/web.py` | Servidor local e API; adaptador de saves da mesa antiga mantido para regressões. |
| `count_queen/web_ui/` | Interface da campanha. |
| `count_queen/game.py` | Campanha anterior de terminal. |

### Visual pixelado e animações

A versão 0.5.1 traz símbolos próprios para as 24 relíquias, juramentos em contratos de pergaminho e revelações por raridade. Use **Tela cheia** no topo e **Esc** para sair. As animações respeitam a preferência de movimento reduzido do sistema. A fonte Pixelify Sans é distribuída localmente sob a licença em `FONT-LICENSE.txt`; não é necessário carregar fontes externas.
