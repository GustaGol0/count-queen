import random
import time

from colorama import Fore, Style

from .logic import (
    calcular_prestigio_ganho,
    calcular_prestigio_perdido,
    obter_nivel_de_nobreza,
    obter_titulo,
)
from .campaign import atualizar_coroacao, etapa, multiplicador_lucro, aposta_desafio
from .events import sortear_encontro, sortear_loja
from .models import Baralho, Dealer, Mao
from .persistence import salvar_estado_do_jogo, salvar_jogador
from .ui.terminal import limpar_tela, pausar, aguardar, configurar_ritmo
from .ui.view import menu_principal, mostrar_loja, mostrar_mochila, mostrar_sacrario_do_segredo


def jogar_blackjack():
    while jogar_jornada():
        pass


def jogar_jornada():
    jogador, estado_do_jogo = menu_principal()
    if jogador is None:
        return

    configurar_ritmo(jogador.modo_rapido)
    herois_verdadeiros = estado_do_jogo.get("herois_verdadeiros", [])
    contador_rodadas = estado_do_jogo.get("contador_rodadas", 0)

    while True:
        if finalizar_jornada(jogador, estado_do_jogo, contador_rodadas):
            return True
        desistiu_nesta_rodada = False
        limpar_tela()
        atualizar_coroacao(jogador)
        capitulo, adversario, limite_dealer = etapa(jogador)
        titulo_atual = obter_titulo(jogador.prestigio, jogador.genero)
        if jogador.coroacao_ativa:
            titulo_atual = 'Pretendente à Coroa'

        print("\n" + "="*60)
        print(Fore.YELLOW + Style.BRIGHT + "                     ~~~ COUNT & QUEEN ~~~")
        print("="*60)

        cor_prestigio = Fore.RED if jogador.caminho == 'tirania' else Fore.CYAN
        caminho_texto = " (Caminho Sombrio)" if jogador.caminho == 'tirania' else ""

        if jogador.nome in herois_verdadeiros:
            print(Fore.YELLOW + Style.BRIGHT + f"Jogador: {jogador.nome} | Título: {titulo_atual}")
        else:
            print(f"Jogador: {jogador.nome} | Título: {titulo_atual}")

        print(f"Prestígio: {cor_prestigio}{jogador.prestigio}{Style.RESET_ALL}{caminho_texto}")
        print(f"Fichas: {Fore.GREEN}{jogador.fichas}{Style.RESET_ALL} | Rodada: {contador_rodadas}")
        print("="*60)

        print(f"Capítulo: {capitulo} | Adversário: {adversario} (para em {limite_dealer})")
        progresso = -jogador.prestigio if jogador.caminho == 'tirania' else jogador.prestigio
        print(f"Rumo à coroa: {max(0, min(10000, progresso))}/10000")
        if jogador.coroacao_ativa:
            print(f"Coroação: {jogador.coroacao_vitorias}/3 vitórias | {jogador.coroacao_derrotas}/3 derrotas")
        print(f"Modo rápido: {'ligado' if jogador.modo_rapido else 'desligado'}")
        print("\n[j/Enter] Jogar | [m] Mochila | [r] Modo rápido | [s] Salvar e sair")
        escolha_menu = input("O que deseja fazer? ").lower()

        if escolha_menu == 'r':
            jogador.modo_rapido = not jogador.modo_rapido
            configurar_ritmo(jogador.modo_rapido)
            salvar_jogador(estado_do_jogo, jogador, contador_rodadas)
            continue
        if escolha_menu == 'm':
            mostrar_mochila(jogador)
            continue
        elif escolha_menu == 's':
            salvar_jogador(estado_do_jogo, jogador, contador_rodadas)
            print("\nSua jornada foi salva. Até a próxima!")
            break
        elif escolha_menu not in ('j', ''):
            continue

        if 'manto_nobreza' in jogador.itens:
            nivel_nobreza = obter_nivel_de_nobreza(abs(jogador.prestigio))
            if nivel_nobreza > 0:
                tributo = nivel_nobreza * 25
                jogador.fichas += tributo
                print(Fore.CYAN + f"\nO Manto da Nobreza concede seu tributo: +{tributo} fichas!")
                aguardar(2)

        baralho = Baralho()
        dealer = Dealer(adversario, limite_dealer)
        baralho.embaralhar()
        jogador.limpar_maos()

        aposta_principal = 0
        while True:
            print(f"\nVocê tem {Fore.GREEN}{jogador.fichas} fichas.")
            aposta_padrao = min(jogador.ultima_aposta, int(jogador.fichas))
            aposta_texto = input(f"{jogador.nome}, quanto você quer apostar? [Enter: {aposta_padrao}] ").strip()
            try:
                aposta_principal = int(aposta_texto) if aposta_texto else aposta_padrao
                if 0 < aposta_principal <= jogador.fichas:
                    break
                else:
                    print(Fore.RED + "Aposta inválida.")
            except ValueError:
                print(Fore.RED + "Entrada inválida.")

        jogador.ultima_aposta = aposta_principal
        jogador.fichas -= aposta_principal
        jogador.maos[0].aposta = aposta_principal

        jogador.pedir_carta(baralho, 0)
        dealer.pedir_carta(baralho, 0)
        jogador.pedir_carta(baralho, 0)
        dealer.pedir_carta(baralho, 0)

        comprou_seguro = False
        if 'manilha_sorte' in jogador.itens and dealer.mostrar_primeira_carta().valor == 'A' and len(jogador.maos) == 1:
            aposta_da_mao = jogador.maos[0].aposta
            seguro_custo = aposta_da_mao / 2
            if jogador.fichas >= seguro_custo:
                print(Fore.CYAN + "\nA Manilha da Sorte brilha! O Dealer mostra um Ás.")
                escolha_seguro = input(f"Deseja pagar {int(seguro_custo)} fichas para fazer um Seguro? (s/n): ").lower()
                if escolha_seguro == 's':
                    print("Você fez a aposta de Seguro.")
                    jogador.fichas -= seguro_custo
                    comprou_seguro = True

        if dealer.maos[0].e_blackjack:
            limpar_tela()
            print(Fore.RED + Style.BRIGHT + "\n--- REVELAÇÃO ---")
            print(f"O Dealer revela sua mão: {dealer.maos[0]}. Blackjack do Dealer!")
            if comprou_seguro:
                print(Fore.GREEN + "A Manilha da Sorte te protegeu!")
                jogador.fichas += seguro_custo * 3

        elif comprou_seguro:
            print(Fore.RED + "O Dealer não tem um Blackjack. Você perdeu o valor do seguro.")
            aguardar(2)

        primeiro_split_feito = False
        indice_mao_atual = 0

        while indice_mao_atual < len(jogador.maos) and not dealer.maos[0].e_blackjack:
            mao_atual = jogador.maos[indice_mao_atual]
            jogando_esta_mao = True

            while jogando_esta_mao:
                prefixo_mao = f"Mão {indice_mao_atual + 1}/{len(jogador.maos)}: " if len(jogador.maos) > 1 else "Sua mão: "
                print(f"\n{Style.BRIGHT}{prefixo_mao}{mao_atual}")
                if mao_atual.aposta > 0:
                    print(f"Aposta nesta mão: {Fore.YELLOW}{mao_atual.aposta} fichas.")
                print(f"Carta do Dealer: {dealer.mostrar_primeira_carta()}")

                if mao_atual.valor >= 21:
                    break

                prompt = "você quer 'p' (pedir) ou 's' (parar)?"
                if 'caleidoscopio_acaso' in jogador.itens and not jogador._oraculo_usado:
                    prompt = "você quer 'p' (usar o Caleidoscópio) ou 's' (parar)?"

                pode_dobrar = len(mao_atual.cartas) == 2 and jogador.fichas >= mao_atual.aposta
                pode_dividir = False
                pode_desistir = len(mao_atual.cartas) == 2 and indice_mao_atual == 0 and len(jogador.maos) == 1

                split_gratis = primeiro_split_feito and 'joias_gemeas' in jogador.itens
                if len(mao_atual.cartas) == 2 and (split_gratis or jogador.fichas >= mao_atual.aposta) and len(jogador.maos) < 4:
                    carta1, carta2 = mao_atual.cartas
                    if carta1.valor == carta2.valor:
                        pode_dividir = True

                if pode_dobrar:
                    prompt += ", 'd' (dobrar)"
                if pode_dividir:
                    prompt += ", 'sp' (split)"
                if pode_desistir:
                    prompt += ", 'des' (desistir)"

                acao = input(f"{jogador.nome}, {prompt}? ").lower()

                if acao == 'des' and pode_desistir:
                    desistiu_nesta_rodada = True
                    jogador.desistencias_consecutivas += 1
                    penalidade = min(5 * (2 ** (jogador.desistencias_consecutivas - 1)), 50)
                    if 'pacto_tirano' in jogador.itens:
                        penalidade *= 2
                    print(f"{jogador.nome} desiste. Metade da aposta foi devolvida.")
                    if jogador.desistencias_consecutivas > 1:
                        print(Fore.RED + f"A covardia consecutiva mancha sua honra! Você perde {int(penalidade)} de prestígio.")
                    jogador.fichas += mao_atual.aposta / 2

                    if jogador.caminho == 'tirania':
                        jogador.prestigio += penalidade
                    else:
                        jogador.prestigio -= penalidade

                    if 'espelho_tirano' in jogador.itens:
                        ganho_sombrio = int(penalidade * 2)
                        print(Fore.MAGENTA + f"O Espelho do Tirano reflete sua desonra! Você ganha {ganho_sombrio} fichas.")
                        jogador.fichas += ganho_sombrio

                    mao_atual.valor = -1
                    jogando_esta_mao = False

                elif acao == 'sp' and pode_dividir:
                    primeiro_split_feito = True
                    print("--- Você dividiu a mão! ---")
                    if not split_gratis:
                        jogador.fichas -= mao_atual.aposta
                    nova_mao = Mao()
                    mao_atual.veio_de_split = True
                    nova_mao.veio_de_split = True
                    nova_mao.aposta = mao_atual.aposta
                    nova_mao.adicionar_carta(mao_atual.cartas.pop(1))
                    jogador.maos.append(nova_mao)
                    jogador.pedir_carta(baralho, indice_mao_atual)
                    jogador.pedir_carta(baralho, len(jogador.maos) - 1)

                    if 'joias_gemeas' in jogador.itens:
                        if len(mao_atual.cartas) == 2 and mao_atual.cartas[0].valor == mao_atual.cartas[1].valor:
                            print(Fore.MAGENTA + "As Joias Gêmeas brilham! Você pode dividir novamente gratuitamente!")
                    continue

                elif acao == 'd' and pode_dobrar:
                    jogador.fichas -= mao_atual.aposta
                    mao_atual.aposta *= 2
                    print(f"Você dobrou! Aposta: {Fore.YELLOW}{mao_atual.aposta} fichas.")
                    jogador.pedir_carta(baralho, indice_mao_atual)
                    jogando_esta_mao = False

                elif acao == 'p':
                    jogador.pedir_carta(baralho, indice_mao_atual)

                elif acao == 's':
                    jogando_esta_mao = False

                else:
                    print(Fore.RED + "Comando inválido.")

            indice_mao_atual += 1

        if any(m.valor <= 21 and m.valor != -1 for m in jogador.maos):
            print("\n--- Vez do Dealer ---")
            dealer.jogar(baralho)
            print(f"Mão final do Dealer: {dealer.maos[0]}")

        print("\n" + "="*40)
        print(Fore.MAGENTA + Style.BRIGHT + "               RESULTADO FINAL")
        print("="*40)
        dealer_valor = dealer.maos[0].valor
        dealer_tem_blackjack = dealer.maos[0].e_blackjack

        resultado_rodada = 0
        for i, mao in enumerate(jogador.maos):
            prefixo_mao = f"Mão {i + 1}: " if len(jogador.maos) > 1 else ""
            print(f"\n{Style.BRIGHT}{prefixo_mao}{mao}")

            if mao.valor == -1:
                resultado_rodada -= 1
                print("Você desistiu desta mão.")
                continue

            if mao.valor > 21:
                resultado_rodada -= 1
                print(Fore.RED + "Você estourou!")
                perda = abs(calcular_prestigio_perdido(jogador, mao, 10))

                if jogador.caminho == 'tirania':
                    jogador.prestigio += perda
                    print(f"Sua derrota reduz sua infâmia. +{perda} de Prestígio.")
                else:
                    jogador.prestigio -= perda
                    print(f"Sua ousadia custou sua honra. -{perda} de Prestígio.")

                if 'espelho_tirano' in jogador.itens:
                    ganho_sombrio = perda * 2
                    print(Fore.MAGENTA + f"O Espelho do Tirano reflete sua desonra! Você ganha {ganho_sombrio} fichas.")
                    jogador.fichas += ganho_sombrio

            elif (dealer_valor > 21 or mao.valor > dealer_valor or mao.e_blackjack) and not dealer_tem_blackjack:
                resultado_rodada += 1
                print(Fore.GREEN + ("BLACKJACK!" if mao.e_blackjack else "Você venceu!"))

                lucro_base = mao.aposta * 1.5 if mao.e_blackjack else mao.aposta

                multiplicador = multiplicador_lucro(jogador, mao)
                lucro_base = round(lucro_base * multiplicador, 2)
                if multiplicador > 1:
                    print(Fore.MAGENTA + f"Bônus dos itens e afinidades: x{multiplicador:.2f}")

                jogador.fichas += mao.aposta + lucro_base

                ganho_de_honra = calcular_prestigio_ganho(jogador, mao, 75 if mao.e_blackjack else 25)
                jogador.prestigio += ganho_de_honra

                if jogador.caminho == 'tirania':
                    print(f"Sua vitória aumenta sua infâmia! {ganho_de_honra} de Prestígio.")
                else:
                    print(f"Sua lenda ecoa pelo reino! +{ganho_de_honra} de Prestígio.")

            elif mao.valor < dealer_valor or (dealer_tem_blackjack and not mao.e_blackjack):
                resultado_rodada -= 1
                print(Fore.RED + "Que pena, o Dealer venceu :(")
                perda = abs(calcular_prestigio_perdido(jogador, mao, 5))

                if jogador.caminho == 'tirania':
                    jogador.prestigio += perda
                    print(f"A derrota alimenta sua infâmia. +{perda} de Prestígio (negativo).")
                else:
                    jogador.prestigio -= perda
                    print(f"Uma derrota amarga. -{perda} de Prestígio.")

                if 'espelho_tirano' in jogador.itens:
                    ganho_sombrio = perda * 2
                    print(Fore.MAGENTA + f"O Espelho do Tirano reflete sua derrota! Você ganha {ganho_sombrio} fichas.")
                    jogador.fichas += ganho_sombrio

            else:
                if mao.e_blackjack and dealer_tem_blackjack:
                    print(Fore.BLUE + "Empate de Blackjacks! A aposta volta.")
                else:
                    print("Empate! A aposta volta.")
                jogador.fichas += mao.aposta

        if not desistiu_nesta_rodada and jogador.desistencias_consecutivas > 0:
            print(Fore.CYAN + "\nSua honra foi restaurada por lutar até o fim nesta rodada.")
            jogador.desistencias_consecutivas = 0

        if jogador.cooldown_apelo > 0:
            jogador.cooldown_apelo -= 1
        if jogador.cooldown_extorquir > 0:
            jogador.cooldown_extorquir -= 1

        print(f"\nSeu saldo final de fichas é: {Fore.GREEN}{Style.BRIGHT}{jogador.fichas}")

        desfecho = atualizar_coroacao(jogador, resultado_rodada)
        if desfecho == 'inicio':
            print("O Regente aceita seu desafio! Vença três rodadas antes de perder três. Empates não contam.")
        elif desfecho == 'recuo':
            print("O Regente defendeu a coroa. Reúna novamente 10.000 de prestígio para tentar outra vez.")
        contador_rodadas += 1
        salvar_jogador(estado_do_jogo, jogador, contador_rodadas)

        pausar("\nPressione Enter para continuar...")

        if finalizar_jornada(jogador, estado_do_jogo, contador_rodadas):
            return True

        # Sistema de lojas - aparecem aleatoriamente
        loja = None if jogador.coroacao_ativa else sortear_loja(contador_rodadas, estado_do_jogo)
        if loja and not jogador.coroacao_ativa:
            # Uma loja por rodada; prioridade alternada entre as duas.
            if loja == 'emporio':
                limpar_tela()
                print(Fore.YELLOW + "\n✨ Um mercador real se aproxima! ✨")
                print("O Empório Real está aberto para negócios!")
                if input("[Enter] Visitar | [s] Ignorar: ").strip().lower() != 's':
                    mostrar_loja(jogador, estado_do_jogo)

            elif loja == 'sacrario':
                limpar_tela()
                print(Fore.RED + "\n🕯️ Uma presença sombria te observa... 🕯️")
                print("O Sacrário do Segredo sussurra seu nome...")
                if input("[Enter] Visitar | [s] Ignorar: ").strip().lower() != 's':
                    mostrar_sacrario_do_segredo(jogador, estado_do_jogo)

        salvar_jogador(estado_do_jogo, jogador, contador_rodadas)
        if finalizar_jornada(jogador, estado_do_jogo, contador_rodadas):
            return True

        # Evento aleatório: Encontro com Andarilho Misterioso (5% de chance)
        if sortear_encontro('andarilho', contador_rodadas, estado_do_jogo, elegivel=not jogador.coroacao_ativa):
            limpar_tela()
            print(Fore.MAGENTA + "\n--- Encontro Inesperado ---")
            print("Um andarilho misterioso se aproxima...")
            print('"Viajante, posso oferecer-lhe uma proposta..."')

            ofertas = [
                {"texto": "Trocar 200 fichas por 100 de prestígio", "fichas": -200, "prestigio": 100},
                {"texto": "Trocar 100 de prestígio por 300 fichas", "fichas": 300, "prestigio": -100},
                {"texto": "Arriscar 500 fichas em um jogo de sorte (50% chance de dobrar)", "tipo": "aposta"}
            ]

            oferta = random.choice(ofertas)
            print(f'\n"{oferta["texto"]}"')
            escolha_andarilho = input("\nAceita? (s/n): ").lower()

            if escolha_andarilho == 's':
                if oferta.get("tipo") == "aposta":
                    if jogador.fichas >= 500:
                        jogador.fichas -= 500
                        if random.random() < 0.5:
                            jogador.fichas += 1000
                            print(Fore.GREEN + "\n🎲 A sorte sorriu para você! +500 fichas!")
                        else:
                            print(Fore.RED + "\n🎲 A sorte não estava ao seu lado... -500 fichas.")
                    else:
                        print(Fore.RED + "\nVocê não tem fichas suficientes.")
                else:
                    pode_fazer = True
                    if oferta["fichas"] < 0 and jogador.fichas < abs(oferta["fichas"]):
                        pode_fazer = False
                        print(Fore.RED + "\nVocê não tem fichas suficientes.")
                    elif oferta["prestigio"] < 0 and jogador.prestigio < abs(oferta["prestigio"]):
                        pode_fazer = False
                        print(Fore.RED + "\nVocê não tem prestígio suficiente.")

                    if pode_fazer:
                        jogador.fichas += oferta["fichas"]
                        jogador.prestigio += oferta["prestigio"]
                        print(Fore.GREEN + "\nNegócio fechado! O andarilho desaparece na névoa...")
                        estado_do_jogo["jogador_atual"]["fichas"] = jogador.fichas
                        estado_do_jogo["jogador_atual"]["prestigio"] = jogador.prestigio
                        salvar_estado_do_jogo(estado_do_jogo)
            else:
                print('\nO andarilho dá de ombros. "Outra vez, talvez..." e desaparece.')

            salvar_jogador(estado_do_jogo, jogador, contador_rodadas)
            pausar("\nPressione Enter para continuar...")

        salvar_jogador(estado_do_jogo, jogador, contador_rodadas)
        if finalizar_jornada(jogador, estado_do_jogo, contador_rodadas):
            return True

        # Evento aleatório: Desafio de Alto Risco (3% de chance, requer prestígio alto)
        if sortear_encontro('desafio', contador_rodadas, estado_do_jogo,
                            elegivel=abs(jogador.prestigio) >= 500 and jogador.fichas >= 100 and not jogador.coroacao_ativa):
            limpar_tela()
            print(Fore.RED + Style.BRIGHT + "\n⚔️ DESAFIO DE ALTO RISCO ⚔️")
            print("\nUm nobre arrogante te desafia para uma partida de apostas altas!")
            valor_desafio = aposta_desafio(jogador)
            print(f"Aposta obrigatória: {Fore.YELLOW}{valor_desafio} fichas")
            print("Se vencer: Dobra a aposta + 150 de prestígio na direção do seu caminho")
            print("Se perder: Perde a aposta + 60 de prestígio de progresso")

            aceitar_desafio = input("\nAceita o desafio? (s/n): ").lower()

            if aceitar_desafio == 's':
                jogador.fichas -= valor_desafio
                chance_vitoria = 0.55 if jogador.prestigio >= 1500 else 0.50

                print("\n🎴 As cartas são distribuídas...")
                aguardar(2)

                if random.random() < chance_vitoria:
                    print(Fore.GREEN + Style.BRIGHT + "\n🏆 VITÓRIA!")
                    jogador.fichas += valor_desafio * 2
                    jogador.prestigio += -150 if jogador.caminho == 'tirania' else 150
                    print(f"Você ganhou {valor_desafio * 2} fichas e 150 de prestígio na direção do seu caminho!")
                    print('O nobre se retira humilhado...')
                else:
                    print(Fore.RED + Style.BRIGHT + "\n💔 DERROTA!")
                    jogador.prestigio += 60 if jogador.caminho == 'tirania' else -60
                    print(f"Você perdeu {valor_desafio} fichas e 60 de prestígio de progresso.")
                    print('O nobre ri com desdém...')

                estado_do_jogo["jogador_atual"]["fichas"] = jogador.fichas
                estado_do_jogo["jogador_atual"]["prestigio"] = jogador.prestigio
                salvar_estado_do_jogo(estado_do_jogo)
                pausar("\nPressione Enter para continuar...")
            else:
                print('\nVocê recusa o desafio. "Covarde!" grita o nobre.')
                jogador.prestigio += 15 if jogador.caminho == 'tirania' else -15
                print(Fore.RED + "Sua recusa te custa 15 de prestígio de progresso.")
                estado_do_jogo["jogador_atual"]["prestigio"] = jogador.prestigio
                salvar_estado_do_jogo(estado_do_jogo)
                pausar("\nPressione Enter para continuar...")

        salvar_jogador(estado_do_jogo, jogador, contador_rodadas)
        if finalizar_jornada(jogador, estado_do_jogo, contador_rodadas):
            return True



