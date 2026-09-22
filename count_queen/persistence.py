import json
import os
import tempfile
from pathlib import Path

from .config import SAVE_FILENAME


def salvar_estado_do_jogo(estado_do_jogo):
    destino = Path(SAVE_FILENAME).resolve()
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                         dir=destino.parent, delete=False) as arquivo:
            temporario = arquivo.name
            json.dump(estado_do_jogo, arquivo, indent=4, ensure_ascii=False)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, destino)
    finally:
        if temporario and os.path.exists(temporario):
            os.unlink(temporario)


def salvar_jogador(estado_do_jogo, jogador, contador_rodadas):
    estado_do_jogo['jogador_atual'] = {
        chave: valor for chave, valor in vars(jogador).items()
        if chave != 'maos' and not chave.startswith('_')
    }
    estado_do_jogo['contador_rodadas'] = contador_rodadas
    salvar_estado_do_jogo(estado_do_jogo)

def carregar_estado_do_jogo():
    try:
        with open(SAVE_FILENAME, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"jogador_atual": None, "herois_caidos": [], "herois_verdadeiros": [], "contador_rodadas": 0}
