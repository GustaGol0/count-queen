import os
import time

MODO_RAPIDO = False


def configurar_ritmo(rapido):
    global MODO_RAPIDO
    MODO_RAPIDO = rapido


def pausar(mensagem="\nPressione Enter para continuar..."):
    if not MODO_RAPIDO:
        input(mensagem)


def aguardar(segundos):
    if not MODO_RAPIDO:
        time.sleep(segundos)


def limpar_tela():
    if not MODO_RAPIDO:
        os.system('cls' if os.name == 'nt' else 'clear')
