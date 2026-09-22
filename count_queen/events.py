"""Sorteios por rodada com um limite de espera para cada encontro."""

import random


# Primeira rodada, chance por tentativa e máximo de tentativas sem aparecer.
REGRAS_ENCONTROS = {
    'emporio': (3, 0.20, 8),
    'sacrario': (5, 0.15, 15),
    'andarilho': (6, 0.05, 20),
    'desafio': (11, 0.03, 25),
}


def sortear_encontro(tipo, rodada, estado, elegivel=True):
    inicio, chance, limite = REGRAS_ENCONTROS[tipo]
    if not elegivel or rodada < inicio:
        return False
    encontros = estado.setdefault('encontros', {})
    progresso = encontros.setdefault(tipo, {'espera': 0, 'ultima_tentativa': 0})
    if progresso['ultima_tentativa'] >= rodada:
        return False
    progresso['ultima_tentativa'] = rodada
    progresso['espera'] += 1
    if progresso['espera'] >= limite or random.random() < chance:
        progresso['espera'] = 0
        return True
    return False


def sortear_loja(rodada, estado):
    if estado.get('ultima_rodada_loja', 0) >= rodada:
        return None
    estado['ultima_rodada_loja'] = rodada
    # Alternar a prioridade evita que o Empório sempre bloqueie o Sacrário.
    ordem = ('sacrario', 'emporio') if estado.get('ultima_loja') == 'emporio' else ('emporio', 'sacrario')
    for tipo in ordem:
        if sortear_encontro(tipo, rodada, estado):
            estado['ultima_loja'] = tipo
            return tipo
    return None
