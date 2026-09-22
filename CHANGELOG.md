# Notas de atualização

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
