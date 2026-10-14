"""Mesa local no navegador. Execute: python -m count_queen.web."""

import argparse
import copy
import errno
import hashlib
import json
import os
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .config import ITENS_DA_LOJA, ITENS_SACRARIO
from .logic import obter_titulo
from .models import Baralho, Carta, Dealer, Jogador, Mao
from .rounds import Rodada

STATIC = Path(__file__).parent / 'web_ui'
DEFAULT_SAVE = Path(__file__).resolve().parent.parent / 'save_visual.json'


def carta_json(carta):
    return {'valor': carta.valor, 'naipe': carta.naipe}


def mao_json(mao):
    return {**vars(mao), 'cartas': [carta_json(c) for c in mao.cartas]}


def ler_mao(dados):
    mao = Mao()
    mao.__dict__.update(dados)
    mao.cartas = [Carta(c['naipe'], c['valor']) for c in dados['cartas']]
    return mao


class Mesa:
    def __init__(self, save=DEFAULT_SAVE):
        self.save = Path(save)
        self.lock = threading.Lock()
        self.revisao = 0
        self.contador = 0
        self.historico = []
        self.rodada = None
        if self.save.exists():
            self.restaurar(json.loads(self.save.read_text(encoding='utf-8')))

    def exportar(self):
        dados = {'versao': 1, 'revisao': self.revisao, 'contador': self.contador,
                 'historico': self.historico, 'rodada': None}
        if self.rodada:
            r = self.rodada
            dados['jogador'] = {k: v for k, v in vars(r.jogador).items() if k != 'maos'}
            dados['maos'] = [mao_json(m) for m in r.jogador.maos]
            dados['rodada'] = {k: v for k, v in vars(r).items()
                                if k not in ('jogador', 'baralho', 'dealer', 'escolhas')}
            dados['baralho'] = [carta_json(c) for c in r.baralho.cartas] if r.baralho else None
            dados['dealer'] = None if not r.dealer else {
                'nome': r.dealer.nome, 'limite': r.dealer.limite, 'mao': mao_json(r.dealer.maos[0])}
            dados['escolhas'] = [r.baralho.cartas.index(c) for c in r.escolhas]
        return copy.deepcopy(dados)

    def restaurar(self, dados):
        if dados.get('versao') != 1:
            raise ValueError('Versão de save visual não suportada.')
        self.revisao = dados['revisao']
        self.contador = dados['contador']
        self.historico = dados['historico']
        self.rodada = None
        if dados['rodada'] is not None:
            jogador = Jogador('')
            jogador.__dict__.update(dados['jogador'])
            jogador.maos = [ler_mao(m) for m in dados['maos']]
            r = Rodada(jogador)
            r.__dict__.update(dados['rodada'])
            if dados['baralho'] is not None:
                r.baralho = Baralho()
                r.baralho.cartas = [Carta(c['naipe'], c['valor']) for c in dados['baralho']]
            if dados['dealer']:
                d = dados['dealer']
                r.dealer = Dealer(d['nome'], d['limite'])
                r.dealer.maos = [ler_mao(d['mao'])]
            r.escolhas = [r.baralho.cartas[i] for i in dados['escolhas']]
            self.rodada = r

    def salvar(self):
        temporario = None
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=self.save.parent,
                                             delete=False) as f:
                temporario = f.name
                json.dump(self.exportar(), f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporario, self.save)
        finally:
            if temporario and os.path.exists(temporario):
                os.unlink(temporario)

    def agir(self, dados):
        if dados.get('revisao') != self.revisao:
            raise ValueError('A mesa mudou em outra janela. Atualize antes de jogar.')
        anterior = copy.deepcopy(self.exportar())
        try:
            acao = dados.get('acao')
            if acao == 'nova':
                if self.rodada and (self.rodada.jogador.fichas >= 1
                                   and not self.rodada.jogador.coroacao_concluida):
                    raise ValueError('Sua jornada ainda está em andamento.')
                nome = dados.get('nome', '')
                genero = dados.get('genero', 'h')
                if not isinstance(nome, str) or not 1 <= len(nome.strip()) <= 30 or genero not in ('h', 'm'):
                    raise ValueError('Informe um nome de até 30 caracteres e um título válido.')
                self.rodada = Rodada(Jogador(nome.strip(), genero=genero))
                self.contador = 0
                self.historico = []
            else:
                if not self.rodada:
                    raise ValueError('Comece uma jornada para jogar.')
                fase = self.rodada.fase
                self.rodada.agir(acao, dados.get('valor'))
                if fase != 'resultado' and self.rodada.fase == 'resultado':
                    self.contador += 1
                    self.historico.insert(0, {'rodada': self.contador, **self.rodada.resumo})
                    self.historico = self.historico[:12]
            self.revisao += 1
            self.salvar()
        except Exception:
            self.restaurar(anterior)
            raise

    def estado(self):
        dados = {'revisao': self.revisao, 'contador': self.contador,
                 'historico': self.historico, 'jogador': None}
        if not self.rodada:
            return dados
        r = self.rodada
        j = r.jogador
        catalogo = {**ITENS_DA_LOJA, **ITENS_SACRARIO}
        titulo = obter_titulo(j.prestigio, j.genero)
        if j.coroacao_ativa and not j.coroacao_concluida:
            titulo = 'Pretendente à Coroa'
        dados.update({
            'jogador': {'nome': j.nome, 'fichas': j.fichas, 'prestigio': j.prestigio,
                        'titulo': titulo, 'caminho': j.caminho, 'ultima_aposta': j.ultima_aposta,
                        'itens': [{'id': i, **catalogo.get(i, {'nome': i, 'descricao': ''})} for i in j.itens],
                        'afinidades': j.afinidades, 'coroacao_ativa': j.coroacao_ativa,
                        'vitorias': j.coroacao_vitorias, 'derrotas': j.coroacao_derrotas},
            'fase': r.fase, 'acoes': r.acoes(), 'indice': r.indice,
            'cenario': r.cenario, 'maos': [mao_json(m) for m in j.maos],
            'dealer': [], 'dealer_valor': None,
            'escolhas': [carta_json(c) for c in r.escolhas],
            'resultados': r.resultados, 'resumo': r.resumo,
            'fim': 'vitoria' if j.coroacao_concluida else ('falencia' if j.fichas < 1 and r.fase in ('aposta', 'resultado') else None),
        })
        if r.dealer:
            revelar = r.fase in ('resultado', 'aposta')
            dados['dealer'] = [carta_json(c) if revelar or i == 0 else {'oculta': True}
                               for i, c in enumerate(r.dealer.maos[0].cartas)]
            if revelar:
                dados['dealer_valor'] = r.dealer.maos[0].valor
        return dados


