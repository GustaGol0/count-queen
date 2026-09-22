def obter_fator_risco(fichas_totais, aposta):
    if aposta <= 0 or fichas_totais <= 0:
        return 1.0

    percentual_apostado = (aposta / fichas_totais) * 100

    if percentual_apostado >= 100: return 3.5
    if percentual_apostado > 75: return 2.75
    if percentual_apostado > 50: return 2.25
    if percentual_apostado > 35: return 1.75
    if percentual_apostado > 20: return 1.5
    if percentual_apostado > 10: return 1.25
    if percentual_apostado > 5: return 1.1
    return 1.0

def obter_fator_maestria(mao):
    if mao.e_blackjack: return 1.5
    if len(mao.cartas) >= 5: return 1.4
    if mao.valor == 21: return 1.3
    if mao.valor == 20: return 1.2
    if mao.valor == 19: return 1.1
    if mao.valor == 18: return 1.05
    return 1.0

def obter_fator_status(jogador):
    nivel = obter_nivel_de_nobreza(jogador.prestigio)
    if nivel == 0: return 1.0

    fator = 1.20 - (nivel * 0.05)

    return round(fator, 2)

def obter_titulo(prestigio, genero):
    if prestigio <= -10000: return "Tirano" if genero == 'h' else "Tirana"
    elif prestigio <= -5000: return "Flagelo do Reino"
    elif prestigio <= -1500: return "Senhor da Guerra" if genero == 'h' else "Senhora da Guerra"
    elif prestigio <= -500: return "Usurpador" if genero == 'h' else "Usurpadora"
    elif prestigio <= -150: return "Mestre Vigarista" if genero == 'h' else "Mestra Vigarista"
    elif prestigio <= -50: return "Ladrão de Estrada" if genero == 'h' else "Ladra de Estrada"
    elif prestigio <= -10: return "Foragido" if genero == 'h' else "Foragida"
    elif prestigio < 0: return "Malandro" if genero == 'h' else "Malandra"
    elif prestigio < 10: return "Plebeu" if genero == 'h' else "Plebeia"
    elif prestigio < 50: return "Cavaleiro" if genero == 'h' else "Dama"
    elif prestigio < 150: return "Barão" if genero == 'h' else "Baronesa"
    elif prestigio < 500: return "Visconde" if genero == 'h' else "Viscondessa"
    elif prestigio < 1500: return "Conde" if genero == 'h' else "Condessa"
    elif prestigio < 5000: return "Duque" if genero == 'h' else "Duquesa"
    elif prestigio < 10000: return "Príncipe" if genero == 'h' else "Princesa"
    else: return "Rei" if genero == 'h' else "Rainha"

def obter_nivel_de_nobreza(prestigio):
    if prestigio >= 10000: return 8
    if prestigio >= 5000: return 7
    if prestigio >= 1500: return 6
    if prestigio >= 500: return 5
    if prestigio >= 150: return 4
    if prestigio >= 50: return 3
    if prestigio >= 10: return 2
    if prestigio >= 0: return 1
    return 0

def calcular_prestigio_ganho(jogador, mao, PRESTIGIO_BASE_GANHO):
    fichas_antes_aposta = getattr(jogador, '_fichas_inicio_rodada', jogador.fichas + mao.aposta)

    fator_r = obter_fator_risco(fichas_antes_aposta, mao.aposta)
    fator_m = obter_fator_maestria(mao)
    fator_s = obter_fator_status(jogador)

    prestigio_final = int(PRESTIGIO_BASE_GANHO * fator_r * fator_m * fator_s)

    if 'pacto_tirano' in jogador.itens:
        prestigio_final *= 2

    if jogador.caminho == 'tirania':
        return -max(1, prestigio_final)
    else:
        return max(1, prestigio_final)

def calcular_prestigio_perdido(jogador, mao, PRESTIGIO_BASE_PERDA):
    ganho_equivalente = abs(calcular_prestigio_ganho(jogador, mao, 25))
    perda_proporcional = int(ganho_equivalente / 2.5)

    perda_final = max(PRESTIGIO_BASE_PERDA, perda_proporcional)


    if jogador.caminho == 'tirania':
        return -max(1, perda_final)
    else:
        return max(1, perda_final)
