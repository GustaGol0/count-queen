import random
import json
from colorama import Fore, Style, init
import os
import time

PRESTIGIO_BASE_GANHO = 25
PRESTIGIO_BASE_PERDA = 5

# ===================================================================
# --- CATÁLOGOS DAS LOJAS ---
# ===================================================================
ITENS_DA_LOJA = {
    'bencao_reinos_v2': {'nome': 'Bênção dos Quatro Reinos', 'preco': 400, 'descricao': 'Passivo: Seu lucro é multiplicado pelo número de naipes únicos na sua mão (até x8).'},
    'forca_sete': {'nome': 'Força do Sete', 'preco': 777, 'descricao': 'Permanente: Ganhos x7 ao vencer com um 7 na mão.'},
    'joias_gemeas': {'nome': 'Joias Gêmeas', 'preco': 900, 'descricao': 'Passivo: Permite "splitar" novamente de graça se a nova carta formar um par.'},
    'manilha_sorte': {'nome': 'Manilha da Sorte', 'preco': 800, 'descricao': 'Ativo: Permite comprar um "Seguro" contra o Blackjack do Dealer.'},
    'caleidoscopio_acaso': {'nome': 'Caleidoscópio do Acaso', 'preco': 2500, 'descricao': 'Ativo: Permite ver as 3 próximas cartas do baralho e escolher qual receber.'}
}

ITENS_SACRARIO = {
    'espelho_tirano': {'nome': 'Espelho do Tirano', 'preco': 750, 'descricao': 'Permanente: Toda vez que perder prestígio, ganhe o dobro do valor em fichas.'},
    'manto_nobreza': {'nome': 'Manto da Nobreza', 'preco': 600, 'descricao': 'Permanente: Receba um tributo em fichas a cada rodada (Nível de Nobreza x 100).'},
    'pacto_tirano': {'nome': 'Pacto do Tirano', 'preco': 250, 'descricao': 'Permanente: Ganhos e perdas de prestígio são dobrados.'}
}

# ===================================================================
# --- FUNÇÕES DE SUPORTE ---
# ===================================================================

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def obter_fator_risco(fichas_totais, aposta):
    if aposta <= 0 or fichas_totais <= 0: 
        return 1.0

    percentual_apostado = (aposta / (fichas_totais + aposta)) * 100
    
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
    if prestigio <= -100000: return "Tirano" if genero == 'h' else "Tirana"
    elif prestigio <= -50000: return "Flagelo do Reino"
    elif prestigio <= -15000: return "Senhor da Guerra" if genero == 'h' else "Senhora da Guerra"
    elif prestigio <= -5000: return "Usurpador" if genero == 'h' else "Usurpadora"
    elif prestigio <= -1500: return "Mestre Vigarista" if genero == 'h' else "Mestra Vigarista"
    elif prestigio <= -500: return "Ladrão de Estrada" if genero == 'h' else "Ladra de Estrada"
    elif prestigio <= -100: return "Foragido" if genero == 'h' else "Foragida"
    elif prestigio < 0: return "Malandro" if genero == 'h' else "Malandra"
    elif prestigio < 100: return "Plebeu" if genero == 'h' else "Plebeia"
    elif prestigio < 500: return "Cavaleiro" if genero == 'h' else "Dama"
    elif prestigio < 1500: return "Barão" if genero == 'h' else "Baronesa"
    elif prestigio < 5000: return "Visconde" if genero == 'h' else "Viscondessa"
    elif prestigio < 15000: return "Conde" if genero == 'h' else "Condessa"
    elif prestigio < 50000: return "Duque" if genero == 'h' else "Duquesa"
    elif prestigio < 100000: return "Príncipe" if genero == 'h' else "Princesa"
    else: return "Rei" if genero == 'h' else "Rainha"

def obter_nivel_de_nobreza(prestigio):
    if prestigio >= 100000: return 8
    if prestigio >= 50000: return 7
    if prestigio >= 15000: return 6
    if prestigio >= 5000: return 5
    if prestigio >= 1500: return 4
    if prestigio >= 500: return 3
    if prestigio >= 100: return 2
    if prestigio >= 0: return 1
    return 0
    
def calcular_prestigio_ganho(jogador, mao, PRESTIGIO_BASE_GANHO):
    fichas_antes_aposta = jogador.fichas + mao.aposta
    
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
    
    if 'pacto_tirano' in jogador.itens:
        perda_final *= 2

    if jogador.caminho == 'tirania':
        return -max(1, perda_final)
    else:
        return max(1, perda_final)

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
                bonus = 50 * nivel
                print(Style.DIM + f"  Bônus: +{bonus}% fichas ao vencer com {carta} na mão")
    
    print("\n" + "="*60)
    input("Pressione Enter para voltar...")

