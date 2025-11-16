# 🎴 Count & Queen - Blackjack RPG

Um jogo de Blackjack com elementos de RPG, sistema de prestígio, lojas mágicas e escolha entre dois caminhos: Nobreza ou Tirania.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📖 Sobre o Jogo

Count & Queen é um Blackjack com twist de RPG onde cada vitória ou derrota afeta seu prestígio no reino. Escolha entre seguir o caminho da nobreza e se tornar Rei/Rainha, ou abraçar a tirania e dominar através do medo.

## ✨ Características

- ⚔️ **Sistema de Prestígio**: Ganhe ou perca prestígio baseado em suas jogadas
- 👑 **Títulos de Nobreza**: Desde Plebeu até Rei/Rainha (ou Tirano)
- 🛒 **Empório Real**: Compre itens mágicos que alteram o gameplay
- 🌑 **Sacrário do Segredo**: Caminho sombrio com poderes proibidos
- 💎 **Afinidades com Cartas**: Forme pactos com cartas específicas para bônus
- 🎲 **Eventos Aleatórios**: Encontros e desafios inesperados
- 💾 **Save Automático**: Seu progresso é salvo automaticamente
- 🏆 **Salão das Lendas**: Seus heróis são eternizados

## 🎮 Como Jogar

### 📋 Requisitos

- **Python 3.7+** instalado
- Biblioteca **colorama**
- Terminal com suporte a cores (PowerShell, CMD, ou terminal do VSCode)

---

### 🚀 Instalação

#### 1. Clone o repositório:

```bash
git clone https://github.com/GustaGol0/count-queen.git
cd count-queen
```

#### 2. Instale as dependências:

```bash
pip install -r requirements.txt
```

**Ou instale manualmente:**

```bash
pip install colorama
```

#### 3. Execute o jogo:

```bash
python count_queen.py
```

**Ou, se `python` não funcionar:**

```bash
py count_queen.py
```

---

### 🃏 Regras Básicas

#### **Blackjack Tradicional**

- O objetivo é chegar o mais próximo possível de **21 pontos** sem estourar
- Cartas numéricas valem seu valor (2-10)
- J, Q, K valem **10 pontos**
- Ás vale **11** (ou 1 se estourar)
- **Blackjack** = 21 pontos com 2 cartas (Ás + figura)

#### **Comandos Durante o Jogo**

- **`p`** (Pedir) - Compra uma nova carta
- **`s`** (Parar) - Mantém a mão atual e passa a vez
- **`d`** (Dobrar) - Dobra a aposta e recebe apenas 1 carta final
- **`sp`** (Split) - Divide um par em duas mãos separadas
- **`des`** (Desistir) - Recupera metade da aposta (penalidade de prestígio)

---

### 👑 Sistema de Prestígio

#### **Caminho da Nobreza** (Padrão)

- ✅ **Ganhe prestígio** ao vencer partidas
- ❌ **Perca prestígio** ao perder ou desistir
- 🎯 **Objetivo:** Alcançar **100.000 de prestígio** para se tornar Rei/Rainha

#### **Caminho da Tirania** (Sombrio)

- ⚠️ Se ativa ao comprar itens no **Sacrário do Segredo**
- 🔄 **Inverte o sistema:** Perde prestígio ao vencer, ganha ao perder
- 🎯 **Objetivo:** Alcançar **-100.000 de prestígio** para se tornar Tirano/Tirana

#### **Títulos de Nobreza:**

```
Prestígio          Título
─────────────────────────────────
100.000+           Rei/Rainha
50.000 - 99.999    Príncipe/Princesa
15.000 - 49.999    Duque/Duquesa
5.000 - 14.999     Conde/Condessa
1.500 - 4.999      Visconde/Viscondessa
500 - 1.499        Barão/Baronesa
100 - 499          Cavaleiro/Dama
0 - 99             Plebeu/Plebeia
```

#### **Títulos da Tirania:**

```
Prestígio          Título
─────────────────────────────────
-100.000 ou menos  Tirano/Tirana
-50.000 a -99.999  Flagelo do Reino
-15.000 a -49.999  Senhor/Senhora da Guerra
-5.000 a -14.999   Usurpador/Usurpadora
-1.500 a -4.999    Mestre/Mestra Vigarista
-500 a -1.499      Ladrão/Ladra de Estrada
-100 a -499        Foragido/Foragida
-1 a -99           Malandro/Malandra
```

---

### 🛒 Sistema de Lojas

#### **Empório Real** (Aparece aleatoriamente)

Itens que melhoram suas chances:

- **Bênção dos Quatro Reinos** (400 fichas) - Multiplica lucro por naipes únicos
- **Força do Sete** (777 fichas) - Ganhos x7 ao vencer com um 7
- **Joias Gêmeas** (900 fichas) - Split grátis em novos pares
- **Manilha da Sorte** (800 fichas) - Compre seguro contra Blackjack do dealer
- **Caleidoscópio do Acaso** (2.500 fichas) - Veja e escolha cartas futuras

