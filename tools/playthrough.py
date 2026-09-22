"""Partida automatizada pela interface textual; salva apenas em pasta temporária.

Uso: python tools/playthrough.py [semente] [nobreza|tirania]
As regras e sorteios são reais; somente as decisões e pausas são automatizadas.
"""
import builtins
import json
from pathlib import Path
import random
import re
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from count_queen import game, models, persistence
from count_queen.ui import view, terminal


def run(seed=42, path='nobreza'):
    random.seed(seed)
    folder = Path(tempfile.mkdtemp(prefix='count-queen-playtest-'))
    old_save = persistence.SAVE_FILENAME
    persistence.SAVE_FILENAME = folder / 'save.json'
    log = (folder / 'transcript.txt').open('w', encoding='utf-8')
    original_print, original_input = builtins.print, builtins.input
    screen, hand = '', []
    finished, rounds, attempts, decisions = False, 0, 0, 0
    old_clear = (game.limpar_tela, models.limpar_tela, view.limpar_tela)
    old_sleep = terminal.time.sleep

    def capture(*args, **kwargs):
        nonlocal screen, finished
        text = re.sub(r'\x1b\[[0-9;]*m', '', ' '.join(map(str, args)))
        screen = (screen + text + '\n')[-30000:]
        log.write(text + '\n')
        if 'VITÓRIA GLORIOSA' in text or 'VITÓRIA SOMBRIA' in text:
            finished = True

    def clear():
        nonlocal screen
        screen = ''

    def score(ranks):
        value = sum(models.Mao.VALORES[r] for r in ranks)
        for _ in range(ranks.count('A')):
            if value > 21:
                value -= 10
        return value if value <= 21 else -value

    def choose(prompt=''):
        nonlocal hand, rounds, attempts, decisions
        prompt = re.sub(r'\x1b\[[0-9;]*m', '', prompt)
        decisions += 1
        if decisions > 100000:
            raise RuntimeError('Limite de decisões do playtest excedido')
        answer = ''
        if 'Escolha seu destino' in prompt:
            answer = '4' if finished else '2'
            if not finished:
                attempts += 1
        elif 'diga-me seu nome' in prompt:
            answer = f'Exploradora {attempts}'
        elif 'herói ou uma heroína' in prompt:
            answer = 'm'
        elif 'O que deseja fazer' in prompt:
            rounds = int(re.findall(r'Rodada: (\d+)', screen)[-1])
            answer = 'r' if 'Modo rápido: desligado' in screen else 'j'
            hand = []
            if rounds % 100 == 0 and answer == 'j':
                original_print(f'{path}: tentativa {attempts}, rodada {rounds}', flush=True)
        elif 'quanto você quer apostar' in prompt:
            balance = float(re.findall(r'Você tem ([\d.]+) fichas', screen)[-1])
            answer = str(max(1, min(1000, int(balance * .025))))
        elif 'Qual carta você escolhe' in prompt:
            options = re.findall(r'\[(\d+)\] (A|K|Q|J|10|[2-9]) de ', screen)
            best = max(options, key=lambda x: score(hand + [x[1]]))
            answer = best[0]
            hand.append(best[1])
        elif 'você quer' in prompt:
            hands = re.findall(r'Cartas \[(.*?)\] somando (\d+) pontos', screen)
            hand = re.findall(r'(A|K|Q|J|10|[2-9]) de ', hands[-1][0])
            total = int(hands[-1][1])
            upcard = re.findall(r'Carta do Dealer: (A|K|Q|J|10|[2-9]) de ', screen)[-1]
            soft = 'A' in hand and sum(models.Mao.VALORES[r] for r in hand) == total
            stop = total >= 18 if soft else total >= 17 or (total >= 13 and models.Mao.VALORES[upcard] <= 6) or (total == 12 and upcard in ('4', '5', '6'))
            answer = 's' if stop else 'p'
        elif 'Seguro?' in prompt:
            answer = 'n'
        elif 'Visitar' in prompt:
            answer = ''
        elif 'número do item' in prompt:
            balance = float(re.findall(r'Suas fichas: ([\d.]+)', screen)[-1])
            offers = re.findall(r'\[(\d+)\] ([^\n]+)', screen)
            answer = 's'
            for number, item in offers:
                price = re.search(r'(\d+) fichas', item)
                if price is None and 'PROMOÇÃO' in item:
                    price = re.search(r'Preço: (\d+) fichas', screen)
                if price and int(price[1]) < balance * .6:
                    answer = number
                    break
        elif 'número da relíquia' in prompt:
            answer = 's'
            if path == 'tirania':
                if '[x] Extorquir' in screen:
                    answer = 'x'
                elif 'Custo: 250 prestígio' in screen:
                    prestige = re.search(r'Seu prestígio: (-?\d+)', screen)
                    if prestige and int(prestige[1]) >= 250:
                        answer = '3'
            elif '[a] Apelo ao Povo' in screen:
                answer = 'a'
        elif 'Aceita o desafio' in prompt:
            answer = 's'
        elif 'Aceita?' in prompt:
            answer = 's' if path == 'nobreza' and 'Trocar 200 fichas por 100' in screen else 'n'
        elif 'Pressione Enter' in prompt:
            answer = ''
        else:
            raise RuntimeError(f'Comando desconhecido: {prompt!r}')
        log.write(prompt + ' ' + answer + '\n')
        return answer

    builtins.print, builtins.input = capture, choose
    game.limpar_tela = models.limpar_tela = view.limpar_tela = clear
    terminal.time.sleep = lambda _: None
    try:
        game.jogar_blackjack()
    finally:
        builtins.print, builtins.input = original_print, original_input
        game.limpar_tela, models.limpar_tela, view.limpar_tela = old_clear
        terminal.time.sleep = old_sleep
        terminal.configurar_ritmo(False)
        persistence.SAVE_FILENAME = old_save
        log.close()
        summary = dict(finished=finished, rounds=rounds + 1, attempts=attempts,
                       decisions=decisions, seed=seed, path=path, artifacts=str(folder))
        (folder / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
        original_print(json.dumps(summary), flush=True)
    return finished


if __name__ == '__main__':
    success = run(int(sys.argv[1]) if len(sys.argv) > 1 else 42,
                  sys.argv[2] if len(sys.argv) > 2 else 'nobreza')
    sys.exit(0 if success else 1)
