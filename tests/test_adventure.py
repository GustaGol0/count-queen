"""Regressões de jornada, efeitos, regras de bosses e persistência."""
import copy
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from count_queen.adventure import Adventure, AdventureMesa
from count_queen.content import RELICS, OATHS, BOSS_PAIRS, MARKS


def game(seed=8):
    g=Adventure(seed)
    g.new('Rainha Áurea','m')
    g.interact('juramento',{'valor':g.s['offers'][0]})
    g.p['juramentos']=[]
    return g


def ordered(g, ranks):
    deck=g.deck(ranks)
    deck['draw']=list(reversed(list(deck['cards'])))
    return deck


def battle(g, player, rival, identity='mesa', kind='mesa', bet=10):
    g.p['deck']=ordered(g,player)
    if identity=='rei':
        g.s.update(king_style='equilibrio',king_face='A')
    g.start_battle(kind,identity)
    g.b['decks'][g.b['active']]=ordered(g,rival)
    g.s['phase']='aposta'
    g.interact('apostar',{'valor':bet})
    return g.b


class CampaignTests(unittest.TestCase):
    def test_catalog_has_27_relics_and_twelve_oaths(self):
        self.assertEqual(Counter(v['raridade'] for v in RELICS.values()),{'comum':6,'incomum':6,'raro':9,'mitico':6})
        self.assertEqual(len(OATHS),12)

    def test_boss_pairs_and_map_connections_are_saved_without_reroll(self):
        seen=[set() for _ in range(4)]
        for seed in range(100):
            g=game(seed)
            for i,boss in enumerate(g.s['boss_ids']):seen[i].add(boss)
            clone=Adventure();clone.restore(json.loads(json.dumps(g.export())))
            self.assertEqual(clone.public(),g.public())
            node=g.s['maps'][0][0]
            g.interact('no',{'valor':node['id']})
            self.assertEqual(g.s['phase'],'encontro')
            g.interact('voltar',{})
            self.assertEqual(g.s['layer'],-1)
            with self.assertRaises(ValueError):g.interact('no',{'valor':g.s['maps'][0][-1]['id']})
        for actual,expected in zip(seen,BOSS_PAIRS):self.assertEqual(actual,set(expected))

    def test_compass_crosses_once_but_never_skips_layers(self):
        g=game();g.p['itens']=['bussola_contrabandista'];g.s.update(layer=0,column=0)
        n=next(n for n in g.s['maps'][0] if n['row']==1 and n['col']==2)
        self.assertTrue(g.possible_node(n));g.interact('no',{'valor':n['id']});g.interact('entrar',{})
        self.assertTrue(g.s['compass'])
        blocked=next(n for n in g.s['maps'][0] if n['row']==2 and n['col']==0)
        self.assertFalse(g.possible_node(blocked))

    def test_oaths_persist_and_do_not_offer_conflicts(self):
        g=game();g.p['juramentos']=['fortuna','lamina'];g.s['region']=1;g.start_region()
        self.assertEqual(len(g.s['offers']),3)
        self.assertFalse(set(g.s['offers'])&{'fortuna','gloria','lamina','quinta'})
        g.s['offers']=['divida','honra','sete'];g.interact('juramento',{'valor':'divida'})
        self.assertEqual(g.p['fichas'],350);self.assertEqual(g.p['debt'],225)
        g.receive_profit(500)
        self.assertEqual(g.p['debt'],0);self.assertTrue(g.p['paid_debt'])

    def test_player_and_rival_decks_stay_separate_across_rounds(self):
        g=game();battle(g,['10','8','4','5'],['10','7','6','2'])
        player_ids=set(g.p['deck']['cards']);rival_ids=set(g.b['decks']['a']['cards'])
        self.assertFalse(player_ids&rival_ids)
        g.interact('parar',{})
        player_hand=[c['id'] for c in g.b['hands'][0]['cards']]
        g.interact('continuar',{})
        self.assertTrue(set(player_hand)<=set(g.p['deck']['draw']+g.p['deck']['discard']))
        self.assertEqual(set(g.p['deck']['cards']),player_ids)
        self.assertEqual(set(g.b['decks']['a']['cards']),rival_ids)

    def test_shop_excludes_mythics_prices_stable_and_service_is_bounded(self):
        g=game();g.enter({'type':'loja','elite':None});g.p['fichas']=1000
        prices=g.public()['shop']['prices']
        self.assertTrue(all(RELICS[k]['raridade']!='mitico' for k in prices))
        g.p['fichas']=2000
        self.assertEqual(g.public()['shop']['prices'],prices)
        g.interact('servico',{});self.assertEqual(g.s['phase'],'oficina')
        cid=next(iter(g.p['deck']['cards']))
        g.interact('marcar',{'carta':cid,'valor':'dourada'})
        self.assertEqual(g.p['deck']['cards'][cid]['marca'],'dourada')
        with self.assertRaises(ValueError):g.interact('servico',{})

    def test_loans_are_collected_next_region_and_not_offered_at_final(self):
        g=game();g.p['itens']=['ampulheta_usurario'];g.enter({'type':'loja'})
        k=g.s['shop']['offers'][0];price=g.shop_price(k)
        g.interact('comprar',{'valor':k,'credito':True})
        self.assertEqual(g.p['loan'],round(price/2*1.25,2))
        old=g.p['fichas'];loan=g.p['loan'];g.s['region']=1;g.start_region()
        self.assertEqual(g.p['fichas'],old-loan);self.assertEqual(g.p['loan'],0)
        g.s['region']=3;g.enter({'type':'loja'})
        self.assertFalse(g.public()['shop']['credit'])

    def test_workshop_marks_transform_remove_and_add(self):
        g=game();cid=next(iter(g.p['deck']['cards']))
        for action,data in [('marcar',{'carta':cid,'valor':'real'}),('transformar',{'carta':cid,'valor':'7'})]:
            g.enter({'type':'oficina'});g.interact(action,data)
        self.assertEqual(g.p['deck']['cards'][cid]['valor'],'7');self.assertEqual(g.p['deck']['cards'][cid]['marca'],'real')
        g.enter({'type':'oficina'})
        with self.assertRaises(ValueError):g.interact('marcar',{'carta':cid,'valor':'maldita'})
        g.interact('remover',{'carta':cid});self.assertNotIn(cid,g.p['deck']['cards'])
        g.enter({'type':'oficina'});g.interact('adicionar',{'valor':'A'});self.assertEqual(len(g.p['deck']['cards']),52)

    def test_event_route_oath_adds_choice_and_prestige_opens_another(self):
        g=game();g.p['itens']=['moeda_peregrino'];g.enter({'type':'evento'})
        self.assertEqual(g.p['fichas'],205)
        self.assertEqual(len(g.story_options()),3)
        g.p['juramentos']=['estrada'];self.assertIn('estrada',[o[0] for o in g.story_options()])
        g.p['juramentos']=[];g.p['prestigio']=25;self.assertIn('influencia',[o[0] for o in g.story_options()])
        g.s['phase']='sacrario';g.interact('escolha',{'valor':'profanar'})
        self.assertEqual(g.p['caminho'],'tirania')
        self.assertTrue(any(c['marca']=='maldita' for c in g.p['deck']['cards'].values()))
        g.s['phase']='refugio';g.interact('escolha',{'valor':'purificar'})
        self.assertFalse(any(c['marca']=='maldita' for c in g.p['deck']['cards'].values()))

    def test_mythics_only_in_boss_reward_pools(self):
        for kind,identity,rarity in [('mesa','mesa',None),('elite','novica','raro'),('boss','ferrugem','mitico')]:
            g=game();g.start_battle(kind,identity);g.end_encounter(True)
            actual={RELICS[k]['raridade'] for k in g.s['offers']}
            self.assertEqual(actual,{rarity}) if rarity else self.assertTrue(actual<={'comum','incomum'})
            self.assertEqual(len(g.s['offers']),3)
            key=g.s['offers'][0];g.interact('reliquia',{'valor':key})
            with self.assertRaises(ValueError):g.interact('reliquia',{'valor':key})

    def test_revival_consumes_heart_and_loses_encounter(self):
        g=game();g.p['itens']=['coracao_exilada'];g.start_battle('mesa','mesa');g.p['fichas']=0
        self.assertTrue(g.bankrupt(in_battle=True));self.assertEqual(g.p['fichas'],200)
        self.assertNotIn('coracao_exilada',g.p['itens']);self.assertFalse(g.s['result']['won'])
        g.p['fichas']=0;g.bankrupt();self.assertEqual(g.s['phase'],'fim')

    def test_final_win_unlock_is_applied_to_next_journey(self):
        g=game();g.s.update(king_style='equilibrio',king_face='A');g.start_battle('boss','rei');g.b['ending']='governar'
        g.finish(True,'Vitória');self.assertIn('carta_real',g.s['unlocks']);g.new('Segunda','h')
        self.assertEqual(sum(c['marca']=='real' for c in g.p['deck']['cards'].values()),1)
        self.assertEqual(len(g.s['legends']),1)

    def test_spending_last_chip_outside_combat_finishes_journey(self):
        g=game();g.s.update(phase='evento',event='ponte');g.p['fichas']=15
        g.interact('escolha',{'valor':'pagar'})
        self.assertEqual(g.s['phase'],'fim')
        g=game();g.enter({'type':'loja'})
        key=g.s['shop']['offers'][0];g.p['fichas']=g.shop_price(key)
        g.interact('comprar',{'valor':key})
        self.assertEqual(g.s['phase'],'fim')

    def test_funds_in_active_all_in_hand_do_not_trigger_premature_game_over(self):
        g=game();battle(g,['10','8'],['10','7'],bet=200)
        self.assertEqual(g.s['phase'],'jogando');self.assertEqual(g.p['fichas'],0)
        g.interact('parar',{});self.assertEqual(g.p['fichas'],400)

    def test_fragile_card_preserves_minimum_deck_and_clears_mark(self):
        g=game();g.start_battle('mesa','mesa');g.p['deck']=ordered(g,['2']*16)
        c=g.draw(g.p['deck']);g.p['deck']['cards'][c['id']]['marca']='quebradica'
        c['destroy']=True;g.discard_card(c)
        self.assertEqual(len(g.p['deck']['cards']),16)
        self.assertIsNone(g.p['deck']['cards'][c['id']]['marca'])
        self.assertIn(c['id'],g.p['deck']['discard'])

    def test_extra_ember_does_not_allow_removing_permanent_below_minimum(self):
        g=game();g.p['deck']=ordered(g,['2']*16);g.add_card('2',temporary='brasa')
        g.enter({'type':'oficina'});cid=next(iter(g.p['deck']['cards']))
        with self.assertRaises(ValueError):g.interact('remover',{'carta':cid})


