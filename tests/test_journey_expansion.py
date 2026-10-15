"""Regression coverage for origins, tactical relics, recurring choices and receipts."""
import json
import tempfile
import unittest
from pathlib import Path
from count_queen.adventure import Adventure, AdventureMesa
from count_queen import stories
from test_adventure import game, battle, ordered


def restore(g):
    clone=Adventure();clone.restore(json.loads(json.dumps(g.export())))
    return clone


class OriginsTests(unittest.TestCase):
    def test_locked_origin_is_rejected_before_changes(self):
        g=Adventure(1);before=g.export()
        with self.assertRaises(ValueError):g.new('A','m','herdeiro')
        self.assertEqual(g.export(),before)

    def test_three_origin_costs_and_decks(self):
        for origin in ('herdeiro','exilada','trapaceiro'):
            g=Adventure(1);g.unlock(origin);g.new('A','m',origin)
            self.assertEqual(len(g.p['deck']['cards']),52)
            self.assertEqual(restore(g).public(),g.public())
            if origin=='herdeiro':
                self.assertEqual(g.p['origin_debt'],120);self.assertEqual(g.p['fichas'],140)
            elif origin=='exilada':
                self.assertFalse(any(c['valor']=='K' for c in g.p['deck']['cards'].values()))
                g.start_battle('mesa','mesa');self.assertEqual(g.b['blessings'],1)
            else:
                g.enter({'type':'loja'});price=g.shop_price('broche_prudencia')
                g.p['origem']='viajante';self.assertEqual(price,round(g.shop_price('broche_prudencia')*1.15))

    def test_unlocks_persist_between_journeys(self):
        g=game();battle(g,['8','8','2','3'],['10','7'])
        g.interact('dividir',{});self.assertIn('origem_trapaceiro',g.s['unlocks'])
        g.end_encounter(True);self.assertIn('origem_herdeiro',g.s['unlocks'])
        g.finish(False,'Fim');self.assertIn('origem_exilada',g.s['unlocks'])
        g=restore(g);g.new('B','h','herdeiro');self.assertEqual(g.p['origem'],'herdeiro')

    def test_old_save_gets_defaults_without_reroll(self):
        g=game();payload=g.export();rng=payload['random']
        for k in ('origem','origin_debt','stories','story_log','reserved'):payload['player'].pop(k)
        payload.pop('effects');payload.pop('new_unlocks')
        clone=Adventure();clone.restore(payload)
        self.assertEqual(clone.p['origem'],'viajante');self.assertEqual(clone.rng.getstate(),rng)
        self.assertEqual(clone.s['maps'],g.s['maps'])


