import random
import time

from colorama import Fore, Style, init

from .terminal import limpar_tela, pausar, aguardar, configurar_ritmo
from ..campaign import MAX_AFINIDADE, custo_afinidade, preco_escalado
from ..config import ITENS_DA_LOJA, ITENS_SACRARIO
from ..logic import obter_nivel_de_nobreza, obter_titulo
from ..models import Jogador, Mao
from ..persistence import salvar_estado_do_jogo, carregar_estado_do_jogo, salvar_jogador


def mostrar_placar_de_lendas(estado_do_jogo):
    herois_verdadeiros = estado_do_jogo.get("herois_verdadeiros", [])
    herois_caidos = estado_do_jogo.get("herois_caidos", [])
    print("\n--- SALÃO DAS LENDAS ---")
    if not herois_verdadeiros and not herois_caidos:
        print("Ainda não há lendas escritas...")
    else:
        print(Fore.YELLOW + Style.BRIGHT + "Heróis Verdadeiros:")
        print(", ".join(herois_verdadeiros) if herois_verdadeiros else "Ninguém... ainda.")
        print(Fore.RED + "\nHeróis Caídos:")
        print(", ".join(herois_caidos) if herois_caidos else "Ninguém... ainda.")
    print("------------------------")

def mostrar_mochila(jogador):
    limpar_tela()
    print("\n" + "="*60)
    print(Fore.CYAN + Style.BRIGHT + "                   ~~~ MOCHILA ~~~")
    print("="*60)

    if not jogador.itens and not jogador.afinidades:
        print("\nSua mochila está vazia!")
    else:
        if jogador.itens:
            print(Fore.YELLOW + "\nItens Adquiridos:")
            print("-" * 40)
            for item_id in jogador.itens:
                item_info = ITENS_DA_LOJA.get(item_id) or ITENS_SACRARIO.get(item_id)
                if item_info:
                    cor = Fore.RED if item_id in ITENS_SACRARIO else Fore.GREEN
                    print(cor + f"• {item_info['nome']}")
                    print(Style.DIM + f"  {item_info['descricao']}")

        if jogador.afinidades:
            print(Fore.MAGENTA + "\nAfinidades Encantadas:")
            print("-" * 40)
            for carta, nivel in jogador.afinidades.items():
                print(f"• Carta {carta}: Nível {nivel}")
                bonus = 15 * min(MAX_AFINIDADE, nivel)
                print(Style.DIM + f"  Bônus: +{bonus}% fichas ao vencer com {carta} na mão")

    print("\n" + "="*60)
    pausar("Pressione Enter para voltar...")

