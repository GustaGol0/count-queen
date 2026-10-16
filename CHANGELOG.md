# Notas de atualização

## Em desenvolvimento — Mesa Viva — 15/10/2026

- Nova apresentação ilustrada: nove retratos em um atlas local, incluindo as duas Gêmeas e uma adversária das mesas comuns. Traços expressivos, molduras de latão, feltro texturizado, cartas de papel e títulos em fonte serifada.
- Distribuição alternada entre jogador e rival, fichas animadas na aposta e no resultado, reação do retrato e brilho breve de vitória. O som do resultado acompanha a revelação. Efeitos são interrompidos com o próximo comando e respeitam movimento reduzido.
- Retratos também aparecem na apresentação do boss, no mapa e nos encontros. Verificação no Chromium cobre carregamento da arte, preservação do retrato entre jogadas, limpeza dos efeitos, recarga sem repetição e larguras de 320 a 1440 px.
- Três origens desbloqueáveis além do Viajante: Herdeiro Arruinado, Exilada e Trapaceiro. Cada uma altera recursos, relíquia, baralho ou preço de loja; saves antigos continuam como Viajante.
- Relíquias raras Bolso Falso, Balança do Carrasco e Última Palavra: guardar para a próxima rodada, transferir entre mãos divididas ou comprar após a revelação. Catálogo ampliado para 27 relíquias.
- Efeitos ativados na mesa e destaque nas relíquias; recibo por mão com fontes do multiplicador, limite aplicado, lucro e retenções de dívida.
- Retratos e objetos dos sete bosses, falas de abertura e resultado, reação à dobra de Ferrugem/Frei, alternância das Gêmeas, medidor de sinos e cobrança familiar contextual. Som opcional desligado por padrão.
- Três histórias em capítulos entre regiões. Escolhas persistem no diário, alteram recursos e recompensas e mudam o desfecho da mensageira após traição. A dívida familiar continua mesmo após abandonar a história.
- Novos testes cobrem desbloqueios, saves antigos, conservação da carta guardada, transferências, última compra, interação de relíquias, cálculos e consequências. 200 jornadas completas alternando as quatro origens; teste adicional no navegador cobre as três relíquias, as origens, os sete retratos, traição persistente e preferência de som.

- Números das cartas, fichas, apostas e placares em fonte limpa; valores grandes também no centro das cartas. Símbolos preservam a identidade do jogo, com bordas mais suaves.
- Distribuição e compras deslizam da pilha até a mão. Carta oculta vira na revelação; cartas são recolhidas ao continuar; saldo, aposta e resultado recebem movimentos curtos.
- Animações acompanham apenas ações confirmadas, não repetem ao recarregar e podem ser interrompidas pelo próximo comando. Movimento reduzido desativa os efeitos e limpa animações em andamento.
- Mesa de combate ocupa a área central, com cartas maiores, aposta sobre o feltro e ações junto à mão do jogador.
- Fichas e prestígio no topo; nome, relíquias equipadas e atalhos no rodapé. As antigas colunas laterais foram removidas.
- Baralho, histórico, jornada e catálogo abrem sob demanda. Cada símbolo equipado abre o efeito daquela relíquia.
- Pilha de compra na mesa mostra a quantidade restante e abre a inspeção do baralho.
- Mapa horizontal no computador e vertical no celular, com caminhos disponíveis e percorridos destacados.
- Cores da mesa acompanham a região. Contratos em pergaminho, revelações por raridade, tela cheia e movimento reduzido preservados.
- Transições curtas entre telas; ações especiais de relíquias aparecem quando disponíveis.
- Combate comum cabe em notebook de 1366 × 768; mãos longas e até quatro mãos divididas se reorganizam sem cortar cartas.
- Validação: 112 testes de regras/persistência; verificação no Chromium de 16 estados, navegação pelos menus, bloqueio de atalhos em janelas, rodada completa e recarga do save. Aquisições nas quatro raridades e tela cheia também verificadas.
- Verificação adicional de movimento: distribuição inicial, compra sem repetir cartas antigas, virada, recolhimento, resultado, recarga, comandos durante animações e mudança para movimento reduzido.

## 0.5.1 — Selos e Pergaminhos — 14/10/2026