def finalizar_jornada(jogador, estado_do_jogo, contador_rodadas):
    """Verifica o fim após rodadas, lojas e eventos, antes de outra aposta."""
    herois_caidos = estado_do_jogo.setdefault("herois_caidos", [])
    herois_verdadeiros = estado_do_jogo.setdefault("herois_verdadeiros", [])
    if atualizar_coroacao(jogador) == 'inicio':
        print("A disputa pela coroa está disponível! Vença três rodadas antes de perder três.")
        salvar_jogador(estado_do_jogo, jogador, contador_rodadas)
    # Eventos pós-rodada - verificar game over
    if jogador.fichas < 1:
        limpar_tela()
        print("\n" + "="*60)
        print(Fore.RED + Style.BRIGHT + "                    GAME OVER")
        print("="*60)
        print(f"\n{jogador.nome}, suas fichas acabaram...")
        print("Sua jornada chegou ao fim.")

        if jogador.nome not in herois_caidos:
            herois_caidos.append(jogador.nome)
            estado_do_jogo["herois_caidos"] = herois_caidos

        estado_do_jogo["jogador_atual"] = None
        salvar_estado_do_jogo(estado_do_jogo)

        print(f"\nSeu nome foi registrado no Salão das Lendas como um Herói Caído.")
        print(f"Rodadas jogadas: {contador_rodadas}")
        pausar("\nPressione Enter para retornar ao menu...")
        return True

    # Verificar vitória pelo caminho da nobreza
    if jogador.coroacao_concluida and jogador.caminho == 'nobreza':
        limpar_tela()
        print("\n" + "="*60)
        print(Fore.YELLOW + Style.BRIGHT + "              ⭐ VITÓRIA GLORIOSA! ⭐")
        print("="*60)
        titulo_final = 'Rei' if jogador.genero == 'h' else 'Rainha'
        print(f"\n{jogador.nome}, você alcançou o título máximo de {titulo_final}!")
        print("O Regente entrega a coroa. As portas do castelo se abrem ao povo.")
        print("Seu reinado começa com uma promessa: nenhuma voz ficará fora do salão.")
        print(f"Disputa final: {jogador.coroacao_vitorias} vitórias e {jogador.coroacao_derrotas} derrotas.")

        if jogador.nome not in herois_verdadeiros:
            herois_verdadeiros.append(jogador.nome)
            estado_do_jogo["herois_verdadeiros"] = herois_verdadeiros

        estado_do_jogo["jogador_atual"] = None
        salvar_estado_do_jogo(estado_do_jogo)

        print(f"\nFichas finais: {Fore.GREEN}{jogador.fichas}")
        print(f"Rodadas jogadas: {contador_rodadas}")
        input("\nPressione Enter para retornar ao menu...")
        return True

    # Verificar vitória pelo caminho da tirania
    if jogador.coroacao_concluida and jogador.caminho == 'tirania':
        limpar_tela()
        print("\n" + "="*60)
        print(Fore.RED + Style.BRIGHT + "              💀 VITÓRIA SOMBRIA! 💀")
        print("="*60)
        titulo_final = 'Tirano' if jogador.genero == 'h' else 'Tirana'
        print(f"\n{jogador.nome}, você ascendeu ao título temível de {titulo_final}!")
        print("O Regente depõe sua coroa. A corte se ajoelha diante do novo poder.")
        print("Sob seu estandarte, o reino aprende o preço de desafiar o trono.")
        print(f"Disputa final: {jogador.coroacao_vitorias} vitórias e {jogador.coroacao_derrotas} derrotas.")

        if jogador.nome not in herois_verdadeiros:
            herois_verdadeiros.append(jogador.nome)
            estado_do_jogo["herois_verdadeiros"] = herois_verdadeiros

        estado_do_jogo["jogador_atual"] = None
        salvar_estado_do_jogo(estado_do_jogo)

        print(f"\nFichas finais: {Fore.GREEN}{jogador.fichas}")
        print(f"Infâmia final: {Fore.RED}{jogador.prestigio}")
        print(f"Rodadas jogadas: {contador_rodadas}")
        input("\nPressione Enter para retornar ao menu...")
        return True

    return False