def mostrar_loja(jogador, estado_do_jogo):
    compras_feitas, ritual_feito = 0, 0
    candidatos = [(k, dict(v, preco=preco_escalado(v['preco'], jogador)))
                  for k, v in ITENS_DA_LOJA.items() if k not in jogador.itens]
    ofertas = random.sample(candidatos, k=min(len(candidatos), 3))
    item_promocao = random.choice([k for k, _ in ofertas]) if ofertas else None
    desconto = random.choice([0.15, 0.25, 0.35])
    while True:
        limpar_tela()
        print("\n" + "="*60)
        print(Fore.YELLOW + Style.BRIGHT + "                   ~~~ EMPÓRIO REAL ~~~")
        print("="*60)
        print(f"Suas fichas: {Fore.GREEN}{jogador.fichas}")
        print(Style.DIM + f"Você pode fazer até {2 - compras_feitas} compras e {1 - ritual_feito} rituais nesta visita.")
        print("------------------------------------------------------------")

        print(Fore.CYAN + "\nServiços Disponíveis:")
        cartas_aprimoraveis = [c for c in Mao.VALORES if jogador.afinidades.get(c, 0) < MAX_AFINIDADE]
        if ritual_feito < 1 and cartas_aprimoraveis:
            print("  [e] Ritual de Afinidade — escolha a carta para consultar o preço (máximo nível 5).")
        else:
            print("Nenhum ritual disponível nesta visita.")

        itens_disponiveis = [(item_id, detalhes) for item_id, detalhes in ITENS_DA_LOJA.items() if item_id not in jogador.itens]

        if not itens_disponiveis:
            print("\nVocê já comprou todos os itens disponíveis no Empório!")
        else:
            oferta_do_dia = [(k, v) for k, v in ofertas if k not in jogador.itens]

            item_promo_idx = next((i for i, (k, _) in enumerate(oferta_do_dia) if k == item_promocao), -1)
            desconto_percentual = int(desconto * 100)

            print(Fore.CYAN + "\nOferta do Dia:")
            for i, (item_id, detalhes) in enumerate(oferta_do_dia):
                if i == item_promo_idx:
                    preco_promocional = int(detalhes['preco'] * (1 - desconto))
                    print(Fore.GREEN + Style.BRIGHT + f"  [{i+1}] {detalhes['nome']} - PROMOÇÃO! {desconto_percentual}% OFF!")
                    print(Fore.GREEN + Style.BRIGHT + f"      Preço: {preco_promocional} fichas " + Style.DIM + f"(Original: {detalhes['preco']})")
                else:
                    print(f"  [{i+1}] {detalhes['nome']} - {Fore.YELLOW}{detalhes['preco']} fichas")
                print(f"      {Style.DIM}{detalhes['descricao']}")

        print("\n------------------------------------------------------------")
        escolha = input("Digite o número do item, 'e' para o ritual, ou 's' para sair: ").lower()

        if escolha == 's':
            break

        if escolha == 'e' and ritual_feito < 1 and cartas_aprimoraveis:
            carta = input("Carta para aprimorar (2-10, J, Q, K, A; s para cancelar): ").strip().upper()
            if carta not in cartas_aprimoraveis:
                print("Carta inválida, cancelamento ou nível máximo atingido.")
                pausar()
                continue
            custo = custo_afinidade(jogador, carta)
            nivel = jogador.afinidades.get(carta, 0)
            if jogador.fichas < custo:
                print(f"Fichas insuficientes. Custo: {custo}.")
                pausar()
                continue
            if input(f"Elevar {carta} ao nível {nivel + 1} por {custo} fichas? (s/n): ").lower() == 's':
                jogador.fichas -= custo
                jogador.afinidades[carta] = nivel + 1
                ritual_feito += 1
                salvar_jogador(estado_do_jogo, jogador, estado_do_jogo.get('contador_rodadas', 0))
                print(f"Afinidade com {carta}: nível {nivel + 1}!")
                pausar()
            continue

        if compras_feitas < 2 and itens_disponiveis:
            try:
                indice_escolhido = int(escolha) - 1
                if 0 <= indice_escolhido < len(oferta_do_dia):
                    item_id, detalhes = oferta_do_dia[indice_escolhido]
                    if indice_escolhido == item_promo_idx:
                        preco_final = int(detalhes['preco'] * (1 - desconto))
                    else:
                        preco_final = detalhes['preco']

                    if jogador.fichas >= preco_final:
                        jogador.fichas -= preco_final
                        jogador.itens.append(item_id)
                        compras_feitas += 1
                        estado_do_jogo["jogador_atual"]["fichas"] = jogador.fichas
                        estado_do_jogo["jogador_atual"]["itens"] = jogador.itens
                        salvar_estado_do_jogo(estado_do_jogo)
                        print(Fore.GREEN + f"\nVocê adquiriu '{detalhes['nome']}'!")
                        pausar("Pressione Enter para continuar...")
                        if compras_feitas >= 2:
                            print(Fore.YELLOW + "\nVocê atingiu o limite de compras desta visita!")
                            aguardar(2)
                            break
                    else:
                        print(Fore.RED + "\nFichas insuficientes!")
                        pausar("Pressione Enter...")
                else:
                    print(Fore.RED + "\nEscolha inválida.")
                    pausar("Pressione Enter...")
            except ValueError:
                print(Fore.RED + "\nEntrada inválida.")
                pausar("Pressione Enter...")