class TacticalRelicsTests(unittest.TestCase):
    def test_pocket_conserves_card_across_reload_and_next_round(self):
        g=game();g.p['itens']=['bolso_falso']
        battle(g,['5','5','7','A','3','2'],['10','7','10','7'])
        g.interact('pedir',{});cid=g.b['hands'][0]['cards'][-1]['id']
        g.interact('guardar',{});self.assertEqual(g.p['reserved'],cid)
        self.assertNotIn('guardar',g.available());self.assertNotIn('dobrar',g.available())
        self.assertNotIn(cid,g.p['deck']['draw']+g.p['deck']['discard'])
        g=restore(g);g.interact('parar',{});g.interact('continuar',{})
        g.interact('apostar',{'valor':10})
        self.assertEqual(g.b['hands'][0]['cards'][0]['id'],cid)
        self.assertIsNone(g.p['reserved']);self.assertTrue(g.b['hands'][0]['no_natural'])

    def test_pocket_cannot_take_borrowed_or_temporary_card(self):
        g=game();g.p['itens']=['bolso_falso'];battle(g,['2','3','4'],['10','7'])
        g.interact('pedir',{});c=g.b['hands'][0]['cards'][-1];c['temporaria']='brasa'
        self.assertNotIn('guardar',g.available());c['temporaria']=None;c['id']='borrowed'
        self.assertNotIn('guardar',g.available())

    def test_reserved_card_cannot_be_removed_from_workshop(self):
        g=game();g.p['reserved']=next(iter(g.p['deck']['cards']));g.s.update(phase='oficina',workshop_paid=False)
        with self.assertRaises(ValueError):g.interact('remover',{'carta':g.p['reserved']})

    def test_balance_moves_exact_card_once_without_new_bet(self):
        g=game();g.p['itens']=['balanca_carrasco'];battle(g,['8','8','2','3','4'],['10','7'])
        g.interact('dividir',{});before=g.p['fichas'];ids=[c['id'] for h in g.b['hands'] for c in h['cards']]
        cid=g.b['hands'][0]['cards'][-1]['id']
        for data in ({'carta':cid,'destino':0},{'carta':'missing','destino':1},{'carta':cid,'destino':True}):
            with self.assertRaises(ValueError):g.interact('transferir',data)
        g.interact('transferir',{'carta':cid,'destino':1})
        self.assertEqual([len(h['cards']) for h in g.b['hands']],[1,3]);self.assertEqual(g.p['fichas'],before)
        self.assertCountEqual(ids,[c['id'] for h in g.b['hands'] for c in h['cards']]);self.assertNotIn('transferir',g.available())

    def test_last_word_reveals_then_draws_once_without_redrawing_dealer(self):
        g=game();g.p['itens']=['ultima_palavra'];battle(g,['7','7','6','2'],['10','8','3'])
        g.interact('parar',{});self.assertEqual(g.s['phase'],'ultima_palavra')
        self.assertEqual(g.public()['battle']['dealer_total'],18)
        dealer=list(g.b['dealer']);g=restore(g);g.interact('comprar_final',{})
        self.assertEqual(g.s['phase'],'resultado');self.assertEqual(g.b['dealer'],dealer)
        self.assertEqual(g.b['result']['fichas'],10);self.assertEqual(g.b['rounds'],1)
        with self.assertRaises(ValueError):g.interact('comprar_final',{})
        self.assertEqual(g.b['rounds'],1)

    def test_last_word_scissors_and_oracle_interaction(self):
        g=game();g.p['itens']=['ultima_palavra','tesoura_destino','caleidoscopio_acaso']
        battle(g,['10','8','10','2'],['10','7','5']);g.interact('parar',{});g.interact('comprar_final',{})
        self.assertEqual(g.s['phase'],'resultado');self.assertEqual(len(g.b['hands'][0]['cards']),2)
        self.assertIn('scissors',g.b['used']);self.assertNotIn('oracle',g.b['round_used']);self.assertEqual(g.b['rounds'],1)

    def test_last_word_crown_rescue(self):
        g=game();g.p['itens']=['ultima_palavra','coroa_22'];battle(g,['10','8','4'],['10','9'])
        g.interact('parar',{});g.interact('comprar_final',{})
        self.assertEqual(g.total(g.b['hands'][0]),21);self.assertEqual(g.b['result']['score'],1)

    def test_last_word_rejected_for_natural_double_and_split(self):
        for ranks,action in [(['A','K','2'],None),(['5','5','6'],'dobrar'),(['8','8','2','3','4'],'dividir')]:
            g=game();g.p['itens']=['ultima_palavra'];battle(g,ranks,['10','7'])
            if action:g.interact(action,{})
            while g.s['phase']=='jogando':g.interact('parar',{})
            self.assertEqual(g.s['phase'],'resultado')

    def test_scepter_is_resolved_before_last_word(self):
        g=game();g.p['itens']=['cetro_sentencas','ultima_palavra'];battle(g,['7','7','6'],['10','7','2'])
        g.interact('parar',{});self.assertEqual(g.s['phase'],'revelacao')
        g.interact('cetro',{});self.assertEqual(g.s['phase'],'ultima_palavra')
        g.interact('aceitar_resultado',{});self.assertEqual(g.b['result']['score'],-1)
        self.assertNotIn('last_word',g.b['used'])