class CombatTests(unittest.TestCase):
    def test_payouts_natural_bust_push(self):
        cases=[(['A','K'],['9','8'],215),(['A','K'],['A','K'],200),(['10','9'],['A','K'],190)]
        for own,enemy,expected in cases:
            g=game();battle(g,own,enemy)
            self.assertEqual(g.s['phase'],'resultado');self.assertEqual(g.p['fichas'],expected)

    def test_double_split_and_oracle_resume(self):
        g=game();g.p['itens']=['caleidoscopio_acaso'];battle(g,['5','6','2','3','K'],['10','7'])
        g.interact('dobrar',{});self.assertEqual(g.s['phase'],'oraculo')
        export=json.loads(json.dumps(g.export()));g.restore(export)
        index=next(i for i,c in enumerate(g.b['choices']) if c['valor']=='K')
        g.interact('escolher',{'valor':index});self.assertEqual(g.p['fichas'],220)
        self.assertEqual(g.b['hands'][0]['bet'],20)
        g=game();g.p['itens']=['mascara_impostor','joias_gemeas'];battle(g,['J','Q','A','A'],['10','7'])
        g.interact('dividir',{});self.assertEqual(g.s['phase'],'resultado')
        self.assertEqual(g.p['fichas'],220);self.assertTrue(all(not g.natural(h) for h in g.b['hands']))

    def test_copper_thimble_scissors_and_crown(self):
        g=game();g.p['itens']=['ficha_cobre'];battle(g,['10','7'],['10','7']);g.interact('parar',{})
        self.assertEqual(g.p['fichas'],205)
        g=game();g.p['itens']=['dedal_costureira'];battle(g,['10','6','K'],['10','7']);g.interact('pedir',{})
        self.assertEqual(g.p['fichas'],191)
        g=game();g.p['itens']=['tesoura_destino'];battle(g,['10','6','K'],['10','7']);g.interact('pedir',{})
        self.assertEqual(g.total(g.b['hands'][0]),16);self.assertIn('scissors',g.b['used'])
        g=game();g.p['itens']=['coroa_22'];battle(g,['10','6','6'],['10','7']);g.interact('pedir',{})
        self.assertEqual(g.total(g.b['hands'][0]),21);self.assertEqual(g.p['fichas'],210)

    def test_insurance_throne_and_scepter(self):
        g=game();g.p['itens']=['manilha_sorte'];battle(g,['10','9'],['A','K'])
        self.assertEqual(g.s['phase'],'seguro');g.interact('segurar',{});self.assertEqual(g.p['fichas'],200)
        g=game();g.p['itens']=['trono_vazio'];battle(g,['10','6'],['10','9'])
        player_ids=set(g.p['deck']['cards']);g.interact('trono',{});self.assertEqual(g.total(g.b['hands'][0]),19)
        g.interact('parar',{});g.interact('continuar',{})
        self.assertEqual(set(g.p['deck']['draw']+g.p['deck']['discard']),player_ids)
        g=game();g.p['itens']=['cetro_sentencas'];battle(g,['10','8'],['10','9','K']);g.interact('parar',{})
        self.assertEqual(g.s['phase'],'revelacao');g.interact('cetro',{});self.assertEqual(g.p['fichas'],210)

    def test_deck_lens_never_exposes_rival_hole_card(self):
        g=game();g.p['itens']=['lente_escrivao'];battle(g,['10','6','4'],['10','9','2'])
        public=g.public();self.assertEqual(public['battle']['dealer'][1],{'oculta':True})
        self.assertIsNone(public['battle']['dealer_total']);self.assertNotIn('decks',public['battle'])
        self.assertEqual(public['deck']['counts'],{'4':1})

    def test_luck_multipliers_and_marks_are_capped(self):
        g=game();g.p['itens']=['forca_sete','bencao_reinos_v2','rosario_humildes','broche_prudencia']
        g.p['juramentos']=['fortuna','quinta','sete','humilde','ultima'];battle(g,['7','3','2','2','3'],['10','7'])
        h=g.b['hands'][0]
        h['cards'] += [g.draw(g.p['deck']) for _ in range(3)]
        g.b['all_in']=True
        self.assertEqual(g.multiplier(h),3)
        g=game();g.p['itens']=['manto_nobreza'];g.p['prestigio']=40;battle(g,['10','8'],['10','7'])
        self.assertEqual(g.p['fichas'],205)  # 200 + 15 tribute - 10 bet

    def test_oath_restrictions_and_consecration(self):
        g=game();g.p['juramentos']=['lamina','honra'];battle(g,['8','8','2','3'],['10','7'])
        self.assertNotIn('dividir',g.available());self.assertNotIn('desistir',g.available())
        g.p['consagrado']='lamina';self.assertIn('dividir',g.available())
        g=game();g.p['juramentos']=['ultima'];battle(g,['10','6'],['10','7'],bet=200)
        self.assertNotIn('desistir',g.available())

    def test_prestige_sources_and_mirror_do_not_turn_spending_into_income(self):
        g=game();g.p['itens']=['pacto_tirano','espelho_tirano'];g.p['prestigio']=20
        g.prestige(-3);self.assertEqual(g.p['prestigio'],14);self.assertEqual(g.p['fichas'],212)
        g.s.update(phase='evento',event='audiencia');g.interact('escolha',{'valor':'favor'})
        self.assertEqual(g.p['prestigio'],9);self.assertEqual(g.p['fichas'],272)
        g=game();g.p['itens']=['luvas_duelista'];g.p['juramentos']=['gloria','honra'];g.start_battle('elite','novica');g.b['double_win']=True;g.end_encounter(True)
        self.assertEqual(g.p['prestigio'],16);self.assertEqual(g.p['fichas'],260)

    def test_ferrugem_discount_and_deck_change(self):
        g=game();battle(g,['5','6','K'],['10','7','J','Q','K'],'ferrugem','boss')
        self.assertEqual(g.double_cost(g.b['hands'][0]),5)
        g.interact('dobrar',{});self.assertEqual(g.p['fichas'],225)
        g.interact('continuar',{})
        self.assertEqual(sum(c['valor'] in ('J','Q','K') for c in g.b['decks']['a']['cards'].values()),1)

    def test_sinos_blessing_and_gemeas_defense(self):
        g=game();battle(g,['10','9'],['2','2']+['2']*8,'sinos','boss');g.interact('parar',{})
        self.assertEqual(g.b['blessings'],1)
        g=game();battle(g,['10','8'],['10','6','10'],'gemeas','boss');g.interact('parar',{})
        self.assertEqual(g.total(g.b['dealer']),16);self.assertIn('a',g.b['sisters_saved'])
        g.interact('continuar',{});self.assertEqual(g.b['active'],'b');self.assertEqual(g.b['dealer_stop'],16)

    def test_cinzas_burn_and_ember(self):
        g=game();battle(g,['10','9'],['10','8','4'],'cinzas','boss');g.interact('parar',{});g.interact('continuar',{})
        self.assertFalse(any(c['valor']=='8' for c in g.b['decks']['a']['cards'].values()))
        self.assertTrue(any(c['temporaria']=='brasa' for c in g.p['deck']['cards'].values()))

    def test_astronomo_limits_and_eclipse(self):
        g=game();g.start_battle('boss','astronomo')
        limits=[]
        for round_no in range(4):
            g.b['rounds']=round_no;g.rules();limits.append((g.b['limit'],g.b['dealer_stop']))
        self.assertEqual(limits,[(19,16),(21,18),(23,20),(21,18)])
        g.b['rounds']=0;g.rules();g.p['deck']=ordered(g,['10','8']);g.b['decks']['a']=ordered(g,['10','6'])
        g.b['wins']=1;g.start_round(10);g.interact('parar',{});g.interact('continuar',{})
        self.assertTrue(g.b['eclipse_pending'])

    def test_cobrador_contracts_and_crown_all_three_acts(self):
        g=game();g.start_battle('boss','cobrador');g.s['offers']=['testemunhas','curta'];g.interact('contrato',{'valor':'testemunhas'})
        self.assertIsNotNone(g.public()['battle']['preview']);self.assertEqual(g.s['phase'],'aposta')
        g=game();g.p['juramentos']=['fortuna','gloria','dobrar','sete'];g.s.update(king_style='dobras',king_face='7');g.start_battle('boss','rei')
        for act in (1,2,3):
            for win in range(2):
                g.p['deck']=ordered(g,['A','K']);g.b['decks'][g.b['active']]=ordered(g,['10','8'])
                g.s['phase']='aposta';g.start_round(10)
                if g.s['phase']=='jogando':g.interact('parar',{})
                self.assertEqual(g.s['phase'],'resultado');g.interact('continuar',{})
            if act==1:
                self.assertEqual(g.s['phase'],'cobranca_real');g.interact('cobranca_real',{'valor':g.s['offers'][0]})
            elif act==2:
                self.assertEqual(g.s['phase'],'consagrar');g.interact('consagrar',{'valor':'dobrar'});g.interact('destino',{'valor':'governar'})
        self.assertEqual(g.s['phase'],'fim');self.assertTrue(g.s['victory']);self.assertIn('carta_real',g.s['unlocks'])

    def test_usurpar_crown_and_single_sacrifice(self):
        g=game();g.s.update(king_style='equilibrio',king_face='A');g.start_battle('boss','rei');g.b['act']=3;g.s['phase']='destino';g.interact('destino',{'valor':'usurpar'})
        g.p['deck']=ordered(g,['5','6']);g.b['decks']['a']=ordered(g,['10','8']);g.start_round(10)
        self.assertEqual(g.b['limit'],22);self.assertIn('coroa',g.available());g.interact('coroa',{'valor':11})
        self.assertEqual(g.total(g.b['hands'][0]),22);self.assertEqual(g.s['phase'],'resultado')
        g=game();g.p['itens']=['forca_sete','broche_prudencia'];battle(g,['5','6','2','3'],['10','7'])
        g.b['ending']='governar';g.interact('sacrificar',{'valor':'forca_sete'});g.interact('pedir',{})
        self.assertNotIn('sacrificar',g.available())