def salvar_estado_do_jogo(estado_do_jogo):
    with open('save.json', 'w') as arquivo:
        json.dump(estado_do_jogo, arquivo, indent=4)

def carregar_estado_do_jogo():
    try:
        with open('save.json', 'r') as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"jogador_atual": None, "herois_caidos": [], "herois_verdadeiros": [], "contador_rodadas": 0}

def mostrar_loja(jogador, estado_do_jogo):
    compras_feitas, ritual_feito = 0, 0
    while True:
        limpar_tela()
        print("\n" + "="*60)
        print(Fore.YELLOW + Style.BRIGHT + "                   ~~~ EMPÓRIO REAL ~~~")
        print("="*60)
        print(f"Suas fichas: {Fore.GREEN}{jogador.fichas}")
        print(Style.DIM + f"Você pode fazer até {2 - compras_feitas} compras e {1 - ritual_feito} rituais nesta visita.")
        print("------------------------------------------------------------")

        print(Fore.CYAN + "\nServiços Disponíveis:")
        nivel_atual = max(jogador.afinidades.values()) if jogador.afinidades else 0
        custo_afinidade = int(150 * (1.5**(nivel_atual)))
        if ritual_feito < 1:
            print(f"  [e] Realizar Ritual de Afinidade - {Fore.YELLOW}{custo_afinidade} fichas")
            print(f"      {Style.DIM}Encante ou aprimore uma afinidade de carta.")
        else:
            print(Style.DIM + "- Você já realizou um ritual nesta visita.")
        
        itens_disponiveis = [(item_id, detalhes) for item_id, detalhes in ITENS_DA_LOJA.items() if item_id not in jogador.itens]
        
        if not itens_disponiveis:
            print("\nVocê já comprou todos os itens disponíveis no Empório!")
        else:
            oferta_do_dia = random.sample(itens_disponiveis, k=min(len(itens_disponiveis), 3))
            
            if oferta_do_dia and random.random() < 0.6:
                item_promo_idx = random.randint(0, len(oferta_do_dia) - 1)
                desconto = random.choice([0.15, 0.25, 0.35, 0.45, 0.50])
                desconto_percentual = int(desconto * 100)
            else:
                item_promo_idx = -1
                desconto_percentual = 0
            
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

        if escolha == 'e' and ritual_feito < 1:
            if jogador.fichas >= custo_afinidade:
                carta_para_encantar = ''
                while carta_para_encantar.upper() not in Mao.VALORES:
                    carta_para_encantar = input("Qual rank de carta você deseja encantar/aprimorar? (2-10, J, Q, K, A): ").upper()
                jogador.fichas -= custo_afinidade
                nivel_anterior = jogador.afinidades.get(carta_para_encantar, 0)
                jogador.afinidades[carta_para_encantar] = nivel_anterior + 1
                ritual_feito += 1
                print(Fore.GREEN + f"\nO pacto com '{carta_para_encantar}' foi fortalecido para o Nível {nivel_anterior + 1}!")
                estado_do_jogo["jogador_atual"]["fichas"] = jogador.fichas
                estado_do_jogo["jogador_atual"]["afinidades"] = jogador.afinidades
                salvar_estado_do_jogo(estado_do_jogo)
                input("Pressione Enter...")
            else:
                print(Fore.RED + "\nFichas insuficientes para o ritual!")
                input("Pressione Enter...")
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
                        input("Pressione Enter para continuar...")
                        if compras_feitas >= 2:
                            print(Fore.YELLOW + "\nVocê atingiu o limite de compras desta visita!")
                            time.sleep(2)
                            break
                    else:
                        print(Fore.RED + "\nFichas insuficientes!")
                        input("Pressione Enter...")
                else:
                    print(Fore.RED + "\nEscolha inválida.")
                    input("Pressione Enter...")
            except ValueError:
                print(Fore.RED + "\nEntrada inválida.")
                input("Pressione Enter...")

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
            input("Pressione Enter para continuar...")
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
            
            input("Pressione Enter para continuar...")
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
                        input("Pressione Enter para continuar...")
                    else:
                        print(Fore.RED + "\nHonra insuficiente para fazer este sacrifício.")
                        input("Pressione Enter...")
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
                            input("Pressione Enter para continuar...")
                        else:
                            print(Fore.RED + "\nFichas insuficientes para pagar o preço do poder.")
                            input("Pressione Enter...")
                    else:
                        print(Fore.RED + "\nSua infâmia ainda não é grande o suficiente para este pacto.")
                        input("Pressione Enter...")
            else:
                print(Fore.RED + "\nEscolha inválida.")
                input("Pressione Enter...")
        except ValueError:
            print(Fore.RED + "\nEntrada inválida.")
            input("Pressione Enter...")

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
                    cooldown_extorquir=dados_jogador_salvo.get("cooldown_extorquir", 0)
                )
                print(f"\nBem-vindo de volta, {jogador.nome}!")
                time.sleep(2)
                return jogador, estado_do_jogo
            else:
                print(Fore.RED + "\nNenhuma jornada em andamento para continuar.")
                time.sleep(2)
        elif escolha == '2':
            herois_caidos = estado_do_jogo.get("herois_caidos", [])
            herois_verdadeiros = estado_do_jogo.get("herois_verdadeiros", [])
            jogador = criar_novo_jogador(herois_caidos, herois_verdadeiros)
            input(f"\nSua jornada como {jogador.nome} começa... Pressione Enter.")
            return jogador, estado_do_jogo
        elif escolha == '3':
            limpar_tela()
            mostrar_placar_de_lendas(estado_do_jogo)
            input("\nPressione Enter para voltar ao menu...")
        elif escolha == '4':
            print("\nObrigado por visitar o reino de Count & Queen!")
            time.sleep(2)
            return None, None
        else:
            print(Fore.RED + "\nOpção inválida, meu nobre.")
            time.sleep(2)

