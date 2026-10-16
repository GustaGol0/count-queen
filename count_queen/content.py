"""Catálogo da campanha: textos públicos e números usados pelo motor."""

REGIONS = ['Fronteira dos Esquecidos', 'Cidade das Máscaras', 'Corte Sem Sol', 'O Trono Vazio']
SUITS = ['Copas', 'Ouros', 'Paus', 'Espadas']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RARITIES = ['comum', 'incomum', 'raro', 'mitico']


def entry(name, description, **extra):
    return {'nome': name, 'descricao': description, **extra}


RELICS = {}
for rarity, rows in {
    'comum': [
        ('manilha_sorte', 'Manilha da Sorte', 'Permite seguro por metade da aposta quando o adversário mostra um Ás. Retorno total: três vezes o custo se ele tiver blackjack.'),
        ('moeda_peregrino', 'Moeda do Peregrino', 'Receba 5 fichas ao entrar em um evento.'),
        ('broche_prudencia', 'Broche da Prudência', '+20% de lucro ao vencer com exatamente 17.'),
        ('dedal_costureira', 'Dedal da Costureira', 'No primeiro estouro de cada encontro, recupera 10% da aposta daquela mão.'),
        ('lente_escrivao', 'Lente do Escrivão', 'Mostra a quantidade exata de cada valor que ainda está na pilha de compra.'),
        ('ficha_cobre', 'Ficha de Cobre', 'O primeiro empate de cada encontro concede 5 fichas extras.'),
    ],
    'incomum': [
        ('forca_sete', 'Força do Sete', '+75% de lucro ao vencer com um 7.'),
        ('bencao_reinos_v2', 'Bênção dos Quatro Reinos', '+25% de lucro por naipe diferente além do primeiro.'),
        ('rosario_humildes', 'Rosário dos Humildes', '+40% de lucro ao vencer sem Ases nem figuras.'),
        ('luvas_duelista', 'Luvas do Duelista', '+30% de prestígio do encontro se você vencer pelo menos uma mão dobrada.'),
        ('bussola_contrabandista', 'Bússola do Contrabandista', 'Uma vez por região, atravesse para um nó não conectado da próxima camada. Não pula camadas ou bosses.'),
        ('selo_mercador', 'Selo do Mercador', 'Uma oferta extra por loja e 15% de desconto na primeira compra.'),
    ],
    'raro': [
        ('joias_gemeas', 'Joias Gêmeas', 'Depois do primeiro split pago, divisões adicionais são grátis. Até quatro mãos.'),
        ('pacto_tirano', 'Pacto do Tirano', 'Dobra ganhos e penalidades de prestígio.'),
        ('espelho_tirano', 'Espelho do Tirano', 'Recebe duas fichas por ponto de prestígio perdido em uma penalidade.'),
        ('tesoura_destino', 'Tesoura do Destino', 'Uma vez por encontro, descarta a carta que causaria estouro e para automaticamente. Não funciona após dobrar.'),
        ('mascara_impostor', 'Máscara do Impostor', 'Uma vez por encontro, permite dividir figuras/10 diferentes com o mesmo valor em pontos.'),
        ('ampulheta_usurario', 'Ampulheta do Usurário', 'Uma compra por loja pode ser feita pela metade do preço. O restante, com 25% de juros, é cobrado na próxima região. Dívida pendente bloqueia outro empréstimo.'),
    ],
    'mitico': [
        ('caleidoscopio_acaso', 'Caleidoscópio do Acaso', 'Uma vez por rodada, ao pedir ou dobrar, escolha uma das três próximas cartas. Compartilhado entre mãos.'),
        ('manto_nobreza', 'Manto da Nobreza', 'Recebe 5 fichas por faixa de influência no início da rodada, de 5 a 25. Rebalanceado para prestígio de 0 a 100.'),
        ('coroa_22', 'Coroa da Vigésima Segunda Hora', 'Uma vez por encontro, uma mão que chegaria a 22 passa a valer 21. Só age quando 22 seria estouro; não cria blackjack natural.'),
        ('cetro_sentencas', 'Cetro das Duas Sentenças', 'Uma vez por encontro, após a revelação, pode obrigar o adversário a comprar uma carta extra. Não funciona contra blackjack natural.'),
        ('coracao_exilada', 'Coração da Rainha Exilada', 'Uma vez por jornada, evita a falência e concede 200 fichas. O encontro é perdido e a relíquia se quebra.'),
        ('trono_vazio', 'Trono Vazio', 'Uma vez por região, antes de agir, troca sua mão inicial pela mão do rival, revelando-a. As duas deixam de ser naturais. Cartas emprestadas voltam ao dono no descarte. Indisponível com Carta da Coroa.'),
    ],
}.items():
    for key, name, description in rows:
        RELICS[key] = entry(name, description, raridade=rarity, preco={'comum':45, 'incomum':90, 'raro':150, 'mitico':0}[rarity])