- Interface pixelada com fonte local, contornos em blocos e mesa verde; menos frases decorativas e informações repetidas.
- 24 símbolos próprios para as relíquias, exibidos nas recompensas, na loja e no inventário.
- Juramentos apresentados como contratos em pergaminho com selo de cera e ação de assinar.
- Revelação ao adquirir relíquias: comum discreta, incomum com pequenas partículas, rara com maior destaque e mítica com uma entrada central mais elaborada. A escolha já está salva antes da animação; é possível fechar imediatamente ou usar Esc.
- Animações curtas de distribuição de cartas, seleção e caminhos percorridos. Respeito à preferência do sistema por movimento reduzido.
- Botão de tela cheia nos navegadores compatíveis, sincronizado ao sair com Esc.
- Raridades continuam sendo das relíquias; cartas do baralho mantêm seus valores, naipes e marcas.
- Verificação: 93 testes automatizados e fluxo no Chromium cobrindo telas da campanha, aquisição das quatro raridades, recarga do save, loja, contratos, tela cheia e larguras de celular/tablet/desktop.

## 0.5.0 — A Estrada da Coroa — 14/10/2026

A campanha visual agora é uma jornada de blackjack por quatro regiões: escolha
rotas, construa seu próprio baralho e enfrente adversários com regras próprias.

### Mapa e progressão

- Tabuleiro escuro com estradas douradas, caminhos alternativos e oito tipos de nó.
- Mesas, elites, bosses, Empório, oficina, eventos, refúgios e Sacrário jogáveis.
- Boss revelado antes do juramento; sorteios e ofertas permanecem fixos ao recarregar.
- Prestígio de 0 a 100 como influência, separado de Nobreza/Tirania e do avanço no mapa.
- Encontros com duração/placar limitados, recompensa própria e uma revanche paga por boss.

### Construção da jornada

- 24 relíquias: seis comuns, seis incomuns, seis raras e seis míticas.
- Míticas exclusivas de vitórias contra bosses das três primeiras regiões.
- 12 juramentos; escolha um entre três no começo de cada região, acumulando efeitos.
- Baralhos separados para jogador e rival, persistentes durante seus encontros;
  o baralho do jogador acompanha toda a jornada, com compra e descarte reais.
- Oficina para adicionar, remover, transformar ou marcar cartas; quatro marcas,
  com mínimo de 16 cartas permanentes e máximo de 80 cartas.
- Afinidades, comércio, dívidas, purificação e pactos integrados à interface.

### Sete bosses

- Região 1: Madame Ferrugem ou Frei Sete-Sinos, 50% cada.
- Região 2: Íris e Véspera ou O Cobrador de Nomes, 50% cada.
- Região 3: A Duquesa das Cinzas ou O Astrônomo Cego, 50% cada.
- Região final: O Rei Sem Rosto, com baralho adaptativo, cobranças de juramentos,
  consagração e escolha entre Governar e Usurpar.
- Epílogos conforme caminho e decisão final; desbloqueio de marca Real para jornadas futuras.

### Ajustes para as novas regras

- Manto da Nobreza concede de 5 a 25 fichas por rodada, conforme influência.
- Penalidades de juramentos foram adaptadas à escala 0–100 e descritas no catálogo.
- A marca Quebradiça preserva o piso de 16 cartas; o sacrifício de Governar é limitado a uma vez por rodada.
- Trono Vazio devolve cartas ao baralho do dono ao descartar; Carta da Coroa não pode ser trocada.
- Empates comuns têm desempate anunciado após duas ocorrências consecutivas.

### Saves e verificação

- Save completo após cada ação, incluindo mapa, escolhas, baralhos e estado do sorteador.
- Migração de saves 0.4 com backup `.v1.bak`, recursos preservados e apostas pendentes devolvidas.
- Campanha de terminal e seu save permanecem disponíveis com as regras anteriores.
- Testes de efeitos, bosses, jornada, migração e gravação atômica; playtest de 200 jornadas
  completas e QA no navegador em telas de desktop e celular.
- Balanceamento inicial: os pares têm dificuldade-alvo equivalente, ainda sujeito a ajuste
  com partidas humanas. A taxa de vitória do playtest não representa a dificuldade para todos os jogadores.

## 0.4.0 — A mesa ganha vida — 12/10/2026

Count & Queen agora tem uma mesa visual jogável no navegador: feltro verde,
detalhes em vinho e dourado, cartas em pergaminho e a jornada até a coroa.

### Mesa e controles

- Criação de personagem, cartas animadas e layout adaptado para telas menores.
- Apostas por fichas e botões para pedir, parar, dobrar, dividir e desistir.
  Ações indisponíveis ficam desabilitadas; divisões permitem até quatro mãos.