# ===================================================================
# --- CLASSES ---
# ===================================================================

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
        
        if len(self.cartas) == 2 and self.valor == 21:
            self.e_blackjack = True

class Jogador:
    def __init__(self, nome, fichas=200, prestigio=0, genero='h',
                 desistencias_consecutivas=0, itens=None, afinidades=None,
                 caminho="nobreza", cooldown_apelo=0, cooldown_extorquir=0):
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

    def __repr__(self):
        return f"Jogador: {self.nome}"
    
    def limpar_maos(self):
        self.maos = [Mao()]
    
    def pedir_carta(self, baralho, indice_mao=0):
        if 'caleidoscopio_acaso' in self.itens:
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
                return
        
        carta_comprada = baralho.comprar_carta()
        if carta_comprada:
            self.maos[indice_mao].adicionar_carta(carta_comprada)
        else:
            print("O baralho acabou!")

class Dealer(Jogador):
    def __init__(self):
        super().__init__("Dealer", fichas=9999)
    
    def mostrar_primeira_carta(self):
        if self.maos[0].cartas:
            return self.maos[0].cartas[0]
        return None
    
    def jogar(self, baralho):
        while self.maos[0].valor < 17:
            self.pedir_carta(baralho, 0)

# ===================================================================
# --- FUNÇÃO PRINCIPAL DO JOGO ---
# ===================================================================