class SaveTests(unittest.TestCase):
    def test_stale_action_and_failed_save_rollback_rng_and_resources(self):
        with tempfile.TemporaryDirectory() as temp:
            m=AdventureMesa(Path(temp)/'save.json',seed=5)
            m.agir({'acao':'nova','nome':'Áurea','genero':'m','revisao':0})
            before=m.game.export();saved=m.save.read_bytes()
            with self.assertRaises(ValueError):m.agir({'acao':'juramento','valor':m.game.s['offers'][0],'revisao':0})
            with patch('count_queen.adventure.os.replace',side_effect=OSError('Full')):
                with self.assertRaises(OSError):m.agir({'acao':'juramento','valor':m.game.s['offers'][0],'revisao':1})
            self.assertEqual(m.game.export(),before);self.assertEqual(m.save.read_bytes(),saved)
            self.assertEqual(AdventureMesa(m.save).estado(),m.estado())

    def test_v1_migration_preserves_backup_and_refunds_active_wagers(self):
        old={'versao':1,'jogador':{'nome':'Antiga','genero':'m','fichas':100,'prestigio':4200,'itens':['forca_sete']},'rodada':{'fase':'oraculo','seguro':5},'maos':[{'aposta':40}]}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'save_visual.json';path.write_text(json.dumps(old))
            m=AdventureMesa(path)
            self.assertEqual(m.game.p['fichas'],145);self.assertEqual(m.game.p['prestigio'],42)
            self.assertEqual(m.game.p['itens'],['forca_sete']);self.assertEqual(m.game.s['phase'],'juramento')
            self.assertEqual(json.loads(path.with_name(path.name+'.v1.bak').read_text()),old)
            self.assertEqual(AdventureMesa(path).estado(),m.estado())
