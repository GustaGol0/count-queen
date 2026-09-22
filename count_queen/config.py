from pathlib import Path

PRESTIGIO_BASE_GANHO = 25
PRESTIGIO_BASE_PERDA = 5

SAVE_FILENAME = Path(__file__).resolve().parent.parent / "save.json"

ITENS_DA_LOJA = {
    'bencao_reinos_v2': {'nome': 'Bênção dos Quatro Reinos', 'preco': 400, 'descricao': 'Passivo: +25% de lucro por naipe além do primeiro. Bônus totais limitados a x3.'},
    'forca_sete': {'nome': 'Força do Sete', 'preco': 777, 'descricao': 'Permanente: +75% de lucro ao vencer com um 7. Soma com os outros bônus, até x3.'},
    'joias_gemeas': {'nome': 'Joias Gêmeas', 'preco': 900, 'descricao': 'Após o primeiro split pago, novas divisões são grátis. Máximo de quatro mãos.'},
    'manilha_sorte': {'nome': 'Manilha da Sorte', 'preco': 800, 'descricao': 'Ativo: Permite comprar um "Seguro" contra o Blackjack do Dealer.'},
    'caleidoscopio_acaso': {'nome': 'Caleidoscópio do Acaso', 'preco': 2500, 'descricao': 'Uma vez por rodada, no primeiro pedir/dobrar, escolha entre três cartas. Não altera a distribuição inicial.'}
}

ITENS_SACRARIO = {
    'espelho_tirano': {'nome': 'Espelho do Tirano', 'preco': 750, 'descricao': 'Permanente: Toda vez que perder prestígio, ganhe o dobro do valor em fichas.'},
    'manto_nobreza': {'nome': 'Manto da Nobreza', 'preco': 600, 'descricao': 'Permanente: Tributo por rodada de 25 fichas por nível, usando o valor absoluto do prestígio.'},
    'pacto_tirano': {'nome': 'Pacto do Tirano', 'preco': 250, 'descricao': 'Permanente: Ganhos e perdas de prestígio são dobrados.'}
}