OATHS = {
    'fortuna': entry('Bolso Cheio, Nome Esquecido', '+25% de lucro. Contrapartida: −25% de prestígio ganho.'),
    'gloria': entry('Meu Nome Antes do Ouro', '+40% de prestígio ganho. Contrapartida: −20% de lucro.'),
    'dobrar': entry('Dobrar ou Desaparecer', '+60% de lucro em vitórias dobradas. Contrapartida: perder uma dobra acrescenta uma penalidade de 2 de prestígio (4 com Pacto).'),
    'lamina': entry('Uma Só Lâmina', '+35% de lucro em vitórias com duas cartas. Contrapartida: dividir fica indisponível.'),
    'quinta': entry('A Quinta Carta é Sagrada', '+100% de lucro ao vencer com cinco ou mais cartas. Contrapartida: −20% de lucro em vitórias com duas cartas.'),
    'honra': entry('Jamais Abaixo a Cabeça', '+25% de prestígio ganho e +20 fichas por encontro vencido sem derrotas. Contrapartida: sem seguro ou desistência.'),
    'sete': entry('Sob o Número Sete', '+50% de lucro ao vencer com 7. Contrapartida: perder com 7 custa 1 de prestígio (2 com Pacto).'),
    'humilde': entry('Nenhum Rei à Minha Mesa', '+45% de lucro ao vencer sem J, Q ou K. Contrapartida: −25% se sua mão vencedora tiver figuras.'),
    'estrada': entry('A Estrada é Meu Palácio', 'Uma alternativa exclusiva nos eventos simples. Histórias recorrentes têm escolhas próprias. Contrapartida: lojas 20% mais caras.'),
    'divida': entry('Toda Dívida Será Paga', 'Recebe 150 fichas agora. Metade do lucro das vitórias paga uma dívida de 225; depois, desconto permanente de 10% nas lojas.'),
    'cacador': entry('Caçador de Coroas', 'Mais uma opção de relíquia em elites e +50% de fichas na recompensa dos bosses. Contrapartida: −20% de lucro nas mesas comuns.'),
    'ultima': entry('A Última Ficha Me Pertence', '+100% de lucro ao apostar todo o saldo. Contrapartida: nessas rodadas, sem seguro/desistência e derrota custa 2 de prestígio (4 com Pacto).'),
}

MARKS = {
    'real': entry('Real', 'Vencer com esta carta concede +1 de prestígio.'),
    'dourada': entry('Dourada', 'Vencer com esta carta concede +5 fichas.'),
    'quebradica': entry('Quebradiça', '+30% de lucro quando vence; depois, a carta é removida. No mínimo de 16 cartas permanentes, apenas a marca desaparece.'),
    'maldita': entry('Maldita', '+60% de lucro quando vence; perder a mão custa mais 5 fichas por carta maldita.'),
}