**Limitações:**

- Máximo de **2 compras** por visita
- Máximo de **1 ritual de afinidade** por visita

#### **Sacrário do Segredo** (Aparece raramente)

Itens poderosos com consequências:

- **Espelho do Tirano** (750 prestígio) - Converte perda de prestígio em fichas (x2)
- **Manto da Nobreza** (600 prestígio) - Tributo de fichas por rodada
- **Pacto do Tirano** (250 prestígio) - Dobra ganhos e perdas de prestígio

⚠️ **AVISO:** Comprar aqui te força ao **Caminho da Tirania**!

---

### 💎 Sistema de Afinidades

Crie pactos com cartas específicas para bônus permanentes!

**Como funciona:**

1. No **Empório Real**, use o ritual de afinidade
2. Escolha uma carta (2-10, J, Q, K, A)
3. Cada nível aumenta **+50% de ganho** ao vencer com essa carta na mão

**Exemplo:**

- Afinidade com **Ás** Nível 3 = **+150% fichas** ao vencer com um Ás na mão
- Custo aumenta exponencialmente: 150 → 225 → 337 → ...

---

### 🎲 Eventos Aleatórios

#### **Andarilho Misterioso** (5% de chance)

Oferece trocas arriscadas:

- Trocar fichas por prestígio
- Trocar prestígio por fichas
- Apostar fichas em jogo de sorte

#### **Desafio de Alto Risco** (3% de chance)

- Requer prestígio alto (5.000+)
- Aposta obrigatória de 500-2.000 fichas
- Vitória: Dobra aposta + 500 prestígio
- Derrota: Perde aposta + 200 prestígio

---

### 💾 Sistema de Save

- **Salvamento automático** após cada rodada
- Arquivo gerado: `save.json` (na mesma pasta do jogo)
- Continue de onde parou a qualquer momento!

---

### 🏆 Condições de Vitória/Derrota

#### **Vitória:**

- 👑 **Nobreza:** Alcance 100.000 de prestígio
- 💀 **Tirania:** Alcance -100.000 de prestígio

#### **Derrota (Game Over):**

- 💸 Fique sem fichas (0 ou menos)

#### **Salão das Lendas:**

- Heróis que **vencem** vão para a lista de **Heróis Verdadeiros** ⭐
- Heróis que **perdem** vão para a lista de **Heróis Caídos** 💀

---

### 💡 Dicas para Iniciantes

1. **Comece conservador** - Aposte pequeno até pegar o ritmo
2. **Aprenda quando parar** - Se tiver 17+, considere parar
3. **Use o split com sabedoria** - Ideal para pares de 8 e Ases
4. **Evite desistir muito** - Penalidades de prestígio aumentam
5. **Priorize afinidades** - Invista em cartas que você vê com frequência
6. **Escolha seu caminho cedo** - Nobreza ou Tirania afetam toda a estratégia

---

### ❓ Problemas Comuns

**"Python não reconhecido":**

```bash
# Tente usar 'py' ao invés de 'python'
py count_queen.py
```

**"ModuleNotFoundError: No module named 'colorama'":**

```bash
# Instale a biblioteca
pip install colorama
```

**Cores não aparecem no terminal:**

- Use PowerShell, CMD ou terminal do VSCode
- Git Bash pode ter problemas com cores

---

### 🎯 Meta do Jogo

**Desafie-se!**

- Quantas rodadas você consegue sobreviver?
- Consegue alcançar o título máximo?
- Qual caminho é mais difícil: Nobreza ou Tirania?

**Boa sorte, nobre aventureiro!** 🎴👑

## 🎯 Objetivo

**Caminho da Nobreza:** Alcance 100.000 de prestígio para se tornar Rei/Rainha

**Caminho da Tirania:** Alcance -100.000 de prestígio para se tornar o Tirano supremo

Cuidado para não perder todas as suas fichas!

## 🃏 Itens Especiais

### Empório Real

- **Bênção dos Quatro Reinos**: Multiplica ganhos por naipes únicos
- **Força do Sete**: Ganhos x7 ao vencer com um 7
- **Caleidoscópio do Acaso**: Veja e escolha cartas futuras
- E mais...

### Sacrário do Segredo

- **Espelho do Tirano**: Converte perdas de prestígio em fichas
- **Pacto do Tirano**: Dobra ganhos e perdas de prestígio
- **Manto da Nobreza**: Receba tributos periódicos

## 🎲 Mecânicas

- **Sistema de Split**: Divida pares e jogue múltiplas mãos
- **Dobrar Aposta**: Dobre sua aposta para uma carta final
- **Seguro**: Proteja-se contra Blackjack do dealer
- **Desistência**: Recupere metade da aposta (com penalidade de prestígio)

## 📜 Licença

MIT License - sinta-se livre para usar, modificar e distribuir!

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se livre para abrir issues ou pull requests.

## 👤 Autor

Criado com ❤️ para amantes de Blackjack e RPGs

---

**Divirta-se jogando Count & Queen!** 🎴👑