- Atalhos P, S e D durante a vez do jogador e ajuda pela tecla ?.
- Fichas, prestígio, título e progresso sempre à vista. Capítulos e adversários
  acompanham a jornada, até a disputa contra o Regente.
- Resumo de cada rodada e histórico das últimas 12 rodadas.
- Animações respeitam a preferência do sistema por movimento reduzido.

### Salvamento e inicialização

- Salvamento automático após cada ação em `save_visual.json`, separado do
  `save.json` da campanha de terminal.
- Atualizar a página ou reiniciar o servidor retoma a mesma rodada, incluindo
  baralho, carta oculta, mãos divididas e escolhas pendentes.
- Pedidos repetidos ou enviados por uma janela desatualizada são rejeitados.
  Se a gravação falhar, a ação é desfeita e o save anterior é preservado.
- `python jogar_visual.py` inicia a mesa e abre o navegador automaticamente.
  No Windows, também é possível abrir `Jogar Count e Queen.bat` com dois cliques.
- A mesa visual exige Python 3.10 ou superior e não precisa de dependências extras.
  Se a porta estiver ocupada, o inicializador escolhe uma porta livre.

### Escopo desta versão

- A interface visual inclui as rodadas e a progressão até a coroação.
- Lojas, eventos, aquisição de relíquias/afinidades e escolha da Tirania pelo
  Sacrário continuam disponíveis na campanha de terminal e aguardam telas próprias.
- O motor visual já trata os efeitos dos itens, seguro e Caleidoscópio para a
  próxima integração. Uma nova jornada visual começa sem esses itens.
- A mesa roda localmente, para uma jornada por servidor. `localhost` funciona
  no computador que iniciou o jogo; não é um endereço de hospedagem online.

### Verificação

- 61 testes automatizados passando, cobrindo também pagamentos, divisão de mãos,
  seguro, Caleidoscópio, coroação, carta oculta e recuperação do save visual.
- Fluxo jogável verificado no navegador, com retomada após atualização da página
  e conferência do layout em larguras de 390, 768 e 1.024 pixels.

## 0.3.0 — A disputa pela coroa — 22/09/2026

Esta atualização reúne as mudanças realizadas desde o início da revisão do projeto,
incluindo as correções de partidas e salvamento, os ajustes de eventos e as melhorias
motivadas pela campanha de avaliação.

### Campanha e ritmo

- Meta reduzida de 100.000 para 10.000 de prestígio na Nobreza, e de -100.000
  para -10.000 na Tirania. Faixas dos títulos ajustadas proporcionalmente.
- Chegar à meta abre a disputa pela coroa. É necessário vencer três rodadas antes
  de perder três; empates não contam. Em rodadas com split, vale o saldo de mãos
  vencidas e perdidas. Desistências contam como derrota.
- O Regente compra cartas até alcançar 18. Os adversários anteriores param em 17.
- Ao perder a disputa sem falir, o progresso retorna a ±9.000 e é possível tentar
  novamente. O placar da disputa é salvo ao sair.
- Capítulos e adversários acompanham o progresso: Taverna da Fronteira, Torneio
  do Castelo, Salão dos Nobres, Corte Real e Disputa pela Coroa.
- Epílogos distintos para a Nobreza e a Tirania, com placar final e registro no
  Salão das Lendas. Lojas e eventos não interrompem a disputa final.
- Modo rápido persistente, acionado com `r`, remove pausas e esperas artificiais.
  As escolhas continuam exigindo entrada; a tela final espera confirmação.
- Enter inicia a rodada e repete a última aposta, limitada ao saldo disponível.
- Visitas às lojas podem ser ignoradas.

### Economia, itens e regras

- Bônus de lucro agora são somados e limitados a x3, em vez de multiplicadores
  cumulativos que faziam o saldo crescer descontroladamente.
- Força do Sete: +75% de lucro ao vencer com um 7, em lugar de x7.
- Bênção dos Quatro Reinos: +25% por naipe adicional, em lugar de até x8.
- Afinidades: +15% por nível, até nível 5. O preço usa o nível da carta escolhida;
  uma afinidade alta não encarece todas as demais. Níveis antigos acima de 5 são
  preservados no save, mas seu efeito fica limitado ao novo máximo.
- Preços dos itens do Empório e dos rituais têm piso de 2% do saldo. Ofertas,
  descontos e preços de itens ficam fixos durante cada visita: digitar uma opção
  inválida não refaz o sorteio.
