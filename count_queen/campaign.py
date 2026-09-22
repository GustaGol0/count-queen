"""Progressão, economia e disputa final da campanha."""

META_PRESTIGIO = 10000
MAX_AFINIDADE = 5


def etapa(jogador):
    pontos = abs(jogador.prestigio)
    if jogador.coroacao_ativa:
        return 'Disputa pela Coroa', 'Regente da Coroa', 18
    if pontos >= 5000:
        return 'Corte Real', 'Chanceler', 17
    if pontos >= 1500:
        return 'Salão dos Nobres', 'Duquesa das Cartas', 17
    if pontos >= 500:
        return 'Torneio do Castelo', 'Capitão da Guarda', 17
    return 'Taverna da Fronteira', 'Taberneiro', 17


def atualizar_coroacao(jogador, resultado=None):
    """Acesso permanente ao duelo; três vitórias antes de três derrotas."""
    if jogador.coroacao_ativa and resultado is not None:
        if resultado > 0:
            jogador.coroacao_vitorias += 1
        elif resultado < 0:
            jogador.coroacao_derrotas += 1
        if jogador.coroacao_vitorias >= 3:
            jogador.coroacao_concluida = True
            return 'vitoria'
        if jogador.coroacao_derrotas >= 3:
            jogador.coroacao_ativa = False
            jogador.coroacao_vitorias = jogador.coroacao_derrotas = 0
            jogador.prestigio = -9000 if jogador.caminho == 'tirania' else 9000
            return 'recuo'
    progresso = -jogador.prestigio if jogador.caminho == 'tirania' else jogador.prestigio
    if not jogador.coroacao_ativa and progresso >= META_PRESTIGIO:
        jogador.coroacao_ativa = True
        return 'inicio'
    return None


def multiplicador_lucro(jogador, mao):
    # Bônus aditivos: o conjunto inteiro nunca supera três vezes o lucro base.
    afinidade = max((jogador.afinidades.get(c.valor, 0) for c in mao.cartas), default=0)
    bonus = 0.15 * min(MAX_AFINIDADE, afinidade)
    if 'forca_sete' in jogador.itens and any(c.valor == '7' for c in mao.cartas):
        bonus += 0.75
    if 'bencao_reinos_v2' in jogador.itens:
        bonus += 0.25 * max(0, len({c.naipe for c in mao.cartas}) - 1)
    return min(3.0, 1.0 + bonus)


def preco_escalado(base, jogador):
    return max(base, int(jogador.fichas * 0.02))


def custo_afinidade(jogador, carta):
    nivel = min(MAX_AFINIDADE, jogador.afinidades.get(carta, 0))
    return preco_escalado(int(150 * 1.8 ** nivel), jogador)


def aposta_desafio(jogador):
    return min(int(jogador.fichas), max(100, int(jogador.fichas * 0.10)))