def mostrar_sacrario_do_segredo(jogador, estado_do_jogo):
    CUSTO_FICHAS_MULTIPLICADOR = 10

    while True:
        limpar_tela()
        print("\n" + "="*50)
        print(Fore.RED + Style.BRIGHT + "            ~~~ SACRÁRIO DO SEGREDO ~~~")
        print("="*50)

        if jogador.caminho == 'nobreza':
            print(Fore.CYAN + "\nServiços Honrados:")
            recompensa_apelo = 500 * obter_nivel_de_nobreza(jogador.prestigio)
            if jogador.prestigio >= 100 and jogador.cooldown_apelo == 0:
                print(f"  [a] Apelo ao Povo - Custo: {Fore.MAGENTA}Nenhum{Style.NORMAL} | Recompensa: {Fore.GREEN}{recompensa_apelo} Fichas")
            elif jogador.cooldown_apelo > 0:
                print(Style.DIM + f"- Apelo ao Povo (Disponível em {jogador.cooldown_apelo} rodadas)")
            else:
                print(Style.DIM + "- Apelo ao Povo (Requer título de Cavaleiro/Dama)")
        else:
            print(Fore.CYAN + "\nServiços Sombrios:")
            if jogador.cooldown_extorquir == 0:
                print(f"  [x] Extorquir os Mercadores")
                print(f"      {Style.DIM}Custo: Aleatório (5-15% das fichas) | Recompensa: Aleatória (10-30% das fichas)")
                print(f"      {Style.DIM}Consequência: Perda adicional de Prestígio")
            else:
                print(Style.DIM + f"- A Extorsão estará disponível em {jogador.cooldown_extorquir} rodadas.")

        fez_pacto_inicial = jogador.caminho == 'tirania'

        if not fez_pacto_inicial:
            print(Fore.YELLOW + "\n⚠ AVISO: Comprar qualquer item aqui selará seu destino ao caminho sombrio!")
            print(f"Seu prestígio: {Fore.MAGENTA}{jogador.prestigio}")
        else:
            print(Fore.RED + "\nVocê já trilha o caminho das sombras. A glória agora é infâmia.")
            print(f"Sua infâmia (Prestígio): {Fore.MAGENTA}{jogador.prestigio}")
            print(f"Suas fichas: {Fore.GREEN}{jogador.fichas}")

        print("--------------------------------------------------")

        itens_a_venda = [(item_id, detalhes) for item_id, detalhes in ITENS_SACRARIO.items() if item_id not in jogador.itens]

        if not itens_a_venda:
            print("\nVocê já adquiriu todos os segredos sombrios deste lugar.")
        else:
            print(Fore.CYAN + "\nRelíquias disponíveis para pacto:")
            for i, (item_id, detalhes) in enumerate(itens_a_venda):
                if not fez_pacto_inicial:
                    print(f"  [{i+1}] {detalhes['nome']} - Custo: {Fore.MAGENTA}{detalhes['preco']} prestígio")
                else:
                    requisito_prestigio = -abs(detalhes['preco'])
                    custo_fichas = detalhes['preco'] * CUSTO_FICHAS_MULTIPLICADOR
                    if jogador.prestigio <= requisito_prestigio:
                        print(Fore.GREEN + f"  [{i+1}] {detalhes['nome']} (Disponível)")
                        print(f"      Requisito: {requisito_prestigio} Prestígio | Custo: {Fore.YELLOW}{custo_fichas} fichas")
                    else:
                        print(Style.DIM + f"  [{i+1}] {detalhes['nome']} (Bloqueado)")
                        print(Style.DIM + f"      Requisito: {requisito_prestigio} de Prestígio")
                print(f"      {Style.DIM}{detalhes['descricao']}")

        print("\n--------------------------------------------------")
        escolha = input("Digite o número da relíquia, 'a' para apelo, 'x' para extorquir, ou 's' para sair: ").lower()

        if escolha == 's':
            break

        if escolha == 'a' and jogador.caminho == 'nobreza' and jogador.prestigio >= 100 and jogador.cooldown_apelo == 0:
            recompensa = 500 * obter_nivel_de_nobreza(jogador.prestigio)
            jogador.fichas += recompensa
            jogador.cooldown_apelo = 10
            print(Fore.GREEN + f"\nO povo atende ao seu chamado! Você recebe {recompensa} fichas como tributo.")
            estado_do_jogo["jogador_atual"]["fichas"] = jogador.fichas
            estado_do_jogo["jogador_atual"]["cooldown_apelo"] = jogador.cooldown_apelo
            salvar_estado_do_jogo(estado_do_jogo)
            pausar("Pressione Enter para continuar...")
            continue

        if escolha == 'x' and jogador.caminho == 'tirania' and jogador.cooldown_extorquir == 0:
            custo_fichas = int(jogador.fichas * random.choice([0.05, 0.10, 0.15]))

            if jogador.fichas > custo_fichas:
                jogador.fichas -= custo_fichas

                percentuais = [0.10, 0.20, 0.30]
                pesos = [50, 30, 20]
                percentual_ganho = random.choices(percentuais, weights=pesos, k=1)[0]
                recompensa = int(jogador.fichas * percentual_ganho)

                jogador.fichas += recompensa
                jogador.prestigio -= 250
                jogador.cooldown_extorquir = 5

                print(Fore.GREEN + f"\nOperação bem-sucedida! Você extorquiu {recompensa} fichas.")
                print(Fore.RED + "Sua infâmia cresce... (-250 Prestígio)")
                estado_do_jogo["jogador_atual"]["fichas"] = jogador.fichas
                estado_do_jogo["jogador_atual"]["prestigio"] = jogador.prestigio
                estado_do_jogo["jogador_atual"]["cooldown_extorquir"] = jogador.cooldown_extorquir
                salvar_estado_do_jogo(estado_do_jogo)
            else:
                print(Fore.RED + "\nVocê não tem fichas suficientes para financiar a operação.")

            pausar("Pressione Enter para continuar...")
            continue

        try:
            indice_escolhido = int(escolha) - 1
            if 0 <= indice_escolhido < len(itens_a_venda):
                item_id, detalhes = itens_a_venda[indice_escolhido]

                if not fez_pacto_inicial:
                    if jogador.prestigio >= detalhes['preco']:
                        jogador.prestigio -= detalhes['preco']
                        jogador.itens.append(item_id)
                        jogador.caminho = 'tirania'
                        print(Fore.RED + Style.BRIGHT + "\n⚠ AO SACRIFICAR SUA HONRA POR PODER, SEU CAMINHO FOI SELADO!")
                        print("A partir de agora, toda vitória trará infâmia ao invés de glória.")
                        print("Você agora perde prestígio ao vencer e ganha ao perder.")
                        estado_do_jogo["jogador_atual"]["prestigio"] = jogador.prestigio
                        estado_do_jogo["jogador_atual"]["itens"] = jogador.itens
                        estado_do_jogo["jogador_atual"]["caminho"] = jogador.caminho
                        salvar_estado_do_jogo(estado_do_jogo)
                        pausar("Pressione Enter para continuar...")
                    else:
                        print(Fore.RED + "\nHonra insuficiente para fazer este sacrifício.")
                        pausar("Pressione Enter...")
                else:
                    requisito_prestigio = -abs(detalhes['preco'])
                    custo_fichas = detalhes['preco'] * CUSTO_FICHAS_MULTIPLICADOR
                    if jogador.prestigio <= requisito_prestigio:
                        if jogador.fichas >= custo_fichas:
                            jogador.fichas -= custo_fichas
                            jogador.itens.append(item_id)
                            print(Fore.GREEN + f"\nVocê adquiriu '{detalhes['nome']}'! O poder foi comprado com ouro.")
                            estado_do_jogo["jogador_atual"]["fichas"] = jogador.fichas
                            estado_do_jogo["jogador_atual"]["itens"] = jogador.itens
                            salvar_estado_do_jogo(estado_do_jogo)
                            pausar("Pressione Enter para continuar...")
                        else:
                            print(Fore.RED + "\nFichas insuficientes para pagar o preço do poder.")
                            pausar("Pressione Enter...")
                    else:
                        print(Fore.RED + "\nSua infâmia ainda não é grande o suficiente para este pacto.")
                        pausar("Pressione Enter...")
            else:
                print(Fore.RED + "\nEscolha inválida.")
                pausar("Pressione Enter...")
        except ValueError:
            print(Fore.RED + "\nEntrada inválida.")
            pausar("Pressione Enter...")