BOSSES = {
    'ferrugem': entry('Madame Ferrugem', '32 cartas: duas de 2–9 e quatro de J/Q/K; sem Ases. Para em 17. A primeira dobra da primeira rodada custa metade. Cada derrota dela remove até duas figuras do baralho.', frase='Aqui, querido, até a sorte paga aluguel.', regiao=0),
    'sinos': entry('Frei Sete-Sinos', '28 cartas: quatro de 2–7 e quatro Ases. Para em 18. A cada sete compras adicionais, concede uma bênção: veja sua próxima carta antes de pedir ou parar.', frase='A pressa é um pecado. Peça outra.', regiao=0),
    'gemeas': entry('Íris e Véspera', 'Íris usa 2–6 e Ases, para em 19. Véspera usa 8–K e poucos valores baixos, para em 16. Alternam a cada rodada. Cada irmã evita seu primeiro estouro e para.', frase='Você está jogando contra a errada.', regiao=1),
    'cobrador': entry('O Cobrador de Nomes', 'Cartas 4–10, Ases extras e poucas figuras. Para em 17. Escolha um contrato antes de cada rodada. Ao perder, escolha pagar 8 fichas ou perder 2 de prestígio.', frase='Fichas acabam. Seu nome ainda tem valor.', regiao=1),
    'cinzas': entry('A Duquesa das Cinzas', 'Duas cartas de cada valor. Para em 18. Sua menor carta não-Ás usada é queimada após cada rodada. Suas vitórias adicionam uma Brasa temporária ao seu descarte.', frase='Tudo o que você ama acaba alimentando o fogo.', regiao=2),
    'astronomo': entry('O Astrônomo Cego', 'Quatro de 3–8, um Ás e uma de cada figura. Limites alternam 19 → 21 → 23 → 21. Para três pontos abaixo do limite. Após a segunda derrota dele, troca qual carta inicial fica oculta na próxima rodada.', frase='Eu não vejo as cartas. Vejo o que elas deixam de ser.', regiao=2),
    'rei': entry('O Rei Sem Rosto', 'Três atos. Duas vitórias por ato antes de quatro derrotas no duelo inteiro. Adapta o baralho à sua estratégia, cobra juramentos e oferece Governar ou Usurpar. Recupera 50 fichas entre atos.', frase='Você acredita que veio tomar meu lugar. Foi para isso que eu o guiei.', regiao=3),
}
BOSS_PAIRS = [('ferrugem','sinos'),('gemeas','cobrador'),('cinzas','astronomo'),('rei',)]
ELITES = {
    'falsificador': entry('Falsificador da Fronteira', 'Muitas figuras, para em 16. Duas vitórias antes de duas derrotas.'),
    'novica': entry('Noviça dos Sinos', 'Cartas pequenas, para em 17. Concede uma bênção de previsão no início. Duas vitórias antes de duas derrotas.'),
    'escrivao': entry('Escrivão de Máscaras', 'Para em 17. Sem dobrar; você recebe +25% de lucro. Duas vitórias antes de duas derrotas.'),
    'aprendiz': entry('Aprendiz do Planetário', 'Primeira rodada tem limite 19; demais, 21. Para três pontos abaixo. Duas vitórias antes de duas derrotas.'),
}
NODE_NAMES = {'mesa':'Mesa de blackjack','elite':'Duelo de elite','boss':'Boss da região', 'loja':'Empório Real', 'oficina':'Oficina de cartas','evento':'Encontro na estrada','refugio':'Refúgio','sacrario':'Sacrário do Segredo'}
CONTRACTS = {
    'firme': entry('Mão Firme', 'Sem dobrar. O adversário precisa comprar até 18.'),
    'individual': entry('Conta Individual', 'Sem dividir. +25% de lucro nas vitórias.'),
    'testemunhas': entry('Sem Testemunhas', 'Sem desistir. Veja a primeira carta do adversário antes de apostar.'),
    'curta': entry('Assinatura Curta', 'No máximo dois pedidos adicionais por mão. Blackjack natural vencedor conta duas vitórias no placar.'),
}
CHARGES = {
    'dobrar': 'Primeira dobra da rodada custa 25% a mais.',
    'lamina': 'O Rei vence empates comuns contra suas mãos de duas cartas.',
    'sete': 'Seu primeiro 7 da rodada vale 6, mas preserva a identidade de 7 para os bônus.',
    'estrada': 'Antes da rodada, pague 8 fichas ou revele sua carta: o Rei passa a comprar até 19.',
    'fortuna': 'Taxa de 10% sobre o lucro das vitórias.',
    'gloria': 'Perder uma rodada custa 2 de prestígio.',
    'quinta': 'O Rei compra até 19.',
    'honra': 'O Rei vence empates comuns de 17 ou menos.',
    'humilde': 'Sua primeira figura de cada rodada vale 9.',
    'divida': 'Taxa fixa de 5 fichas ao vencer uma rodada.',
    'cacador': 'O Rei compra até 19.',
    'ultima': 'Apostar todo o saldo acrescenta 1 de prestígio à penalidade de derrota.',
}


