"""Campanha de mapa. Estado JSON determinístico, independente da interface."""
import copy
import json
import math
import os
import random
import tempfile
import threading
from collections import Counter
from pathlib import Path

from .content import (REGIONS, SUITS, RANKS, RELICS, OATHS, MARKS, BOSSES,
                      BOSS_PAIRS, ELITES, NODE_NAMES, CONTRACTS, CHARGES, ORIGINS, BOSS_PRESENTATION)
from . import stories


def require(condition, message='Esta escolha não está disponível agora.'):
    if not condition:
        raise ValueError(message)


def tuples(value):
    return tuple(tuples(v) for v in value) if isinstance(value, list) else value


def points(rank):
    return 11 if rank == 'A' else 10 if rank in ('J', 'Q', 'K') else int(rank)


class Adventure:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.s = {'versao': 2, 'revisao': 0, 'phase': 'inicio', 'player': None,
                  'uid': 0, 'unlocks': [], 'legends': [], 'history': [], 'notice': '', 'effects': [], 'new_unlocks': []}

    @property
    def p(self):
        return self.s['player']

    @property
    def b(self):
        return self.s['battle']

    def has(self, relic):
        return relic in self.p['itens']

    def oath(self, key, downside=False):
        return key in self.p['juramentos'] and (not downside or self.p['consagrado'] != key)

    def export(self):
        return copy.deepcopy({**self.s, 'random': self.rng.getstate()})

    def restore(self, data):
        require(data.get('versao') == 2, 'Versão de jornada não suportada.')
        self.s = copy.deepcopy({k: v for k, v in data.items() if k != 'random'})
        self.rng.setstate(tuples(data['random']))
        self.s.setdefault('effects', [])
        self.s.setdefault('new_unlocks', [])
        if self.p:
            legacy='origem' not in self.p
            for key, value in dict(origem='viajante', origin_debt=0., stories={}, story_log=[], reserved=None).items():
                self.p.setdefault(key, value)
            if legacy and self.p['stats']['splits']:
                self.unlock('trapaceiro')
            if legacy and (self.s.get('region', 0)>0 or any(x.get('vitoria') or x.get('regiao', 0)>1 for x in self.s['legends'])):
                self.unlock('herdeiro')
            if legacy and self.s['legends']:
                self.unlock('exilada')

    def unlock(self, origin):
        key = 'origem_'+origin
        if key not in self.s['unlocks']:
            self.s['unlocks'].append(key)
            self.s['new_unlocks'].append(origin)

    def effect(self, source, text):
        self.s['effects'].append({'source':source, 'text':text})
        self.s['effects'] = self.s['effects'][-30:]

    def card(self, rank, suit=None, temporary=None):
        self.s['uid'] += 1
        return {'id': str(self.s['uid']), 'valor': rank,
                'naipe': suit or self.rng.choice(SUITS), 'marca': None,
                'temporaria': temporary}

    def deck(self, ranks=None):
        cards = ([self.card(r, n) for n in SUITS for r in RANKS] if ranks is None
                 else [self.card(r, SUITS[i % 4]) for i, r in enumerate(ranks)])
        ids = [c['id'] for c in cards]
        self.rng.shuffle(ids)
        return {'cards': {c['id']: c for c in cards}, 'draw': ids, 'discard': [], 'shuffles': 0}

    def add_card(self, rank, mark=None, temporary=None):
        c = self.card(rank, 'Sem naipe' if temporary else None, temporary)
        c['marca'] = mark
        self.p['deck']['cards'][c['id']] = c
        self.p['deck']['discard'].append(c['id'])
        return c

    def remove_card(self, deck, cid):
        deck['cards'].pop(cid, None)
        for pile in ('draw', 'discard'):
            if cid in deck[pile]:
                deck[pile].remove(cid)

    def replenish(self, deck, minimum=1):
        if len(deck['draw']) < minimum and deck['discard']:
            deck['draw'].extend(deck['discard'])
            deck['discard'] = []
            self.rng.shuffle(deck['draw'])
            deck['shuffles'] += 1

    def draw(self, deck):
        self.replenish(deck)
        require(deck['draw'], 'O baralho não tem cartas disponíveis.')
        cid = deck['draw'].pop()
        return copy.deepcopy(deck['cards'][cid])

    def new(self, name, gender, origin='viajante'):
        require(self.s['phase'] in ('inicio', 'fim'), 'Termine a jornada atual antes de começar outra.')
        require(isinstance(name, str) and 1 <= len(name.strip()) <= 30, 'Use um nome de 1 a 30 caracteres.')
        require(gender in ('h', 'm'), 'Escolha os títulos do personagem.')
        require(origin in ORIGINS and (origin=='viajante' or 'origem_'+origin in self.s['unlocks']), 'Origem ainda não desbloqueada.')
        self.s.update(phase='juramento', region=0, layer=-1, column=1, visited=[], history=[],
                      battle=None, round_count=0, notice='', result=None, choice=None,
                      boss_ids=[self.rng.choice(pair) for pair in BOSS_PAIRS], pending=None)
        self.s['player'] = {'nome': name.strip(), 'genero': gender, 'fichas': 200.,
                            'prestigio': 0, 'caminho': 'nobreza', 'itens': [], 'juramentos': [],
                            'consagrado': None, 'afinidades': {}, 'ultima_aposta': 10,
                            'debt': 0., 'loan': 0., 'paid_debt': False, 'revived': False,
                            'stats': {'doubles': 0, 'splits': 0, 'long': 0, 'wins': {}},
                            'deck': self.deck(), 'prepared': False, 'origem':origin,
                            'origin_debt':0., 'stories':{}, 'story_log':[], 'reserved':None}
        if origin=='herdeiro':
            self.p.update(fichas=140., origin_debt=120., itens=['balanca_carrasco'])
        elif origin=='exilada':
            self.p.update(fichas=140., prepared=True, itens=['broche_prudencia'])
            for card in self.p['deck']['cards'].values():
                if card['valor']=='K': card['valor']='2'
        elif origin=='trapaceiro':
            self.p.update(fichas=160., caminho='tirania', itens=['bolso_falso'])
        if 'carta_real' in self.s['unlocks']:
            next(iter(self.p['deck']['cards'].values()))['marca'] = 'real'
        self.s['maps'] = [self.make_map(i) for i in range(4)]
        self.start_region()

    def make_map(self, region):
        layout = [['mesa','evento','mesa'], ['loja','elite','oficina'],
                  ['refugio','evento','sacrario'], ['elite','mesa','oficina'],
                  ['loja','refugio','elite']]
        if region == 3:
            layout = [['oficina','refugio','loja'], ['elite','evento','sacrario'], ['refugio','oficina','loja']]
        result = []
        for row, kinds in enumerate(layout):
            kinds = kinds[:]
            self.rng.shuffle(kinds)
            for column, kind in enumerate(kinds):
                elite = self.rng.choice(list(ELITES)) if kind == 'elite' else None
                result.append({'id': f'{region}-{row}-{column}', 'row': row, 'col': column, 'type': kind, 'elite': elite})
        result.append({'id': f'{region}-{len(layout)}-1', 'row': len(layout), 'col': 1, 'type': 'boss', 'elite': None})
        return result

    def start_region(self):
        self.s.update(phase='juramento', layer=-1, column=1, battle=None, pending=None,
                      compass=False, throne=False, retry=False, choice=None)
        if self.p['loan']:
            paid = min(self.p['fichas'], self.p['loan'])
            self.p['fichas'] -= paid
            self.p['loan'] -= paid
            self.s['notice'] = f'Cobrança do empréstimo: {paid:g} fichas. Saldo devedor: {self.p["loan"]:g}.'
            if self.bankrupt() and self.s['phase'] == 'fim':
                return
            self.s['phase'] = 'juramento'
        options = [k for k in OATHS if k not in self.p['juramentos']]
        incompatible = {'fortuna':'gloria','gloria':'fortuna','lamina':'quinta','quinta':'lamina'}
        options = [k for k in options if incompatible.get(k) not in self.p['juramentos']]
        self.s['offers'] = self.rng.sample(options, 3)
        if self.s['region'] == 3:
            stats = self.p['stats']
            scores = [(stats['doubles'], 'dobras'), (stats['splits'], 'divisoes'), (stats['long'], 'longas')]
            best = max(scores)[1] if max(v for v, _ in scores) >= 3 else 'equilibrio'
            self.s['king_style'] = best
            self.s['king_face'] = max(stats['wins'], key=stats['wins'].get) if stats['wins'] else 'A'

    def prestige(self, amount):
        if amount > 0:
            amount *= (1.4 if self.oath('gloria') else 1)
            amount *= (.75 if self.oath('fortuna', True) else 1)
            amount *= (1.25 if self.oath('honra') else 1)
        if self.has('pacto_tirano'):
            amount *= 2
        amount = int(round(amount))
        old = self.p['prestigio']
        self.p['prestigio'] = max(0, min(100, old + amount))
        if amount < 0 and self.has('espelho_tirano'):
            self.p['fichas'] += abs(self.p['prestigio'] - old) * 2

    def connected(self, node):
        return self.s['layer'] < 0 or node['type'] == 'boss' or abs(node['col'] - self.s['column']) <= 1

    def possible_node(self, node):
        return node['row'] == self.s['layer'] + 1 and (self.connected(node) or
               (self.has('bussola_contrabandista') and not self.s['compass']))

    def interact(self, action, data):
        self.s.update(effects=[], new_unlocks=[])
        phase = self.s['phase']
        value = data.get('valor')
        if action == 'nova':
            return self.new(data.get('nome'), data.get('genero', 'h'), data.get('origem','viajante'))
        require(self.p is not None, 'Comece uma jornada.')
        if phase == 'juramento':
            require(action == 'juramento' and value in self.s['offers'])
            self.p['juramentos'].append(value)
            if value == 'divida':
                self.p['fichas'] += 150
                self.p['debt'] = 225.
            self.s['phase'] = 'mapa'
        elif phase == 'mapa':
            require(action == 'no')
            node = next((n for n in self.s['maps'][self.s['region']] if n['id'] == value), None)
            require(node and self.possible_node(node), 'Escolha um encontro conectado na próxima camada.')
            self.s.update(pending=node, phase='encontro')
        elif phase == 'encontro':
            require(action in ('entrar','voltar'))
            if action == 'voltar':
                self.s.update(phase='mapa', pending=None)
                return
            node = self.s['pending']
            if not self.connected(node):
                self.s['compass'] = True
            self.s.update(layer=node['row'], column=node['col'])
            self.s['visited'].append(node['id'])
            self.enter(node)
        elif phase == 'loja':
            self.shop_action(action, data)
        elif phase == 'oficina':
            self.workshop_action(action, data)
        elif phase in ('evento','refugio','sacrario'):
            self.story_action(action, value)
        elif phase == 'recompensa':
            require(action == 'reliquia' and value in self.s['offers'])
            self.p['itens'].append(value)
            self.after_reward()
        elif phase == 'conclusao':
            require(action in ('seguir','revanche'))
            result = self.s['result']
            if action == 'revanche':
                require(result['retry'] and self.p['fichas'] >= result['cost'])
                self.p['fichas'] -= result['cost']
                self.s['retry'] = True
                self.start_battle('boss', self.s['boss_ids'][self.s['region']])
            elif result['boss'] and not result['won']:
                self.finish(False, 'O boss defendeu a passagem. Sua jornada termina aqui.')
            elif result['won'] and result['boss'] and self.s['region'] < 3:
                self.s['region'] += 1
                self.start_region()
            else:
                self.s['phase'] = 'mapa'
        elif phase == 'fim':
            raise ValueError('A jornada terminou. Comece uma nova lenda.')
        else:
            self.battle_action(action, data)
        self.p['fichas'] = round(self.p['fichas'], 2)
        if self.s['phase'] in ('mapa', 'encontro', 'juramento', 'loja', 'oficina',
                               'evento', 'refugio', 'sacrario', 'aposta', 'contrato', 'pedagio'):
            self.bankrupt(in_battle=self.s['phase'] in ('aposta', 'contrato', 'pedagio'))

    def enter(self, node):
        self.s['notice'] = ''
        kind = node['type']
        if kind in ('mesa','elite','boss'):
            identity = self.s['boss_ids'][self.s['region']] if kind == 'boss' else node['elite'] if kind == 'elite' else 'mesa'
            self.start_battle(kind, identity)
        elif kind == 'loja':
            self.s['phase'] = 'loja'
            pool = [k for k,v in RELICS.items() if v['raridade'] != 'mitico' and k not in self.p['itens']]
            options = self.rng.sample(pool, min(len(pool), 4 if self.has('selo_mercador') else 3))
            self.s['shop'] = {'offers': options, 'bought': [], 'services': 0, 'loan_used': False}
        elif kind == 'oficina':
            self.s['phase'] = 'oficina'
            self.s['workshop_paid'] = False
        else:
            self.s['phase'] = kind
            if kind == 'evento':
                story = stories.select_story(self)
                self.s['event'] = 'historia:'+story if story else self.rng.choice(['ponte','biblioteca','audiencia'])
                if self.has('moeda_peregrino'):
                    self.p['fichas'] += 5

    def shop_price(self, key):
        price = RELICS[key]['preco'] * (1 + .15 * self.s['region'])
        if self.p['origem']=='trapaceiro': price *= 1.15
        if self.oath('estrada', True):
            price *= 1.2
        if self.has('selo_mercador') and not self.s['shop']['bought']:
            price *= .85
        if self.p['paid_debt']:
            price *= .9
        if self.p['prestigio'] >= 40:
            price *= .9
        return int(round(price))

    def shop_action(self, action, data):
        shop = self.s['shop']
        if action == 'sair':
            self.s['phase'] = 'mapa'
            return
        if action == 'comprar':
            key = data.get('valor')
            require(key in shop['offers'] and key not in self.p['itens'] and len(shop['bought']) < 2)
            price = self.shop_price(key)
            credit = data.get('credito', False)
            if credit:
                require(self.has('ampulheta_usurario') and not self.p['loan'] and not shop['loan_used'] and self.s['region'] < 3,
                        'Crédito indisponível: quite a dívida ou compre à vista. Não há empréstimos na região final.')
                cost = round(price / 2, 2)
            else:
                cost = price
            require(self.p['fichas'] >= cost, 'Fichas insuficientes.')
            self.p['fichas'] -= cost
            if credit:
                self.p['loan'] = round(price / 2 * 1.25, 2)
                shop['loan_used'] = True
            self.p['itens'].append(key)
            shop['bought'].append(key)
        elif action == 'servico':
            require(shop['services'] < 1 and self.p['fichas'] >= 35, 'O serviço custa 35 fichas e só pode ser usado uma vez por visita.')
            self.p['fichas'] -= 35
            shop['services'] += 1
            self.s.update(phase='oficina', workshop_paid=True)
        elif action == 'afinidade':
            rank = data.get('valor')
            require(rank in RANKS and shop['services'] < 1)
            level = self.p['afinidades'].get(rank, 0)
            cost = 40 * (level + 1)
            require(level < 5 and self.p['fichas'] >= cost, f'Ritual custa {cost} fichas; máximo nível 5.')
            self.p['fichas'] -= cost
            self.p['afinidades'][rank] = level + 1
            shop['services'] += 1
        else:
            raise ValueError('Serviço desconhecido.')

    def workshop_action(self, action, data):
        if action == 'sair':
            self.s['phase'] = 'loja' if self.s['workshop_paid'] else 'mapa'
            return
        require(action in ('remover','transformar','marcar','adicionar'))
        deck = self.p['deck']
        if action == 'adicionar':
            require(data.get('valor') in RANKS and len(deck['cards']) < 80, 'Máximo de 80 cartas.')
            self.add_card(data['valor'])
        else:
            cid = data.get('carta')
            require(cid != self.p['reserved'], 'A carta guardada deve ser jogada antes de ser alterada.')
            require(isinstance(cid, str) and cid in deck['cards'] and not deck['cards'][cid]['temporaria'],
                    'Escolha uma carta permanente do seu baralho.')
            if action == 'remover':
                require(sum(not c['temporaria'] for c in deck['cards'].values()) > 16,
                        'Mantenha ao menos 16 cartas permanentes no baralho.')
                self.remove_card(deck, cid)
            elif action == 'transformar':
                require(data.get('valor') in RANKS)
                deck['cards'][cid]['valor'] = data['valor']
            else:
                require(data.get('valor') in MARKS and deck['cards'][cid]['marca'] is None, 'Cada carta aceita apenas uma marca.')
                deck['cards'][cid]['marca'] = data['valor']
        self.s['notice'] = 'Seu baralho foi modificado. A mudança permanece nesta jornada.'
        self.s['phase'] = 'loja' if self.s['workshop_paid'] else 'mapa'

    def story_options(self):
        phase = self.s['phase']
        if phase=='evento' and self.s['event'].startswith('historia:'):
            return [(o['id'],o['nome'],o['descricao']) for o in stories.scene(self)['options']]
        if phase == 'refugio':
            return [('reserva','Reserva da estrada','Receba 35 fichas.'),
                    ('purificar','Lavar a maldição','Remove todas as marcas malditas do seu baralho.'),
                    ('preparar','Estudar o adversário','Uma bênção de previsão no próximo encontro.')]
        if phase == 'sacrario':
            return [('pacto','Assinar com seu nome','Pague 30 fichas: escolha a Tirania e ganhe 5 de prestígio.'),
                    ('caridade','Acender uma vela pelo reino','Pague 20 fichas: escolha a Nobreza e ganhe 4 de prestígio.'),
                    ('profanar','Tomar a oferenda','Receba 45 fichas, perca 3 de prestígio e receba um 7 Maldito. Escolhe Tirania.'),
                    ('recusar','Deixar o silêncio intacto','Siga sem alterações.')]
        event = self.s['event']
        options = {
            'ponte': [('pagar','Pagar a travessia','Perca 15 fichas e ganhe 3 de prestígio.'),('risco','Aceitar o jogo do guarda','50% de ganhar 45 fichas; 50% de perder 20.')],
            'biblioteca': [('estudar','Estudar um tomo','Pague 20 fichas e marque uma carta aleatória como Real.'),('vender','Vender o tomo','Receba 25 fichas e perca 2 de prestígio.')],
            'audiencia': [('favor','Pedir um favor','Troque 5 de prestígio por 60 fichas.'),('discurso','Defender sua causa','Receba 4 de prestígio.')],
        }[event]
        if self.oath('estrada'):
            options += [('estrada','Conhecer a passagem esquecida','Receba 20 fichas e escolha uma alteração gratuita no baralho.')]
        elif self.p['prestigio'] >= 20:
            options += [('influencia','Invocar seu título','Receba 15 fichas e 1 de prestígio.')]
        return options + [('recusar','Seguir viagem','Siga sem alterações.')]

    def story_action(self, action, value):
        require(action == 'escolha' and value in [o[0] for o in self.story_options()])
        if self.s['phase']=='evento' and self.s['event'].startswith('historia:'):
            stories.resolve(self, value)
            self.bankrupt()
            return
        if value in ('pacto','caridade','pagar','estudar'):
            cost = {'pacto':30,'caridade':20,'pagar':15,'estudar':20}[value]
            require(self.p['fichas'] >= cost, f'Você precisa de {cost} fichas.')
            self.p['fichas'] -= cost
        if value in ('pacto','profanar'):
            self.p['caminho'] = 'tirania'
        if value == 'caridade':
            self.p['caminho'] = 'nobreza'
        if value in ('pacto','caridade','pagar','discurso','influencia'):
            self.prestige({'pacto':5,'caridade':4,'pagar':3,'discurso':4,'influencia':1}[value])
        if value in ('reserva','profanar','vender','estrada','influencia'):
            self.p['fichas'] += {'reserva':35,'profanar':45,'vender':25,'estrada':20,'influencia':15}[value]
        if value == 'profanar':
            self.prestige(-3)
            self.add_card('7', 'maldita')
        if value == 'vender':
            self.prestige(-2)
        if value == 'purificar':
            for card in self.p['deck']['cards'].values():
                if card['marca'] == 'maldita':
                    card['marca'] = None
        if value == 'preparar':
            self.p['prepared'] = True
        if value == 'risco':
            change = 45 if self.rng.random() < .5 else -min(20, self.p['fichas'])
            self.p['fichas'] += change
            self.s['notice'] = f'O guarda encerra o jogo: {change:+g} fichas.'
        if value == 'estudar':
            options = [c for c in self.p['deck']['cards'].values() if not c['marca']]
            if options:
                self.rng.choice(options)['marca'] = 'real'
            else:
                self.p['fichas'] += 20
                self.s['notice'] = 'Todas as cartas já têm marcas; suas fichas foram devolvidas.'
        if value == 'favor':
            require(self.p['prestigio'] >= 5, 'Você precisa de 5 de prestígio.')
            self.p['prestigio'] -= 5  # Gasto voluntário, não penalidade do Espelho.
            self.p['fichas'] += 60
        if self.bankrupt():
            return
        self.s['phase'] = 'oficina' if value == 'estrada' else 'mapa'
        self.s['workshop_paid'] = False

    def rival_decks(self, identity):
        if identity in ('ferrugem','falsificador'):
            ranks = [str(n) for n in range(2,10)]*2 + ['J','Q','K']*4
        elif identity in ('sinos','novica'):
            ranks = [str(n) for n in range(2,8)]*4 + ['A']*4
        elif identity == 'gemeas':
            return {'a': self.deck([str(n) for n in range(2,7)]*4+['A']*4),
                    'b': self.deck(['8','9','10','J','Q','K']*4+['2','3','4','5'])}
        elif identity in ('cobrador','escrivao'):
            ranks = [str(n) for n in range(4,11)]*3+['A']*6+['J','Q','K']
        elif identity == 'cinzas':
            ranks = RANKS*2
        elif identity in ('astronomo','aprendiz'):
            ranks = [str(n) for n in range(3,9)]*4+['A','J','Q','K']
        elif identity == 'rei':
            style = self.s['king_style']
            ranks = {'dobras':[str(n) for n in range(2,9)]*4+['A']*2,
                     'divisoes':['A','10','J','Q','K']*5+['2','3','4','5']*2,
                     'longas':['6','7','8','9','10','J','Q','K']*4,
                     'equilibrio':RANKS*4+[self.s['king_face']]*2}[style]
        else:
            return {'a': self.deck()}
        return {'a': self.deck(ranks)}

    def start_battle(self, kind, identity):
        self.s['battle'] = {'kind':kind, 'identity':identity, 'decks':self.rival_decks(identity),
            'active':'a', 'wins':0, 'losses':0, 'draws':0, 'rounds':0, 'act':1,
            'target':2 if kind in ('mesa','elite') or identity == 'rei' else 4 if self.s['region']==2 else 3,
            'max_losses':4 if identity=='rei' else 2 if kind=='elite' else 3,
            'blessings':int(identity=='novica')+int(self.p['prepared']), 'bells':0,
            'used':[], 'sisters_saved':[], 'contract':None, 'charge':None, 'ending':None,
            'hands':[], 'dealer':[], 'double_win':False, 'perfect':True, 'result':None,
            'preview':None, 'eclipse_pending':False, 'eclipse_used':False, 'current':0,
            'reveal':False, 'limit':21, 'dealer_stop':17, 'tax':0}
        self.p['prepared'] = False
        self.prepare_round()

    def prepare_round(self):
        b = self.b
        b.update(hands=[], dealer=[], reveal=False, contract=None, current=0,
                 round_used=[], choices=[], pending_action=None, crown_value=0, swapped=False,
                 peeked=False, surrender=False, tax=0, face_exposed=False, result=None)
        if b['identity'] == 'gemeas':
            b['active'] = 'a' if b['rounds'] % 2 == 0 else 'b'
        self.replenish(self.p['deck'], 16)
        self.replenish(b['decks'][b['active']], 10)
        self.rules()
        if b['identity'] == 'cobrador':
            self.s['offers'] = self.rng.sample(list(CONTRACTS), 2)
            self.s['phase'] = 'contrato'
        elif b['identity'] == 'rei' and b['act']==2 and b['charge']=='estrada':
            self.s['phase'] = 'pedagio'
        else:
            self.s['phase'] = 'aposta'

    def rules(self):
        b = self.b
        identity = b['identity']
        b['limit'] = [19,21,23,21][b['rounds'] % 4] if identity=='astronomo' else 19 if identity=='aprendiz' and b['rounds']==0 else 22 if b['ending']=='usurpar' else 21
        b['dealer_stop'] = {'ferrugem':17,'falsificador':16,'sinos':18,'novica':17,'cobrador':17,
                            'escrivao':17,'cinzas':18,'rei':18}.get(identity,17)
        if identity=='gemeas':
            b['dealer_stop'] = 19 if b['active']=='a' else 16
        if identity in ('astronomo','aprendiz'):
            b['dealer_stop'] = b['limit']-3
        if b['contract']=='firme':
            b['dealer_stop']=18
        if b['charge'] in ('quinta','cacador') or b.get('face_exposed') or b['ending']=='governar':
            b['dealer_stop']=19

    def total(self, hand):
        cards = hand['cards'] if isinstance(hand,dict) else hand
        value = sum(c.get('pontos',points(c['valor'])) for c in cards)
        aces = sum(c['valor']=='A' and 'pontos' not in c for c in cards)
        while value > self.b['limit'] and aces:
            value -= 10
            aces -= 1
        return value - (hand.get('adjust',0) if isinstance(hand,dict) else 0)

    def natural(self, hand):
        cards=hand['cards'] if isinstance(hand,dict) else hand
        return (self.b['limit']==21 and len(cards)==2 and self.total(hand)==21
                and not (hand.get('split') or hand.get('no_natural')) if isinstance(hand,dict)
                else self.b['limit']==21 and len(cards)==2 and self.total(cards)==21 and not self.b['swapped'])

    def double_cost(self, hand):
        cost=hand['bet']
        if self.b['identity']=='ferrugem' and self.b['rounds']==0 and 'double' not in self.b['round_used']:
            cost *= .5
        if self.b['charge']=='dobrar' and 'double' not in self.b['round_used']:
            cost *= 1.25
        return round(cost,2)

    def available(self):
        phase=self.s['phase']
        if phase=='aposta':
            return ['apostar']
        if phase=='seguro':
            return ['segurar','recusar_seguro']
        if phase=='oraculo':
            return ['escolher']
        if phase=='revelacao':
            return ['liquidar','cetro']
        if phase=='ultima_palavra':
            return ['comprar_final','aceitar_resultado']
        if phase=='resultado':
            return ['continuar']
        if phase!='jogando':
            return []
        b=self.b
        h=b['hands'][b['current']]
        a=['parar']
        if (self.has('bolso_falso') and 'pocket' not in b['used'] and not self.p['reserved']
                and h['hits']>0 and len(h['cards'])>2 and not h['double'] and not b['peeked']
                and not h['cards'][-1]['temporaria'] and h['cards'][-1]['id'] in self.p['deck']['cards']):
            a.append('guardar')
        if (self.has('balanca_carrasco') and 'balance' not in b['used'] and h.get('split')
                and h['hits']==0 and len(h['cards'])>=2 and not b['peeked'] and not h['double']
                and b['current']+1<len(b['hands'])):
            a.append('transferir')
        can_hit=b['contract']!='curta' or h['hits']<2
        can_hit = can_hit and bool(self.p['deck']['draw'] or self.p['deck']['discard'])
        if can_hit and self.total(h)<b['limit'] and b.get('peek_mode')!='stop':
            a.append('pedir')
        two=len(h['cards'])==2
        if two and h['hits']==0 and not b['peeked'] and b['contract']!='firme' and b['identity']!='escrivao' and can_hit and self.p['fichas']>=self.double_cost(h):
            a.append('dobrar')
        equal=two and h['cards'][0]['valor']==h['cards'][1]['valor']
        impersonate=two and self.has('mascara_impostor') and 'mask' not in b['used'] and points(h['cards'][0]['valor'])==points(h['cards'][1]['valor'])
        free='split' in b['round_used'] and self.has('joias_gemeas')
        if (equal or impersonate) and h['hits']==0 and not self.oath('lamina',True) and b['contract']!='individual' and not b['peeked'] and len(b['hands'])<4 and (free or self.p['fichas']>=h['bet']):
            a.append('dividir')
        first=two and h['hits']==0 and len(b['hands'])==1 and not b['peeked']
        if first and b['contract']!='testemunhas' and not self.oath('honra',True) and not (b['all_in'] and self.oath('ultima',True)):
            a.append('desistir')
        if first and self.has('trono_vazio') and not self.s['throne'] and not b['swapped'] and b['ending'] != 'usurpar':
            a.append('trono')
        if can_hit and b['blessings'] and not b['peeked']:
            a.append('bencao')
        if can_hit and b['ending']=='governar' and self.p['itens'] and not b['peeked'] and 'sacrifice' not in b['round_used']:
            a.append('sacrificar')
        if can_hit and any(c['temporaria']=='brasa' for c in h['cards']) and 'ember' not in b['round_used']:
            a.append('brasa')
        if b['ending']=='usurpar' and 'crown' not in b['round_used'] and any(c['temporaria']=='coroa' for c in h['cards']):
            a.append('coroa')
        return a

    def battle_action(self, action, data):
        phase=self.s['phase']
        value=data.get('valor')
        b=self.b
        require(b is not None)
        if phase=='contrato':
            require(action=='contrato' and value in self.s['offers'])
            b['contract']=value
            self.rules()
            if value=='testemunhas':
                b['preview']=self.draw(b['decks'][b['active']])
            self.s['phase']='aposta'
            return
        if phase=='cobranca':
            require(action=='cobranca' and value in ('fichas','prestigio'))
            if value=='fichas':
                require(self.p['fichas']>=8,'A cobrança custa 8 fichas.')
                self.p['fichas']-=8
            else:
                self.prestige(-2)
            self.after_round()
            return
        if phase=='cobranca_real':
            require(action=='cobranca_real' and value in self.s['offers'])
            b['charge']=value
            self.prepare_round()
            return
        if phase=='consagrar':
            require(action=='consagrar' and value in self.p['juramentos'])
            self.p['consagrado']=value
            if value=='divida':
                self.p['debt']=0
                self.p['paid_debt']=True
            self.s['phase']='destino'
            return
        if phase=='destino':
            require(action=='destino' and value in ('governar','usurpar'))
            b['ending']=value
            self.prepare_round()
            return
        if phase=='pedagio':
            require(action=='pedagio' and value in ('pagar','revelar'))
            if value=='pagar':
                require(self.p['fichas']>=8,'São necessárias 8 fichas.')
                self.p['fichas']-=8
            else:
                b['face_exposed']=True
                self.rules()
            if not self.bankrupt():
                self.s['phase']='aposta'
            return
        require(action in self.available())
        b['last_action']=action
        if action=='apostar':
            self.start_round(value)
        elif action in ('segurar','recusar_seguro'):
            if action=='segurar':
                b['insurance']=b['hands'][0]['bet']/2
                self.p['fichas']-=b['insurance']
            self.after_insurance()
        elif action=='escolher':
            require(type(value) is int and 0<=value<len(b['choices']))
            card=b['choices'][value]
            self.p['deck']['draw'].remove(card['id'])
            b['hands'][b['current']]['cards'].append(self.player_card(copy.deepcopy(card)))
            b['choices']=[]
            self.s['phase']='jogando'
            self.after_hit(b['pending_action'])
        elif action=='continuar':
            if b['identity']=='cobrador' and b['result']['score']<0 and self.p['fichas']>=1:
                self.s['phase']='cobranca'
            else:
                self.after_round()
        elif action=='liquidar':
            self.offer_last_word()
        elif action=='cetro':
            b['used'].append('scepter')
            deck=b['decks'][b['active']]
            if deck['draw'] or deck['discard']:
                b['dealer'].append(self.draw(deck))
            self.offer_last_word()
        elif action in ('comprar_final','aceitar_resultado'):
            if action=='comprar_final':
                b['used'].append('last_word')
                b['current']=0
                h=b['hands'][0]
                h['cards'].append(self.player_card(self.draw(self.p['deck'])))
                h['hits']+=1
                h['no_natural']=True
                self.effect('ultima_palavra','Uma última carta, com o rival já revelado.')
                self.after_hit('ultima')
            else:
                self.settle()
        else:
            h=b['hands'][b['current']]
            if action=='parar':
                self.advance()
            elif action=='guardar':
                self.p['reserved']=h['cards'].pop()['id']
                h['no_natural']=True
                b['used'].append('pocket')
                self.effect('bolso_falso','Última carta guardada para abrir a próxima rodada.')
            elif action=='transferir':
                target=data.get('destino')
                require(type(target) is int and b['current']<target<len(b['hands']), 'Escolha uma mão ainda não jogada.')
                card=next((c for c in h['cards'] if c['id']==data.get('carta')),None)
                require(card is not None, 'Escolha uma carta desta mão.')
                h['cards'].remove(card)
                h['no_natural']=True
                b['hands'][target]['cards'].append(card)
                b['hands'][target]['no_natural']=True
                b['used'].append('balance')
                self.effect('balanca_carrasco',f'Carta transferida para a mão {target+1}.')
            elif action=='desistir':
                h['surrender']=True
                self.p['fichas']+=h['bet']/2
                b['surrender']=True
                self.advance()
            elif action=='dividir':
                a,c=h['cards']
                if a['valor']!=c['valor']:
                    b['used'].append('mask')
                free='split' in b['round_used'] and self.has('joias_gemeas')
                if not free:
                    self.p['fichas']-=h['bet']
                b['round_used'].append('split')
                self.p['stats']['splits']+=1
                self.unlock('trapaceiro')
                new={'cards':[h['cards'].pop()], 'bet':h['bet'], 'split':True, 'hits':0, 'double':False}
                h.update(split=True, no_natural=True)
                b['hands'].append(new)
                h['cards'].append(self.player_card(self.draw(self.p['deck'])))
                new['cards'].append(self.player_card(self.draw(self.p['deck'])))
                if self.total(h)>=b['limit']:
                    self.advance()
            elif action in ('pedir','dobrar','brasa'):
                if action=='brasa':
                    card=next(c for c in h['cards'] if c['temporaria']=='brasa')
                    h['cards'].remove(card)
                    self.remove_card(self.p['deck'],card['id'])
                    b['round_used'].append('ember')
                if action=='dobrar':
                    cost=self.double_cost(h)
                    self.p['fichas']-=cost
                    h['bet']*=2
                    h['double']=True
                    b['round_used'].append('double')
                    self.p['stats']['doubles']+=1
                self.hit(action)
            elif action=='trono':
                h['cards'],b['dealer']=b['dealer'],h['cards']
                h['no_natural']=True
                b['swapped']=True
                b['reveal']=True
                self.s['throne']=True
                if self.total(h)>=b['limit']:
                    self.advance()
            elif action in ('bencao','sacrificar'):
                if action=='sacrificar':
                    require(value in self.p['itens'],'Escolha a relíquia a sacrificar.')
                    self.p['itens'].remove(value)
                    b['round_used'].append('sacrifice')
                else:
                    b['blessings']-=1
                self.replenish(self.p['deck'])
                b['peeked']=True
                b['peek']=copy.deepcopy(self.p['deck']['cards'][self.p['deck']['draw'][-1]])
            elif action=='coroa':
                require(type(value) is int and 1<=value<=11,'Escolha um valor entre 1 e 11.')
                c=next(c for c in h['cards'] if c['temporaria']=='coroa')
                c['pontos']=value
                b['round_used'].append('crown')
                if self.total(h)>=b['limit']:
                    self.advance()

    def start_round(self, bet):
        require(type(bet) is int and 1<=bet<=self.p['fichas'],'Aposte um inteiro positivo até seu saldo.')
        b=self.b
        b.update(start_chips=self.p['fichas'], start_prestige=self.p['prestigio'], insurance=0,
                 all_in=bet==math.floor(self.p['fichas']), peek=None, seven_changed=False, figure_changed=False)
        if self.has('manto_nobreza'):
            self.p['fichas']+=5*(min(4,self.p['prestigio']//20)+1)
            self.effect('manto_nobreza',f"+{5*(min(4,self.p['prestigio']//20)+1)} fichas antes da aposta.")
        self.p['ultima_aposta']=bet
        self.p['fichas']-=bet
        h={'cards':[], 'bet':bet, 'split':False, 'hits':0, 'double':False}
        b['hands']=[h]
        rival=b['decks'][b['active']]
        for _ in range(2):
            if self.p['reserved'] and not h['cards']:
                card=copy.deepcopy(self.p['deck']['cards'][self.p['reserved']])
                self.p['reserved']=None
                h['no_natural']=True
                self.effect('bolso_falso','A carta guardada abriu esta mão. Sem blackjack natural.')
            else:
                card=self.draw(self.p['deck'])
            h['cards'].append(self.player_card(card))
            if b['preview']:
                b['dealer'].append(b['preview'])
                b['preview']=None
            else:
                b['dealer'].append(self.draw(rival))
        if b['ending']=='usurpar':
            crown=self.card('0','Sem naipe','coroa')
            h['cards'].append(crown)
        b['eclipse']=b['eclipse_pending']
        b['eclipse_pending']=False
        visible=b['dealer'][1 if b['eclipse'] else 0]
        if (self.has('manilha_sorte') and visible['valor']=='A' and self.p['fichas']>=bet/2
                and not self.oath('honra',True) and not (b['all_in'] and self.oath('ultima',True)) and b['limit']==21):
            self.s['phase']='seguro'
        else:
            self.after_insurance()

    def player_card(self, c):
        b=self.b
        if b['charge']=='sete' and c['valor']=='7' and not b['seven_changed']:
            c['pontos']=6
            b['seven_changed']=True
        if b['charge']=='humilde' and c['valor'] in ('J','Q','K') and not b['figure_changed']:
            c['pontos']=9
            b['figure_changed']=True
        return c

    def after_insurance(self):
        b=self.b
        if self.natural(b['dealer']):
            self.p['fichas']+=b['insurance']*3
            self.settle()
        else:
            self.s['phase']='jogando'
            if self.total(b['hands'][0])>=b['limit']:
                self.advance()

    def hit(self, action):
        b=self.b
        h=b['hands'][b['current']]
        h['hits']+=1
        if self.has('caleidoscopio_acaso') and 'oracle' not in b['round_used'] and not b['peeked']:
            self.replenish(self.p['deck'],3)
            b['choices']=[copy.deepcopy(self.p['deck']['cards'][cid]) for cid in self.p['deck']['draw'][-3:]]
            if b['choices']:
                self.effect('caleidoscopio_acaso','Escolha uma das próximas cartas do seu baralho.')
                b['round_used'].append('oracle')
                b['pending_action']=action
                self.s['phase']='oraculo'
                return
        h['cards'].append(self.player_card(self.draw(self.p['deck'])))
        self.after_hit(action)

    def after_hit(self, action):
        b=self.b
        h=b['hands'][b['current']]
        b['peeked']=False
        b['peek']=None
        value=self.total(h)
        if value==22 and value>b['limit'] and self.has('coroa_22') and 'crown22' not in b['used']:
            h['adjust']=1
            b['used'].append('crown22')
            self.effect('coroa_22','22 se tornou 21.')
        if self.total(h)>b['limit'] and action!='dobrar' and self.has('tesoura_destino') and 'scissors' not in b['used']:
            c=h['cards'].pop()
            self.discard_card(c)
            b['used'].append('scissors')
            self.effect('tesoura_destino','A carta que estourou foi descartada.')
            self.settle() if action=='ultima' else self.advance()
            return
        if action=='ultima':
            self.settle()
            return
        if action=='dobrar' or self.total(h)>=b['limit'] or (b['contract']=='curta' and h['hits']>=2):
            self.advance()

    def advance(self):
        b=self.b
        b['peeked']=False
        b['peek']=None
        b['current']+=1
        while b['current']<len(b['hands']) and self.total(b['hands'][b['current']])>=b['limit']:
            b['current']+=1
        if b['current']<len(b['hands']):
            return
        if any(not h.get('surrender') and self.total(h)<=b['limit'] for h in b['hands']):
            rival=b['decks'][b['active']]
            while self.total(b['dealer'])<b['dealer_stop'] and (rival['draw'] or rival['discard']):
                b['dealer'].append(self.draw(rival))
                if b['identity']=='sinos':
                    b['bells']+=1
                    if b['bells']>=7:
                        b['blessings']+=1
                        b['bells']=0
                if b['identity']=='gemeas' and self.total(b['dealer'])>b['limit'] and b['active'] not in b['sisters_saved']:
                    self.discard_card(b['dealer'].pop())
                    b['sisters_saved'].append(b['active'])
                    break
        b['reveal']=True
        if self.has('cetro_sentencas') and 'scepter' not in b['used'] and not self.natural(b['dealer']) and any(self.total(h)<=b['limit'] and not h.get('surrender') for h in b['hands']):
            self.s['phase']='revelacao'
        else:
            self.offer_last_word()

    def offer_last_word(self):
        b=self.b
        h=b['hands'][0]
        if (self.has('ultima_palavra') and 'last_word' not in b['used'] and len(b['hands'])==1
                and not h['double'] and not h.get('surrender') and not self.natural(h)
                and self.total(h)<b['limit'] and not self.natural(b['dealer'])
                and (b['contract']!='curta' or h['hits']<2)
                and (self.p['deck']['draw'] or self.p['deck']['discard'])):
            self.s['phase']='ultima_palavra'
        else:
            self.settle()

    def multiplier(self, hand):
        return max(.1,min(3,1+sum(p['amount'] for p in self.multiplier_parts(hand))))

    def multiplier_parts(self, hand):
        ranks=[c['valor'] for c in hand['cards']]
        v=self.total(hand)
        parts=[]
        def add(source, amount):
            if amount: parts.append({'source':source, 'amount':round(amount,4)})
        add('afinidade',.15*min(5,max((self.p['afinidades'].get(r,0) for r in ranks),default=0)))
        add('broche_prudencia', (.2 if self.has('broche_prudencia') and v==17 else 0))
        add('forca_sete', (.75 if self.has('forca_sete') and '7' in ranks else 0))
        add('bencao_reinos_v2', (.25*max(0,len({c['naipe'] for c in hand['cards'] if c['naipe']!='Sem naipe'})-1) if self.has('bencao_reinos_v2') else 0))
        add('rosario_humildes', (.4 if self.has('rosario_humildes') and not set(ranks)&{'A','J','Q','K'} else 0))
        add('fortuna', (.25 if self.oath('fortuna') else 0))
        add('gloria', -(.2 if self.oath('gloria',True) else 0))
        add('dobrar', (.6 if self.oath('dobrar') and hand['double'] else 0))
        add('lamina', (.35 if self.oath('lamina') and len(ranks)==2 else 0))
        add('quinta', (1 if self.oath('quinta') and len(ranks)>=5 else 0))
        add('quinta', -(.2 if self.oath('quinta',True) and len(ranks)==2 else 0))
        add('sete', (.5 if self.oath('sete') and '7' in ranks else 0))
        if self.oath('humilde'):
            add('humilde', (.45 if not set(ranks)&{'J','Q','K'} else -.25 if self.oath('humilde',True) else 0))
        add('cacador', -(.2 if self.oath('cacador',True) and self.b['kind']=='mesa' else 0))
        add('ultima', (1 if self.oath('ultima') and self.b['all_in'] else 0))
        add('contrato', (.25 if self.b['contract']=='individual' or self.b['identity']=='escrivao' else 0))
        add('marcas', (sum(.3 if c['marca']=='quebradica' else .6 if c['marca']=='maldita' else 0 for c in hand['cards'])))
        return parts

    def receive_profit(self, profit):
        paid_origin=min(self.p['origin_debt'],round(profit*.25,2))
        self.p['origin_debt']=round(self.p['origin_debt']-paid_origin,2)
        profit-=paid_origin
        if paid_origin:
            self.effect('credor',f'{paid_origin:g} fichas pagaram a dívida familiar.')
        payment=0
        if self.p['debt']:
            payment=min(self.p['debt'],round(profit/2,2))
            self.p['debt']=round(self.p['debt']-payment,2)
            profit-=payment
            if not self.p['debt']:
                self.p['paid_debt']=True
        self.p['fichas']+=profit
        return {'family':paid_origin, 'oath':payment, 'received':profit}

    def settle(self):
        b=self.b
        score=0
        results=[]
        dealer=self.total(b['dealer'])
        natural=self.natural(b['dealer'])
        for h in b['hands']:
            hand_start=self.p['fichas']
            profit=0
            payments={'family':0,'oath':0,'received':0}
            v=self.total(h)
            if h.get('surrender') or v>b['limit']:
                outcome=-1
            elif self.natural(h) and not natural:
                outcome=1
            elif natural and not self.natural(h):
                outcome=-1
            elif dealer>b['limit'] or v>dealer:
                outcome=1
            elif v<dealer:
                outcome=-1
            else:
                outcome=0
                if not natural and (b['ending']=='usurpar' or b['charge']=='lamina' and len(h['cards'])==2 or b['charge']=='honra' and v<=17):
                    outcome=-1
                elif not natural and b['draws']>=2:
                    outcome=1 if len(h['cards'])<=len(b['dealer']) else -1
            multiplier=self.multiplier(h)
            if outcome>0:
                profit=round(h['bet']*(1.5 if self.natural(h) else 1)*multiplier,2)
                if b['charge']=='fortuna':
                    profit=round(profit*.9,2)
                self.p['fichas']+=h['bet']
                payments=self.receive_profit(profit)
                for part in self.multiplier_parts(h):
                    self.effect(part['source'], f"{part['amount']:+.0%} no lucro desta mão.")
                if h['double']:
                    b['double_win']=True
                if len(h['cards'])>=5:
                    self.p['stats']['long']+=1
                for c in h['cards']:
                    self.p['stats']['wins'][c['valor']]=self.p['stats']['wins'].get(c['valor'],0)+1
                    if c['marca']=='real':
                        self.prestige(1)
                        self.effect('marcas','Carta Real: prestígio recebido.')
                    if c['marca']=='dourada' or c['temporaria']=='brasa':
                        self.p['fichas']+=5
                        self.effect('marcas','Carta Dourada ou Brasa: +5 fichas.')
                    if c['marca']=='quebradica':
                        c['destroy']=True
                if b['contract']=='curta' and self.natural(h):
                    score+=1
            elif outcome==0:
                self.p['fichas']+=h['bet']
                if self.has('ficha_cobre') and 'copper' not in b['used']:
                    self.p['fichas']+=5
                    b['used'].append('copper')
                    self.effect('ficha_cobre','Empate: +5 fichas.')
            else:
                if v>b['limit'] and self.has('dedal_costureira') and 'thimble' not in b['used']:
                    self.p['fichas']+=round(h['bet']*.1,2)
                    b['used'].append('thimble')
                    self.effect('dedal_costureira',f"Estouro: {round(h['bet']*.1,2):g} fichas devolvidas.")
                if self.oath('dobrar',True) and h['double']:
                    self.prestige(-2)
                if self.oath('sete',True) and any(c['valor']=='7' for c in h['cards']):
                    self.prestige(-1)
                if self.oath('ultima',True) and b['all_in']:
                    self.prestige(-2)
                self.p['fichas']=max(0,self.p['fichas']-5*sum(c['marca']=='maldita' for c in h['cards']))
            score+=outcome
            results.append({'texto':'Desistência' if h.get('surrender') else 'Estourou' if v>b['limit'] else 'Blackjack!' if outcome>0 and self.natural(h) else 'Vitória' if outcome>0 else 'Derrota' if outcome<0 else 'Empate', 'resultado':outcome,'bonus':round(multiplier,2)})
            results[-1]['calculation']={'bet':h['bet'], 'natural':self.natural(h), 'parts':self.multiplier_parts(h),
                'multiplier':multiplier, 'profit':profit, 'payments':payments,
                'credited':round(self.p['fichas']-hand_start,2), 'applied':outcome>0}
        if score>0:
            b['wins']+=2 if b['contract']=='curta' and any(self.natural(h) and r['resultado']>0 for h,r in zip(b['hands'],results)) else 1
            b['draws']=0
            if b['charge']=='divida':
                self.p['fichas']=max(0,self.p['fichas']-5)
        elif score<0:
            b['losses']+=1
            b['perfect']=False
            b['draws']=0
            if b['charge']=='gloria':
                self.prestige(-2)
            if b['charge']=='ultima' and b['all_in']:
                self.prestige(-1)
        else:
            b['draws']+=1
        b['rounds']+=1
        self.s['round_count']+=1
        b['reveal']=True
        b['result']={'score':score,'hands':results, 'fichas':round(self.p['fichas']-b['start_chips'],2),
                     'prestigio':self.p['prestigio']-b['start_prestige']}
        self.s['history'].insert(0,{'rodada':self.s['round_count'], 'adversario':self.enemy_name(), **b['result']})
        self.s['history']=self.s['history'][:12]
        self.s['phase']='resultado'

    def discard_card(self, c):
        if c['temporaria']=='coroa':
            return
        decks=[self.p['deck']]+list(self.b['decks'].values())
        for deck in decks:
            if c['id'] in deck['cards']:
                permanent = sum(not card['temporaria'] for card in deck['cards'].values())
                if c.get('destroy') and deck is self.p['deck'] and permanent <= 16:
                    # O piso mantém quatro mãos divididas possíveis na próxima rodada.
                    deck['cards'][c['id']]['marca'] = None
                    c['destroy'] = False
                    self.s['notice'] = 'O baralho atingiu 16 cartas permanentes. A marca Quebradiça se desfez, preservando a carta.'
                if c.get('destroy') or c['temporaria']=='brasa':
                    self.remove_card(deck,c['id'])
                elif c['id'] not in deck['discard'] and c['id'] not in deck['draw']:
                    deck['discard'].append(c['id'])
                return

    def archive_round(self):
        b=self.b
        for h in b['hands']:
            for card in h['cards']:
                self.discard_card(card)
        for card in b['dealer']:
            self.discard_card(card)
        rival=b['decks'][b['active']]
        if b['identity']=='ferrugem' and b['result']['score']>0:
            figures=[cid for cid,c in rival['cards'].items() if c['valor'] in ('J','Q','K')]
            for cid in self.rng.sample(figures,min(2,len(figures))):
                self.remove_card(rival,cid)
        if b['identity']=='cinzas':
            candidates=[c for c in b['dealer'] if c['valor']!='A']
            if candidates:
                self.remove_card(rival,min(candidates,key=lambda c:points(c['valor']))['id'])
            if b['result']['score']>0:
                self.add_card('2',temporary='brasa')
        if b['identity']=='astronomo' and b['wins']>=2 and not b['eclipse_used']:
            b['eclipse_pending']=True
            b['eclipse_used']=True

    def after_round(self):
        b=self.b
        self.archive_round()
        if self.bankrupt(in_battle=True):
            return
        if b['wins']>=b['target']:
            if b['identity']=='rei' and b['act']<3:
                b['act']+=1
                b['wins']=0
                b['charge']=None
                self.p['fichas']+=50
                if b['act']==2:
                    self.s['offers']=self.rng.sample(self.p['juramentos'],min(2,len(self.p['juramentos'])))
                    self.s['phase']='cobranca_real'
                else:
                    self.s['phase']='consagrar'
                return
            self.end_encounter(True)
        elif b['losses']>=b['max_losses'] or b['kind']=='mesa' and b['rounds']>=3:
            self.end_encounter(False)
        else:
            self.prepare_round()

    def bankrupt(self, in_battle=False):
        if self.p['fichas']>=1:
            return False
        if self.has('coracao_exilada') and not self.p['revived']:
            self.p['revived']=True
            self.p['itens'].remove('coracao_exilada')
            self.p['fichas']=200
            self.s['notice']='O Coração da Rainha se partiu. Você retorna com 200 fichas.'
            if in_battle:
                self.end_encounter(False)
            else:
                self.s['phase']='mapa'
        else:
            self.finish(False,'Suas fichas acabaram. O reino guardará seu nome.')
        return True

    def end_encounter(self, won):
        b=self.b
        boss=b['kind']=='boss'
        if won:
            self.unlock('herdeiro')
            amount={'mesa':3,'elite':7,'boss':12}[b['kind']]
            if b['double_win'] and self.has('luvas_duelista'):
                amount*=1.3
            self.prestige(amount)
            reward={'mesa':20,'elite':40,'boss':80}[b['kind']]
            if boss and self.oath('cacador'):
                reward*=1.5
            self.p['fichas']+=reward
            if b['perfect'] and self.oath('honra'):
                self.p['fichas']+=20
        else:
            self.prestige(-{'mesa':2,'elite':3,'boss':5}[b['kind']])
        self.s['result']={'won':won,'boss':boss,'retry':boss and not won and not self.s['retry'],
                          'cost':30*(self.s['region']+1),'name':self.enemy_name()}
        if won and b['identity']=='rei':
            self.finish(True, 'Você escolheu '+('governar' if b['ending']=='governar' else 'usurpar')+' o reino.')
            return
        if won:
            rarity='mitico' if boss else 'raro' if b['kind']=='elite' else self.rng.choice(['comum','incomum'])
            pool=[k for k,v in RELICS.items() if v['raridade']==rarity and k not in self.p['itens']]
            count=4 if b['kind']=='elite' and self.oath('cacador') else 3
            self.s['offers']=self.rng.sample(pool,min(count,len(pool)))
            if self.s['offers']:
                self.s['phase']='recompensa'
                return
            self.p['fichas']+=25
        self.s['phase']='conclusao'

    def after_reward(self):
        self.s['phase']='conclusao'

    def finish(self, won, reason):
        self.unlock('exilada')
        self.s.update(phase='fim', epilogue=reason, victory=won)
        if won:
            if 'carta_real' not in self.s['unlocks']:
                self.s['unlocks'].append('carta_real')
            path=self.p['caminho']
            ending=self.b['ending'] if self.s.get('battle') else None
            text={('nobreza','governar'):'As portas do palácio se abrem. Você governa ouvindo as vozes da estrada.',
                  ('nobreza','usurpar'):'A corte esperava clemência. Você tomou a coroa e deixou uma promessa para trás.',
                  ('tirania','governar'):'O reino se preparou para o medo. Sua primeira ordem foi abrir as portas.',
                  ('tirania','usurpar'):'Seu estandarte ocupa o trono. O reino conhece o preço de desafiá-lo.'}
            self.s['epilogue']+=' '+text.get((path,ending),'')
            self.s['epilogue']+=' Desbloqueio: nas próximas jornadas, marque gratuitamente sua primeira carta como Real.'
        self.s['legends'].append({'nome':self.p['nome'],'vitoria':won,'regiao':self.s.get('region',0)+1,
                                  'caminho':self.p['caminho'],'prestigio':self.p['prestigio']})

    def enemy_name(self):
        b=self.b
        if b['identity']=='gemeas':
            return 'Íris, o Reflexo Voraz' if b['active']=='a' else 'Véspera, o Reflexo Imóvel'
        return BOSSES.get(b['identity'], ELITES.get(b['identity'],{'nome':'Jogador da Estrada'}))['nome']

    def public(self):
        s=self.s
        out={k:copy.deepcopy(s.get(k)) for k in ('versao','revisao','phase','region','layer','column','visited','notice','round_count','history','result','epilogue','victory','legends','unlocks')}
        out.update(regions=REGIONS, catalog={'relics':RELICS,'oaths':OATHS,'marks':MARKS,'origins':ORIGINS}, player=None,
                   effects=copy.deepcopy(s['effects']), new_unlocks=s['new_unlocks'][:])
        if not self.p:
            return out
        p=self.p
        out['player']={k:copy.deepcopy(v) for k,v in p.items() if k not in ('deck','stats')}
        titles=['Desconhecida' if p['genero']=='m' else 'Desconhecido','Nome nas tavernas','Figura influente','Pretendente','Lenda do reino']
        dark=['Sombra sem nome','Vigarista da fronteira','Senhora do submundo' if p['genero']=='m' else 'Senhor do submundo','Usurpadora' if p['genero']=='m' else 'Usurpador','Flagelo do reino']
        out['player']['titulo']=(dark if p['caminho']=='tirania' else titles)[min(4,p['prestigio']//20)]
        d=p['deck']
        out['deck']={'cards':sorted(copy.deepcopy(list(d['cards'].values())),key=lambda c:(RANKS.index(c['valor']) if c['valor'] in RANKS else 99,c['naipe'],c['id'])),
                     'remaining':len(d['draw']), 'discard':[copy.deepcopy(d['cards'][cid]) for cid in d['discard']], 'shuffles':d['shuffles']}
        if self.has('lente_escrivao'):
            out['deck']['counts']=dict(Counter(d['cards'][cid]['valor'] for cid in d['draw']))
        out['boss']={'id':s['boss_ids'][s['region']],**BOSSES[s['boss_ids'][s['region']]]}
        if s['region']==3:
            out['boss'].update(style=s.get('king_style'),face=s.get('king_face'))
        out['nodes']=[{**n,'available':s['phase']=='mapa' and self.possible_node(n),'connected':self.connected(n),
                       'name':BOSSES[s['boss_ids'][s['region']]]['nome'] if n['type']=='boss' else ELITES[n['elite']]['nome'] if n['elite'] else NODE_NAMES[n['type']]} for n in s['maps'][s['region']]]
        out['pending']=copy.deepcopy(s.get('pending'))
        phase=s['phase']
        if phase in ('juramento','recompensa','contrato','cobranca_real'):
            out['offers']=s['offers'][:]
        if phase in ('evento','refugio','sacrario'):
            out['options']=[{'id':k,'nome':n,'descricao':d} for k,n,d in self.story_options()]
            out['event']=s.get('event')
            if phase=='evento' and s['event'].startswith('historia:'):
                out['story']=stories.scene(self)
                out['options']=out['story']['options']
        if phase=='loja':
            out['shop']={**copy.deepcopy(s['shop']), 'prices':{k:self.shop_price(k) for k in s['shop']['offers']},
                         'credit':self.has('ampulheta_usurario') and not p['loan'] and not s['shop']['loan_used'] and s['region']<3}
        if s.get('battle'):
            b=self.b
            visible={k:copy.deepcopy(v) for k,v in b.items() if k not in ('decks','dealer','preview','choices','hands')}
            visible['name']=self.enemy_name()
            if b['identity'] in BOSS_PRESENTATION:
                presence=copy.deepcopy(BOSS_PRESENTATION[b['identity']])
                mood='win' if b.get('result') and b['result']['score']>0 else 'loss' if b.get('result') and b['result']['score']<0 else 'double' if b.get('last_action')=='dobrar' and 'double' in presence else 'intro'
                presence['speech']=presence[mood]
                presence['mood']=mood
                if b['identity']=='cobrador' and p['origin_debt'] and mood=='intro':
                    presence['speech']=f"Sua família ainda me deve {p['origin_debt']:g} fichas."
                visible['presence']=presence
            visible['charge_descriptions']=CHARGES
            visible['description']=BOSSES.get(b['identity'],ELITES.get(b['identity'],{'descricao':'Até três rodadas; vença duas. O adversário para em 17.'}))['descricao']
            visible['hands']=[{**copy.deepcopy(h),'total':self.total(h),'natural':self.natural(h)} for h in b['hands']]
            reveal=b['reveal'] or phase in ('resultado','recompensa','conclusao','fim')
            hidden=0 if b.get('eclipse') else 1
            visible['dealer']=[copy.deepcopy(c) if reveal or i!=hidden else {'oculta':True} for i,c in enumerate(b['dealer'])]
            visible['dealer_total']=self.total(b['dealer']) if reveal else None
            visible['preview']=copy.deepcopy(b['preview'])
            visible['choices']=copy.deepcopy(b['choices']) if phase=='oraculo' else []
            visible['composition']=dict(Counter(c['valor'] for c in b['decks'][b['active']]['cards'].values()))
            visible['remaining']=len(b['decks'][b['active']]['draw'])
            visible['actions']=self.available()
            visible['double_cost']=self.double_cost(b['hands'][b['current']]) if phase=='jogando' else None
            out['battle']=visible
        else:
            out['battle']=None
        return out


class AdventureMesa:
    """Persistência transacional; uma revisão por movimento, incluindo escolhas de mapa."""
    def __init__(self, path, seed=None):
        self.save=Path(path)
        self.lock=threading.Lock()
        self.game=Adventure(seed)
        if self.save.exists():
            data=json.loads(self.save.read_text(encoding='utf-8'))
            if data.get('versao')==1:
                backup=self.save.with_name(self.save.name+'.v1.bak')
                if not backup.exists():
                    backup.write_bytes(self.save.read_bytes())
                self.migrate(data)
                self.salvar()
            else:
                self.game.restore(data)

    def migrate(self, data):
        old=data.get('jogador')
        if not old:
            return
        g=self.game
        g.new(old['nome'],old.get('genero','h'))
        p=g.p
        p['fichas']=old.get('fichas',200)
        phase=(data.get('rodada') or {}).get('fase')
        if phase in ('jogando','seguro','oraculo'):
            p['fichas']+=sum(m.get('aposta',0) for m in data.get('maos',[]))
            p['fichas']+=(data.get('rodada') or {}).get('seguro',0)
        p['prestigio']=min(100,int(abs(old.get('prestigio',0))/100))
        p['caminho']=old.get('caminho','nobreza')
        p['itens']=[i for i in old.get('itens',[]) if i in RELICS]
        p['afinidades']=old.get('afinidades',{})
        g.s['notice']='Save 0.4 preservado em .v1.bak. Recursos e itens migrados; apostas pendentes devolvidas. A nova campanha começa na primeira região.'
        if p['fichas']<1:
            g.finish(False,'A jornada anterior já havia terminado sem fichas.')

    def salvar(self):
        name=None
        try:
            with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=self.save.parent,delete=False) as f:
                name=f.name
                json.dump(self.game.export(),f,ensure_ascii=False,indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(name,self.save)
        finally:
            if name and os.path.exists(name):
                os.unlink(name)

    def agir(self, data):
        require(type(data.get('revisao')) is int and data['revisao']==self.game.s['revisao'],
                'A jornada mudou em outra janela. Atualize antes de continuar.')
        before=self.game.export()
        try:
            self.game.interact(data.get('acao'),data)
            self.game.s['revisao']+=1
            self.salvar()
        except Exception:
            self.game.restore(before)
            raise

    def estado(self):
        return self.game.public()