def criar_novo_jogador(herois_caidos, herois_verdadeiros):
    print("\nBem-vindo ao Count & Queen, nobre aventureiro!")
    while True:
        nome_do_jogador = input("Para começar sua jornada, diga-me seu nome: ")
        if nome_do_jogador in herois_caidos:
            print(Fore.RED + "Este nome pertence a um herói caído... Escolha outro.")
        elif not nome_do_jogador.strip():
            print(Fore.RED + "O nome não pode estar em branco.")
        else:
            genero_jogador = ''
            while genero_jogador not in ['h', 'm']:
                genero_jogador = input("Você será um herói ou uma heroína? (h/m): ").lower()
            if nome_do_jogador in herois_verdadeiros:
                print(Fore.YELLOW + Style.BRIGHT + f"\nO seu nome já está no Salão das Lendas, {nome_do_jogador}!")
            else:
                print(f"\nÉ uma honra conhecê-lo, {nome_do_jogador}. Sua lenda começa agora.")
            return Jogador(nome_do_jogador, genero=genero_jogador)

def menu_principal():
    configurar_ritmo(False)
    init(autoreset=True)
    estado_do_jogo = carregar_estado_do_jogo()
    dados_jogador_salvo = estado_do_jogo.get("jogador_atual")

    while True:
        limpar_tela()
        print(Fore.YELLOW + Style.BRIGHT + "\n.----------------------------------------------------.")
        print(r"|   _   _   _   _   _     _     _   _   _   _   _   |")
        print(r"|  / \ / \ / \ / \ / \   / \   / \ / \ / \ / \ / \  |")
        print(r"| ( C | O | U | N | T | ( & ) ( Q | U | E | E | N ) |")
        print(r"|  \_/ \_/ \_/ \_/ \_/   \_/   \_/ \_/ \_/ \_/ \_/  |")
        print("|                                                   |")
        print(Fore.YELLOW + Style.BRIGHT + "'----------------------------------------------------'")
        print("\n" + "="*52)

        if dados_jogador_salvo:
            fichas = dados_jogador_salvo.get('fichas', 0)
            prestigio = dados_jogador_salvo.get('prestigio', 0)
            genero = dados_jogador_salvo.get('genero', 'h')
            titulo = obter_titulo(prestigio, genero)
            print(f"   [1] Continuar a jornada de {Style.BRIGHT}{dados_jogador_salvo['nome']}{Style.NORMAL}")
            print(Style.DIM + f"               (Título: {titulo} | Fichas: {fichas})")
        else:
            print(Style.DIM + "   [1] Continuar Última Jornada (Nenhum jogo salvo)")

        print(Fore.WHITE + "\n   [2] Iniciar Nova Lenda")
        print("   [3] Ver o Salão das Lendas")
        print("   [4] Deixar o Reino")
        print("\n" + "="*52)

        escolha = input(f"\nEscolha seu destino: ")

        if escolha == '1':
            if dados_jogador_salvo:
                jogador = Jogador(
                    dados_jogador_salvo["nome"],
                    fichas=fichas,
                    prestigio=prestigio,
                    genero=genero,
                    desistencias_consecutivas=dados_jogador_salvo.get("desistencias_consecutivas", 0),
                    itens=dados_jogador_salvo.get("itens", []),
                    afinidades=dados_jogador_salvo.get("afinidades", {}),
                    caminho=dados_jogador_salvo.get("caminho", "nobreza"),
                    cooldown_apelo=dados_jogador_salvo.get("cooldown_apelo", 0),
                    cooldown_extorquir=dados_jogador_salvo.get("cooldown_extorquir", 0),
                    modo_rapido=dados_jogador_salvo.get("modo_rapido", False),
                    ultima_aposta=dados_jogador_salvo.get("ultima_aposta", 10),
                    coroacao_ativa=dados_jogador_salvo.get("coroacao_ativa", False),
                    coroacao_vitorias=dados_jogador_salvo.get("coroacao_vitorias", 0),
                    coroacao_derrotas=dados_jogador_salvo.get("coroacao_derrotas", 0),
                    coroacao_concluida=dados_jogador_salvo.get("coroacao_concluida", False)
                )
                print(f"\nBem-vindo de volta, {jogador.nome}!")
                aguardar(2)
                return jogador, estado_do_jogo
            else:
                print(Fore.RED + "\nNenhuma jornada em andamento para continuar.")
                aguardar(2)
        elif escolha == '2':
            herois_caidos = estado_do_jogo.get("herois_caidos", [])
            herois_verdadeiros = estado_do_jogo.get("herois_verdadeiros", [])
            jogador = criar_novo_jogador(herois_caidos, herois_verdadeiros)
            estado_do_jogo['encontros'] = {}
            estado_do_jogo.pop('ultima_loja', None)
            estado_do_jogo.pop('ultima_rodada_loja', None)
            salvar_jogador(estado_do_jogo, jogador, 0)
            input(f"\nSua jornada como {jogador.nome} começa... Pressione Enter.")
            return jogador, estado_do_jogo
        elif escolha == '3':
            limpar_tela()
            mostrar_placar_de_lendas(estado_do_jogo)
            pausar("\nPressione Enter para voltar ao menu...")
        elif escolha == '4':
            print("\nObrigado por visitar o reino de Count & Queen!")
            aguardar(2)
            return None, None
        else:
            print(Fore.RED + "\nOpção inválida, meu nobre.")
            aguardar(2)