def criar_servidor(mesa, host='127.0.0.1', port=8000):
    class Handler(BaseHTTPRequestHandler):
        def responder(self, codigo, conteudo, tipo='application/json; charset=utf-8'):
            if not isinstance(conteudo, bytes):
                conteudo = json.dumps(conteudo, ensure_ascii=False).encode('utf-8')
            self.send_response(codigo)
            self.send_header('Content-Type', tipo)
            self.send_header('Content-Length', str(len(conteudo)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(conteudo)

        def do_GET(self):
            caminho = urlparse(self.path).path
            if caminho == '/api/estado':
                with mesa.lock:
                    self.responder(200, mesa.estado())
            elif caminho == '/api/versao':
                digest = hashlib.sha256()
                for arquivo in sorted(STATIC.iterdir()):
                    digest.update(arquivo.read_bytes())
                self.responder(200, {'versao': digest.hexdigest()})
            elif caminho in ('/', '/app.js', '/style.css'):
                nome, tipo = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'),
                              '/style.css': ('style.css', 'text/css')}[caminho]
                self.responder(200, (STATIC / nome).read_bytes(), tipo + '; charset=utf-8')
            else:
                self.responder(404, {'erro': 'Página não encontrada.'})

        def do_POST(self):
            if self.path != '/api/acao':
                self.responder(404, {'erro': 'Página não encontrada.'})
                return
            origem = self.headers.get('Origin')
            if origem and urlparse(origem).netloc != self.headers.get('Host'):
                self.responder(403, {'erro': 'Origem inválida.'})
                return
            if self.headers.get_content_type() != 'application/json':
                self.responder(415, {'erro': 'Envie JSON.'})
                return
            try:
                tamanho = int(self.headers.get('Content-Length', '0'))
                if not 0 < tamanho <= 4096:
                    raise ValueError('Pedido inválido.')
                dados = json.loads(self.rfile.read(tamanho))
                if not isinstance(dados, dict):
                    raise ValueError('Pedido inválido.')
                with mesa.lock:
                    mesa.agir(dados)
                    self.responder(200, mesa.estado())
            except (ValueError, TypeError) as erro:
                self.responder(400, {'erro': str(erro)})
            except OSError:
                self.responder(500, {'erro': 'Não foi possível salvar. A ação foi desfeita; tente novamente.'})

    return ThreadingHTTPServer((host, port), Handler)


def main(abrir_navegador=False):
    from .adventure import AdventureMesa
    parser = argparse.ArgumentParser(description='Count & Queen — mesa visual local')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--save', type=Path, default=DEFAULT_SAVE)
    parser.add_argument('--open', action='store_true', default=abrir_navegador,
                        help='Abre a mesa no navegador padrão.')
    args = parser.parse_args()
    mesa = AdventureMesa(args.save)
    try:
        servidor = criar_servidor(mesa, args.host, args.port)
    except OSError as erro:
        if erro.errno != errno.EADDRINUSE:
            raise
        servidor = criar_servidor(mesa, args.host, 0)
    host_navegador = '127.0.0.1' if args.host == '0.0.0.0' else args.host
    url = f'http://{host_navegador}:{servidor.server_port}'
    print(f'Count & Queen: {url}', flush=True)
    print('Mantenha esta janela aberta enquanto joga. Ctrl+C encerra a mesa.', flush=True)
    if args.open:
        timer = threading.Timer(0.3, webbrowser.open, args=(url,))
        timer.daemon = True
        timer.start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == '__main__':
    main()
