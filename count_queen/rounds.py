"""Rodadas interativas sem entrada/saída, para a mesa visual."""

from .campaign import atualizar_coroacao, etapa, multiplicador_lucro
from .logic import calcular_prestigio_ganho, calcular_prestigio_perdido, obter_nivel_de_nobreza
from .models import Baralho, Dealer, Mao


class Rodada:
    def __init__(self, jogador):
        self.jogador = jogador
        self.baralho = None
        self.dealer = None
        self.fase = 'aposta'
        self.indice = 0
        self.primeiro_split = False
        self.seguro = 0
        self.escolhas = []
        self.acao_pendente = None
        self.resultados = []
        self.resumo = None
        self.tributo = 0
        self.cenario = list(etapa(jogador))

    def acoes(self):
        j = self.jogador
        if self.fase == 'aposta':
            return ['apostar'] if j.fichas >= 1 and not j.coroacao_concluida else []
        if self.fase == 'resultado':
            return ['continuar']
        if self.fase == 'seguro':
            return ['segurar', 'recusar_seguro']
        if self.fase == 'oraculo':
            return ['escolher']
        if self.fase != 'jogando':
            return []
        mao = j.maos[self.indice]
        acoes = ['pedir', 'parar']
        if len(mao.cartas) == 2:
            if j.fichas >= mao.aposta:
                acoes.append('dobrar')
            gratis = self.primeiro_split and 'joias_gemeas' in j.itens
            if (mao.cartas[0].valor == mao.cartas[1].valor and len(j.maos) < 4
                    and (gratis or j.fichas >= mao.aposta)):
                acoes.append('dividir')
            if self.indice == 0 and len(j.maos) == 1:
                acoes.append('desistir')
        return acoes

    def agir(self, acao, valor=None):
        if acao not in self.acoes():
            raise ValueError('Esta ação não está disponível agora.')
        j = self.jogador
        if acao == 'apostar':
            self.iniciar(valor)
        elif acao == 'continuar':
            self.fase = 'aposta'
            self.cenario = list(etapa(j))
        elif acao in ('segurar', 'recusar_seguro'):
            if acao == 'segurar':
                self.seguro = j.maos[0].aposta / 2
                j.fichas -= self.seguro
            self._apos_seguro()
        elif acao == 'escolher':
            if type(valor) is not int or not 0 <= valor < len(self.escolhas):
                raise ValueError('Escolha uma das cartas reveladas.')
            carta = self.escolhas[valor]
            self.baralho.cartas.remove(carta)
            j.maos[self.indice].adicionar_carta(carta)
            j._oraculo_usado = True
            self.escolhas = []
            self.fase = 'jogando'
            self._apos_compra(self.acao_pendente)
            self.acao_pendente = None
        elif acao == 'parar':
            self._avancar()
        elif acao == 'desistir':
            j.desistencias_consecutivas += 1
            perda = min(5 * 2 ** (j.desistencias_consecutivas - 1), 50)
            if 'pacto_tirano' in j.itens:
                perda *= 2
            j.fichas += j.maos[self.indice].aposta / 2
            self._penalizar(perda)
            j.maos[self.indice].valor = -1
            self._avancar()
        elif acao == 'dividir':
            mao = j.maos[self.indice]
            if not (self.primeiro_split and 'joias_gemeas' in j.itens):
                j.fichas -= mao.aposta
            self.primeiro_split = True
            nova = Mao()
            nova.aposta = mao.aposta
            mao.veio_de_split = nova.veio_de_split = True
            nova.adicionar_carta(mao.cartas.pop())
            mao.calcular_valor()
            j.maos.append(nova)
            self._comprar(mao)
            self._comprar(nova)
            if mao.valor >= 21:
                self._avancar()
        elif acao in ('pedir', 'dobrar'):
            mao = j.maos[self.indice]
            if acao == 'dobrar':
                j.fichas -= mao.aposta
                mao.aposta *= 2
            if ('caleidoscopio_acaso' in j.itens and not j._oraculo_usado
                    and self.baralho.cartas):
                self.escolhas = self.baralho.cartas[-3:]
                self.acao_pendente = acao
                self.fase = 'oraculo'
            else:
                self._comprar(mao)
                self._apos_compra(acao)

    def iniciar(self, aposta):
        j = self.jogador
        if type(aposta) is not int or not 1 <= aposta <= j.fichas:
            raise ValueError('Aposte um número inteiro entre 1 e seu saldo.')
        self.fichas_iniciais = j.fichas
        self.prestigio_inicial = j.prestigio
        self.tributo = 0
        if 'manto_nobreza' in j.itens:
            self.tributo = obter_nivel_de_nobreza(abs(j.prestigio)) * 25
            j.fichas += self.tributo
        atualizar_coroacao(j)
        self.cenario = list(etapa(j))
        self.dealer = Dealer(self.cenario[1], self.cenario[2])
        self.baralho = Baralho()
        self.baralho.embaralhar()
        j.limpar_maos()
        self.indice = 0
        self.primeiro_split = False
        self.seguro = 0
        self.resultados = []
        self.resumo = None
        j.ultima_aposta = aposta
        j.fichas -= aposta
        j.maos[0].aposta = aposta
        for _ in range(2):
            self._comprar(j.maos[0])
            self._comprar(self.dealer.maos[0])
        if ('manilha_sorte' in j.itens and self.dealer.mostrar_primeira_carta().valor == 'A'
                and j.fichas >= aposta / 2):
            self.fase = 'seguro'
        else:
            self._apos_seguro()

    def _comprar(self, mao):
        carta = self.baralho.comprar_carta()
        if carta:
            mao.adicionar_carta(carta)

    def _apos_seguro(self):
        if self.dealer.maos[0].e_blackjack:
            self.jogador.fichas += self.seguro * 3
            self._resolver()
        else:
            self.fase = 'jogando'
            if self.jogador.maos[self.indice].valor >= 21:
                self._avancar()

    def _apos_compra(self, acao):
        if acao == 'dobrar' or self.jogador.maos[self.indice].valor >= 21:
            self._avancar()

    def _avancar(self):
        self.indice += 1
        while self.indice < len(self.jogador.maos):
            if self.jogador.maos[self.indice].valor < 21:
                return
            self.indice += 1
        if any(0 <= m.valor <= 21 for m in self.jogador.maos):
            self.dealer.jogar(self.baralho)
        self._resolver()

    def _penalizar(self, perda):
        j = self.jogador
        j.prestigio += perda if j.caminho == 'tirania' else -perda
        if 'espelho_tirano' in j.itens:
            j.fichas += perda * 2

    def _resolver(self):
        j = self.jogador
        dealer = self.dealer.maos[0]
        placar = 0
        for mao in j.maos:
            bonus = 1
            retorno = 0
            if mao.valor == -1:
                texto, resultado = 'Desistência', -1
                retorno = mao.aposta / 2
            elif mao.valor > 21:
                texto, resultado = 'Estourou', -1
                self._penalizar(abs(calcular_prestigio_perdido(j, mao, 10)))
            elif (dealer.valor > 21 or mao.valor > dealer.valor or mao.e_blackjack) and not dealer.e_blackjack:
                texto, resultado = ('Blackjack!' if mao.e_blackjack else 'Vitória'), 1
                bonus = multiplicador_lucro(j, mao)
                lucro = round(mao.aposta * (1.5 if mao.e_blackjack else 1) * bonus, 2)
                retorno = mao.aposta + lucro
                j.fichas += retorno
                j.prestigio += calcular_prestigio_ganho(j, mao, 75 if mao.e_blackjack else 25)
            elif mao.valor < dealer.valor or (dealer.e_blackjack and not mao.e_blackjack):
                texto, resultado = 'Derrota', -1
                self._penalizar(abs(calcular_prestigio_perdido(j, mao, 5)))
            else:
                texto, resultado = 'Empate', 0
                retorno = mao.aposta
                j.fichas += retorno
            placar += resultado
            self.resultados.append({'texto': texto, 'resultado': resultado, 'retorno': retorno, 'bonus': bonus})
        if not any(m.valor == -1 for m in j.maos):
            j.desistencias_consecutivas = 0
        j.cooldown_apelo = max(0, j.cooldown_apelo - 1)
        j.cooldown_extorquir = max(0, j.cooldown_extorquir - 1)
        desfecho = atualizar_coroacao(j, placar)
        self.resumo = {'fichas': round(j.fichas - self.fichas_iniciais, 2),
                       'prestigio': j.prestigio - self.prestigio_inicial,
                       'desfecho': desfecho, 'placar': placar, 'tributo': self.tributo}
        self.fase = 'resultado'