def jogar_blackjack():
    jogador, estado_do_jogo = menu_principal()
    if jogador is None:
        return

    herois_caidos = estado_do_jogo.get("herois_caidos", [])
    herois_verdadeiros = estado_do_jogo.get("herois_verdadeiros", [])
    contador_rodadas = estado_do_jogo.get("contador_rodadas", 0)
    
    while True:
        desistiu_nesta_rodada = False
        limpar_tela()
        titulo_atual = obter_titulo(jogador.prestigio, jogador.genero)
        
        apareceu_loja_nesta_rodada = False
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

        print("\n[j] Jogar rodada | [m] Ver mochila | [s] Salvar e sair")
        escolha_menu = input("O que deseja fazer? ").lower()
        
        if escolha_menu == 'm':
            mostrar_mochila(jogador)
            continue
        elif escolha_menu == 's':
            print("\nSua jornada foi salva. Até a próxima!")
            break
        elif escolha_menu != 'j':
            continue

        if 'manto_nobreza' in jogador.itens and jogador.caminho == 'nobreza':
            nivel_nobreza = obter_nivel_de_nobreza(jogador.prestigio)
            if nivel_nobreza > 0:
                tributo = nivel_nobreza * 100
                jogador.fichas += tributo
                print(Fore.CYAN + f"\nO Manto da Nobreza concede seu tributo: +{tributo} fichas!")
                time.sleep(2)
        
        baralho = Baralho()
        dealer = Dealer()
        baralho.embaralhar()
        jogador.limpar_maos()
        
        aposta_principal = 0
        while True:
            print(f"\nVocê tem {Fore.GREEN}{jogador.fichas} fichas.")
            aposta_texto = input(f"{jogador.nome}, quanto você quer apostar? ")
            try:
                aposta_principal = int(aposta_texto)
                if 0 < aposta_principal <= jogador.fichas:
                    break 
                else:
                    print(Fore.RED + "Aposta inválida.")
            except ValueError:
                print(Fore.RED + "Entrada inválida.")
        
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
                jogador.fichas += jogador.maos[0].aposta * 2
            if jogador.maos[0].e_blackjack:
                print(Fore.BLUE + "Você também tem um Blackjack! Empate (Push).")
                jogador.fichas += jogador.maos[0].aposta
            else:
                print(f"Sua mão: {jogador.maos[0]}")
                print("Você perdeu a aposta principal.")
            input("\nPressione Enter para continuar...")
            contador_rodadas += 1
            continue
            
        elif comprou_seguro:
            print(Fore.RED + "O Dealer não tem um Blackjack. Você perdeu o valor do seguro.")
            time.sleep(2)
            
        primeiro_split_feito = False
        indice_mao_atual = 0
        
        while indice_mao_atual < len(jogador.maos):
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
                if 'caleidoscopio_acaso' in jogador.itens:
                    prompt = "você quer 'p' (usar o Caleidoscópio) ou 's' (parar)?"
                
                pode_dobrar = len(mao_atual.cartas) == 2 and jogador.fichas >= mao_atual.aposta
                pode_dividir = False
                pode_desistir = len(mao_atual.cartas) == 2 and indice_mao_atual == 0 and len(jogador.maos) == 1
                
                if len(mao_atual.cartas) == 2 and jogador.fichas >= mao_atual.aposta:
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
                    jogador.fichas -= mao_atual.aposta
                    nova_mao = Mao()
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
        
        for i, mao in enumerate(jogador.maos):
            prefixo_mao = f"Mão {i + 1}: " if len(jogador.maos) > 1 else ""
            print(f"\n{Style.BRIGHT}{prefixo_mao}{mao}")
    
            if mao.valor == -1:
                print("Você desistiu desta mão.")
                continue

            bonus_afinidade = 1.0
            tem_sete = False
            naipes_unicos = set()
            
            for carta in mao.cartas:
                naipes_unicos.add(carta.naipe)
                if carta.valor == '7':
                    tem_sete = True
                if carta.valor in jogador.afinidades:
                    nivel = jogador.afinidades[carta.valor]
                    bonus_afinidade = max(bonus_afinidade, 1 + (0.5 * nivel))

            if mao.valor > 21:
                print(Fore.RED + "Você estourou!")
                perda = abs(calcular_prestigio_perdido(jogador, mao, 10))
                
                if jogador.caminho == 'tirania':
                    jogador.prestigio -= perda
                    print(f"Sua incompetência aumenta sua infâmia. -{perda} de Prestígio.")
                else:
                    jogador.prestigio -= perda
                    print(f"Sua ousadia custou sua honra. -{perda} de Prestígio.")
                
                if 'espelho_tirano' in jogador.itens:
                    ganho_sombrio = perda * 2
                    print(Fore.MAGENTA + f"O Espelho do Tirano reflete sua desonra! Você ganha {ganho_sombrio} fichas.")
                    jogador.fichas += ganho_sombrio
                    
            elif dealer_valor > 21:
                print(Fore.GREEN + "O Dealer estourou! Você venceu!")
                
                lucro_base = mao.aposta
                
                if bonus_afinidade > 1.0:
                    print(Fore.MAGENTA + f"Afinidade ativada! Bônus de {int((bonus_afinidade - 1) * 100)}%!")
                    lucro_base = int(lucro_base * bonus_afinidade)
                
                if 'forca_sete' in jogador.itens and tem_sete:
                    print(Fore.YELLOW + "A Força do Sete se manifesta! Ganhos x7!")
                    lucro_base *= 7
                
                if 'bencao_reinos_v2' in jogador.itens:
                    multiplicador_naipes = len(naipes_unicos) * 2
                    print(Fore.CYAN + f"Bênção dos {len(naipes_unicos)} Reinos! Ganhos x{multiplicador_naipes}!")
                    lucro_base *= multiplicador_naipes
                
                jogador.fichas += mao.aposta + lucro_base
                
                ganho_de_honra = calcular_prestigio_ganho(jogador, mao, 25)
                jogador.prestigio += ganho_de_honra
                
                if jogador.caminho == 'tirania':
                    print(f"Sua vitória aumenta sua infâmia! {ganho_de_honra} de Prestígio.")
                else:
                    print(f"Sua lenda ecoa pelo reino! +{ganho_de_honra} de Prestígio.")
                
            elif mao.valor > dealer_valor:
                prestigio_base = 75 if mao.e_blackjack else 25
                mensagem_vitoria = "BLACKJACK!" if mao.e_blackjack else "Parabéns, você venceu!"
                print(Fore.GREEN + mensagem_vitoria)
                
                lucro_base = mao.aposta * 1.5 if mao.e_blackjack else mao.aposta
                
                if bonus_afinidade > 1.0:
                    print(Fore.MAGENTA + f"Afinidade ativada! Bônus de {int((bonus_afinidade - 1) * 100)}%!")
                    lucro_base = int(lucro_base * bonus_afinidade)
                
                if 'forca_sete' in jogador.itens and tem_sete:
                    print(Fore.YELLOW + "A Força do Sete se manifesta! Ganhos x7!")
                    lucro_base *= 7
                
                if 'bencao_reinos_v2' in jogador.itens:
                    multiplicador_naipes = len(naipes_unicos) * 2
                    print(Fore.CYAN + f"Bênção dos {len(naipes_unicos)} Reinos! Ganhos x{multiplicador_naipes}!")
                    lucro_base *= multiplicador_naipes
                
                jogador.fichas += mao.aposta + int(lucro_base)
                
                ganho_de_honra = calcular_prestigio_ganho(jogador, mao, prestigio_base)
                jogador.prestigio += ganho_de_honra
                
                if jogador.caminho == 'tirania':
                    print(f"Sua vitória aumenta sua infâmia! {ganho_de_honra} de Prestígio.")
                else:
                    print(f"Sua lenda ecoa pelo reino! +{ganho_de_honra} de Prestígio.")
                
            elif mao.valor < dealer_valor:
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
        
        contador_rodadas += 1
        estado_do_jogo["contador_rodadas"] = contador_rodadas
        
        estado_do_jogo["jogador_atual"] = {
            "nome": jogador.nome,
            "fichas": jogador.fichas,
            "prestigio": jogador.prestigio,
            "genero": jogador.genero,
            "desistencias_consecutivas": jogador.desistencias_consecutivas,
            "itens": jogador.itens,
            "afinidades": jogador.afinidades,
            "caminho": jogador.caminho,
            "cooldown_apelo": jogador.cooldown_apelo,
            "cooldown_extorquir": jogador.cooldown_extorquir
        }
        salvar_estado_do_jogo(estado_do_jogo)

        input("\nPressione Enter para continuar...")

        # Eventos pós-rodada - verificar game over
        if jogador.fichas <= 0:
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
            input("\nPressione Enter para retornar ao menu...")
            jogar_blackjack()
            return
        
        # Verificar vitória pelo caminho da nobreza
        if jogador.prestigio >= 100000:
            limpar_tela()
            print("\n" + "="*60)
            print(Fore.YELLOW + Style.BRIGHT + "              ⭐ VITÓRIA GLORIOSA! ⭐")
            print("="*60)
            titulo_final = obter_titulo(jogador.prestigio, jogador.genero)
            print(f"\n{jogador.nome}, você alcançou o título máximo de {titulo_final}!")
            print("Sua lenda será contada por gerações!")
            
            if jogador.nome not in herois_verdadeiros:
                herois_verdadeiros.append(jogador.nome)
                estado_do_jogo["herois_verdadeiros"] = herois_verdadeiros
            
            estado_do_jogo["jogador_atual"] = None
            salvar_estado_do_jogo(estado_do_jogo)
            
            print(f"\nFichas finais: {Fore.GREEN}{jogador.fichas}")
            print(f"Rodadas jogadas: {contador_rodadas}")
            input("\nPressione Enter para retornar ao menu...")
            jogar_blackjack()
            return
        
        # Verificar vitória pelo caminho da tirania
        if jogador.prestigio <= -100000:
            limpar_tela()
            print("\n" + "="*60)
            print(Fore.RED + Style.BRIGHT + "              💀 VITÓRIA SOMBRIA! 💀")
            print("="*60)
            titulo_final = obter_titulo(jogador.prestigio, jogador.genero)
            print(f"\n{jogador.nome}, você ascendeu ao título temível de {titulo_final}!")
            print("Seu nome será sussurrado com terror por gerações!")
            
            if jogador.nome not in herois_verdadeiros:
                herois_verdadeiros.append(jogador.nome)
                estado_do_jogo["herois_verdadeiros"] = herois_verdadeiros
            
            estado_do_jogo["jogador_atual"] = None
            salvar_estado_do_jogo(estado_do_jogo)
            
            print(f"\nFichas finais: {Fore.GREEN}{jogador.fichas}")
            print(f"Infâmia final: {Fore.RED}{jogador.prestigio}")
            print(f"Rodadas jogadas: {contador_rodadas}")
            input("\nPressione Enter para retornar ao menu...")
            jogar_blackjack()
            return
        
        # Sistema de lojas - aparecem aleatoriamente
        if not apareceu_loja_nesta_rodada and contador_rodadas > 0:
            # Empório Real (20% de chance a cada 3 rodadas)
            if contador_rodadas % 3 == 0 and random.random() < 0.20:
                limpar_tela()
                print(Fore.YELLOW + "\n✨ Um mercador real se aproxima! ✨")
                print("O Empório Real está aberto para negócios!")
                input("Pressione Enter para entrar...")
                mostrar_loja(jogador, estado_do_jogo)
                apareceu_loja_nesta_rodada = True
            
            # Sacrário do Segredo (15% de chance a cada 5 rodadas)
            elif contador_rodadas % 5 == 0 and random.random() < 0.15:
                limpar_tela()
                print(Fore.RED + "\n🕯️ Uma presença sombria te observa... 🕯️")
                print("O Sacrário do Segredo sussurra seu nome...")
                input("Pressione Enter para entrar...")
                mostrar_sacrario_do_segredo(jogador, estado_do_jogo)
                apareceu_loja_nesta_rodada = True
        
        # Evento aleatório: Encontro com Andarilho Misterioso (5% de chance)
        if random.random() < 0.05 and contador_rodadas > 5:
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
            
            input("\nPressione Enter para continuar...")
        
        # Evento aleatório: Desafio de Alto Risco (3% de chance, requer prestígio alto)
        if random.random() < 0.03 and jogador.prestigio >= 5000 and contador_rodadas > 10:
            limpar_tela()
            print(Fore.RED + Style.BRIGHT + "\n⚔️ DESAFIO DE ALTO RISCO ⚔️")
            print("\nUm nobre arrogante te desafia para uma partida de apostas altas!")
            aposta_desafio = min(jogador.fichas, random.randint(500, 2000))
            print(f"Aposta obrigatória: {Fore.YELLOW}{aposta_desafio} fichas")
            print("Se vencer: Dobra a aposta + 500 de prestígio")
            print("Se perder: Perde a aposta + 200 de prestígio")
            
            aceitar_desafio = input("\nAceita o desafio? (s/n): ").lower()
            
            if aceitar_desafio == 's':
                jogador.fichas -= aposta_desafio
                chance_vitoria = 0.55 if jogador.prestigio >= 15000 else 0.50
                
                print("\n🎴 As cartas são distribuídas...")
                time.sleep(2)
                
                if random.random() < chance_vitoria:
                    print(Fore.GREEN + Style.BRIGHT + "\n🏆 VITÓRIA!")
                    jogador.fichas += aposta_desafio * 2
                    jogador.prestigio += 500
                    print(f"Você ganhou {aposta_desafio * 2} fichas e 500 de prestígio!")
                    print('O nobre se retira humilhado...')
                else:
                    print(Fore.RED + Style.BRIGHT + "\n💔 DERROTA!")
                    jogador.prestigio -= 200
                    print(f"Você perdeu {aposta_desafio} fichas e 200 de prestígio.")
                    print('O nobre ri com desdém...')
                
                estado_do_jogo["jogador_atual"]["fichas"] = jogador.fichas
                estado_do_jogo["jogador_atual"]["prestigio"] = jogador.prestigio
                salvar_estado_do_jogo(estado_do_jogo)
                input("\nPressione Enter para continuar...")
            else:
                print('\nVocê recusa o desafio. "Covarde!" grita o nobre.')
                jogador.prestigio -= 50
                print(Fore.RED + "Sua recusa te custa 50 de prestígio.")
                estado_do_jogo["jogador_atual"]["prestigio"] = jogador.prestigio
                salvar_estado_do_jogo(estado_do_jogo)
                input("\nPressione Enter para continuar...")

# ===================================================================
# --- EXECUÇÃO DO JOGO ---
# ===================================================================

if __name__ == "__main__":
    jogar_blackjack()