- Caleidoscópio: um uso por rodada, no primeiro pedido de carta ou dobra;
  não interfere nas duas cartas iniciais. O limite é compartilhado entre mãos.
- Joias Gêmeas realmente permitem novas divisões gratuitas após o primeiro
  split pago, inclusive sem saldo adicional. Limite de quatro mãos por rodada.
- Manto da Nobreza funciona nos dois caminhos e rende 25 fichas por nível.
- Desafio de Alto Risco: requer 500 de prestígio em valor absoluto e 100 fichas;
  aposta 10% do saldo, com mínimo de 100. Vitória avança 150 de prestígio no caminho
  escolhido; derrota retira 60 e recusa retira 15 de progresso.
- Risco de aposta usa o saldo anterior à rodada; pagamentos e bônus não alteram
  retroativamente o risco. Apostar todo o saldo alcança o fator correspondente.
- Removida a aplicação duplicada do Pacto do Tirano na perda proporcional de
  prestígio. Estourar na Tirania passa a reduzir o progresso, como outras derrotas.
- Blackjack natural vence um 21 com mais cartas; paga 3:2 também quando o dealer
  estoura. Duas mãos naturais empatam. Um 21 após split não é blackjack natural.
- Seguro vencedor retorna três vezes seu custo, incluindo a devolução do seguro.
- Dealer com blackjack segue o encerramento normal da rodada: contabiliza,
  salva, verifica derrota e permite encontros quando a jornada continua.
- Baralho vazio não prende o dealer num loop. Saldo abaixo de uma ficha encerra
  a jornada, evitando a solicitação de uma aposta impossível.

### Lojas, eventos e salvamento

- Lojas não dependem mais de rodadas múltiplas de 3 ou 5. Empório disponível desde
  a 3ª rodada e Sacrário desde a 5ª, com prioridade alternada e uma loja por rodada.
- Limites de espera garantem aparição após 8 tentativas elegíveis para o Empório,
  15 para o Sacrário, 20 para o Andarilho e 25 para o Desafio. Chances normais
  permanecem em 20%, 15%, 5% e 3%, respectivamente.
- Contadores de encontros persistem no save. Retomar a partida não refaz um sorteio
  já realizado na mesma rodada; rodadas inelegíveis não avançam a espera.
- Iniciar Nova Lenda zera rodadas e contadores de encontros, salva imediatamente
  o novo personagem e mantém o Salão das Lendas.
- Salvar e sair grava o estado atual, mesmo antes da primeira rodada.
- Resultados de lojas e eventos são salvos; derrota e acesso à disputa final são
  verificados antes de outra aposta ou encontro.
- Gravação por arquivo temporário e substituição atômica: uma falha ao gravar não
  trunca o save anterior. Arquivos usam UTF-8 e ficam na raiz do projeto,
  independentemente da pasta usada para iniciar o jogo.
- Retorno ao menu após terminar jornadas usa um laço, sem chamadas recursivas.
- Saves antigos continuam carregando com padrões para as novas preferências e o
  placar da coroação. Saldos e inventários existentes não são apagados na atualização.

### Organização e validação

- Consolidada a organização em módulos de modelos, regras, campanha, encontros,
  persistência e interface, preservando a reorganização local já existente.
- Entrada principal em `main.py`; `python count_queen.py` permanece compatível.
- README reescrito para refletir as regras atuais, instalação e comandos.
- Suíte de 45 testes automatizados, com cobertura de pagamentos, persistência,
  novas jornadas, encontros, economia, lojas, modo rápido e coroação nos dois caminhos.
- Adicionado workflow do GitHub Actions para executar testes em Python 3.10,
  3.12 e 3.13 a cada push ou pull request.
- Ferramenta `tools/playthrough.py` executa campanhas pela interface textual,
  sem alterar regras e usando saves temporários. Com a semente 42, campanhas novas
  atingiram a vitória em 532 rodadas na Nobreza e 248 na Tirania, ambas na primeira
  tentativa. Esses resultados são amostras, não uma garantia de duração ou vitória.

### Histórico da revisão local

- O save local foi resetado uma vez, a pedido do usuário, durante a etapa de correção
  de eventos. Esse reset não é parte da atualização publicada nem será aplicado
  aos saves de outros jogadores.
- A avaliação anterior continuou uma cópia da jornada existente até a rodada 2.262;
  ela motivou a revisão de ritmo e economia. Seus números não são diretamente
  comparáveis aos testes novos, que começaram do zero.
- Saves pessoais, dependências locais e transcrições de partidas não são publicados.