class ConsequenceTests(unittest.TestCase):
    def test_receipt_matches_cap_debt_and_actual_credit(self):
        g=game();g.p.update(itens=['forca_sete','rosario_humildes'],juramentos=['sete','fortuna'],origin_debt=120.,debt=225.)
        battle(g,['7','10'],['10','6','10']);g.interact('parar',{})
        c=g.b['result']['hands'][0]['calculation']
        self.assertEqual(c['multiplier'],2.9);self.assertEqual(c['profit'],29)
        self.assertEqual(c['payments'],{'family':7.25,'oath':10.88,'received':10.87})
        self.assertAlmostEqual(g.b['result']['fichas'],10.87)
        self.assertAlmostEqual(c['credited'],20.87)
        g.p['afinidades']={'7':5};self.assertEqual(g.multiplier(g.b['hands'][0]),3)

    def scene(self,g,key,region):
        g.s.update(phase='evento',event='historia:'+key,region=region)

    def test_messenger_betrayal_persists_and_changes_final_choices(self):
        g=game();self.scene(g,'mensageira',0);g.interact('escolha',{'valor':'escoltar'})
        self.assertTrue(g.p['prepared']);g=restore(g)
        self.scene(g,'mensageira',1);g.interact('escolha',{'valor':'vender'})
        g=restore(g);self.scene(g,'mensageira',2)
        self.assertEqual([o['id'] for o in stories.scene(g)['options']],['reparar','abandonar'])
        self.assertEqual(len(g.p['story_log']),2)
        g.interact('escolha',{'valor':'reparar'});self.assertEqual(g.p['stories']['mensageira']['stage'],3)

    def test_loyal_messenger_gives_relic_and_duplicate_compensation(self):
        for owned in (False,True):
            g=game();g.p['stories']['mensageira']={'stage':2,'choice':'proteger'}
            if owned:g.p['itens']=['ultima_palavra']
            self.scene(g,'mensageira',2);before=g.p['fichas'];g.interact('escolha',{'valor':'legado'})
            self.assertEqual(g.p['itens'].count('ultima_palavra'),1)
            self.assertEqual(g.p['fichas']-before,60 if owned else 0)

    def test_forgery_cannot_exceed_deck_limit_and_disabled_choice_rolls_back(self):
        with tempfile.TemporaryDirectory() as t:
            mesa=AdventureMesa(Path(t)/'save.json');mesa.game=game();g=mesa.game
            while len(g.p['deck']['cards'])<80:g.add_card('2')
            g.p['stories']['falsificadora']={'stage':1};self.scene(g,'falsificadora',1)
            before=g.export();self.assertFalse(stories.scene(g)['options'][0]['enabled'])
            with self.assertRaises(ValueError):mesa.agir({'acao':'escolha','valor':'carta','revisao':0})
            self.assertEqual(g.export(),before)

    def test_story_waits_until_later_region_and_debt_survives_refusal(self):
        g=game();g.p['origem']='herdeiro';self.scene(g,'credor',0)
        g.interact('escolha',{'valor':'emprestar'});self.assertEqual(g.p['origin_debt'],90)
        for _ in range(20):self.assertNotEqual(stories.select_story(g),'credor')
        g.s['region']=1;self.assertEqual(stories.select_story(g),'credor')
        self.scene(g,'credor',1);g.interact('escolha',{'valor':'seguir'})
        self.assertEqual(g.p['origin_debt'],90);self.assertEqual(g.p['stories']['credor']['stage'],3)
        g.receive_profit(20);self.assertEqual(g.p['origin_debt'],85)

    def test_creditor_reacts_to_origin_debt_without_exposing_cards(self):
        g=game();g.p['origin_debt']=120;g.start_battle('boss','cobrador')
        g.interact('contrato',{'valor':g.s['offers'][0]});g.interact('apostar',{'valor':10})
        public=g.public()['battle'];self.assertIn('120',public['presence']['speech'])
        if not public['reveal']:self.assertTrue(any(c.get('oculta') for c in public['dealer']))

if __name__=='__main__':unittest.main()
