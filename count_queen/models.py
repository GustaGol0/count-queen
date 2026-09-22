import random

from .ui.terminal import limpar_tela


class Carta:
    def __init__(self, naipe, valor):
        self.naipe = naipe
        self.valor = valor

    def __repr__(self):
        return f"{self.valor} de {self.naipe}"

class Baralho:
    def __init__(self):
        naipes = ["Copas", "Ouros", "Paus", "Espadas"]
        valores = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.cartas = [Carta(n, v) for n in naipes for v in valores]

    def embaralhar(self):
        random.shuffle(self.cartas)

    def comprar_carta(self):
        if len(self.cartas) > 0:
            return self.cartas.pop()
        return None

class Mao:
    VALORES = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11}

    def __init__(self):
        self.cartas = []
        self.valor = 0
        self.ases = 0
        self.aposta = 0
        self.e_blackjack = False
        self.veio_de_split = False

    def __repr__(self):
        status = " (BLACKJACK!)" if self.e_blackjack else ""
        return f"Cartas {self.cartas} somando {self.valor} pontos{status}"

    def adicionar_carta(self, carta):
        self.cartas.append(carta)
        self.calcular_valor()

    def calcular_valor(self):
        self.valor = 0
        self.ases = 0
        self.e_blackjack = False

        for carta in self.cartas:
            self.valor += Mao.VALORES[carta.valor]
            if carta.valor == "A":
                self.ases += 1

        while self.valor > 21 and self.ases > 0:
            self.valor -= 10
            self.ases -= 1

        if len(self.cartas) == 2 and self.valor == 21 and not self.veio_de_split:
            self.e_blackjack = True

class Jogador:
    def __init__(self, nome, fichas=200, prestigio=0, genero='h',
                 desistencias_consecutivas=0, itens=None, afinidades=None,
                 caminho="nobreza", cooldown_apelo=0, cooldown_extorquir=0,
                 modo_rapido=False, ultima_aposta=10, coroacao_ativa=False,
                 coroacao_vitorias=0, coroacao_derrotas=0, coroacao_concluida=False):
        self.nome = nome
        self.fichas = fichas
        self.prestigio = prestigio
        self.genero = genero
        self.desistencias_consecutivas = desistencias_consecutivas
        self.maos = [Mao()]
        self.itens = [] if itens is None else itens
        self.afinidades = {} if afinidades is None else afinidades
        self.caminho = caminho
        self.cooldown_apelo = cooldown_apelo
        self.cooldown_extorquir = cooldown_extorquir
        self.modo_rapido = modo_rapido
        self.ultima_aposta = ultima_aposta
        self.coroacao_ativa = coroacao_ativa
        self.coroacao_vitorias = coroacao_vitorias
        self.coroacao_derrotas = coroacao_derrotas
        self.coroacao_concluida = coroacao_concluida
        self._oraculo_usado = False

    def __repr__(self):
        return f"Jogador: {self.nome}"

    def limpar_maos(self):
        self.maos = [Mao()]
        self._oraculo_usado = False
        self._fichas_inicio_rodada = self.fichas

    def pedir_carta(self, baralho, indice_mao=0):
        if ('caleidoscopio_acaso' in self.itens and not self._oraculo_usado
                and len(self.maos[indice_mao].cartas) >= 2):
            proximas_cartas = baralho.cartas[-3:] if len(baralho.cartas) >= 3 else baralho.cartas
            if len(proximas_cartas) > 0:
                limpar_tela()
                print("-- O Caleidoscópio do Acaso revela o futuro --")
                for idx, carta_futura in enumerate(proximas_cartas):
                    print(f" [{idx+1}] {carta_futura}")
                escolha_oraculo = ''
                while escolha_oraculo not in [str(i+1) for i in range(len(proximas_cartas))]:
                    escolha_oraculo = input("Qual carta você escolhe para o seu destino? ")

                carta_escolhida = proximas_cartas[int(escolha_oraculo)-1]
                baralho.cartas.remove(carta_escolhida)
                self.maos[indice_mao].adicionar_carta(carta_escolhida)
                self._oraculo_usado = True
                return

        carta_comprada = baralho.comprar_carta()
        if carta_comprada:
            self.maos[indice_mao].adicionar_carta(carta_comprada)
        else:
            print("O baralho acabou!")

class Dealer(Jogador):
    def __init__(self, nome="Dealer", limite=17):
        super().__init__(nome, fichas=9999)
        self.limite = limite

    def mostrar_primeira_carta(self):
        if self.maos[0].cartas:
            return self.maos[0].cartas[0]
        return None

    def jogar(self, baralho):
        while self.maos[0].valor < self.limite and baralho.cartas:
            self.pedir_carta(baralho, 0)