ORIGINS = {
    'viajante': entry('Viajante', '200 fichas e um baralho tradicional de 52 cartas.', unlock='Disponível desde o início.'),
    'herdeiro': entry('Herdeiro Arruinado', '140 fichas, Balança do Carrasco e dívida familiar de 120. 25% do lucro de cada vitória paga essa dívida.', unlock='Vença qualquer encontro.'),
    'exilada': entry('Exilada', '140 fichas, Broche da Prudência e uma bênção inicial. Os quatro Reis do baralho são substituídos por cartas 2.', unlock='Conclua uma jornada, com vitória ou derrota.'),
    'trapaceiro': entry('Trapaceiro', '160 fichas, Bolso Falso e caminho da Tirania. Relíquias nas lojas custam 15% a mais.', unlock='Divida uma mão durante uma jornada.'),
}
RELICS.update({
    'bolso_falso': entry('Bolso Falso', 'Uma vez por encontro, guarde sua última carta pedida, enquanto a mão ainda estiver ativa. Ela será sua primeira carta da próxima rodada, sem blackjack natural. Não guarda cartas temporárias ou emprestadas.', raridade='raro', preco=150),
    'balanca_carrasco': entry('Balança do Carrasco', 'Uma vez por encontro, antes de pedir na mão dividida atual, transfira uma de suas cartas para outra mão dividida ainda não jogada. Mantenha pelo menos uma carta na origem.', raridade='raro', preco=150),
    'ultima_palavra': entry('Última Palavra', 'Após a revelação do rival, compre exatamente uma carta, uma vez por encontro. Aceitar o resultado preserva o uso. Exige uma única mão válida, sem dobra, desistência, blackjack ou limite de compras atingido. Compra direta, sem Oráculo.', raridade='raro', preco=150),
})
BOSS_PRESENTATION = {
    'ferrugem': {'object':'Moeda de ferrugem', 'intro':'A casa sempre cobra sua parte.', 'win':'Essa moeda ainda volta para mim.', 'loss':'Ouviu? É o som do seu troco.', 'double':'Finalmente alguém com coragem.'},
    'sinos': {'object':'Sete sinos', 'intro':'Escute antes de pedir.', 'win':'Até o silêncio pode abençoar.', 'loss':'O próximo sino será por você.', 'double':'A fé também exige uma aposta.'},
    'gemeas': {'object':'Espelho partido', 'intro':'Qual de nós você pensa conhecer?', 'win':'Minha irmã não cometerá esse erro.', 'loss':'Você estava olhando para a outra.'},
    'cobrador': {'object':'Livro de dívidas', 'intro':'Toda assinatura deixa uma marca.', 'win':'Considerarei isso um adiantamento.', 'loss':'Seu nome continua na minha lista.'},
    'cinzas': {'object':'Braseiro', 'intro':'Deixe uma carta para o fogo.', 'win':'Uma vitória também deixa cinzas.', 'loss':'Tudo encontra seu fim na chama.'},
    'astronomo': {'object':'Astrolábio', 'intro':'Os limites estão em movimento.', 'win':'Uma órbita que eu não previ.', 'loss':'As estrelas já haviam decidido.'},
    'rei': {'object':'Coroa vazia', 'intro':'Mostre o que a estrada fez de você.', 'win':'Sua promessa está começando a pesar.', 'loss':'A coroa ainda reconhece seu dono.'},
}
