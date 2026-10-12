import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from count_queen.models import Baralho, Carta, Jogador
from count_queen.rounds import Rodada
from count_queen.web import Mesa, criar_servidor


def deck(values):
    baralho = Baralho()
    baralho.cartas = [Carta('Copas', v) for v in reversed(values)]
    return baralho


def start(values, jogador=None, aposta=20):
    rodada = Rodada(jogador or Jogador('Áurea'))
    with patch('count_queen.rounds.Baralho', return_value=deck(values)), patch.object(Baralho, 'embaralhar'):
        rodada.agir('apostar', aposta)
    return rodada


class VisualRoundTests(unittest.TestCase):
    def test_natural_and_push_payouts(self):
        for cards, expected in [(['A','7','K','7','7'],230),
                                (['A','A','K','K'],200),
                                (['10','A','9','K'],180)]:
            with self.subTest(cards=cards):
                r = start(cards)
                self.assertEqual(r.fase, 'resultado')
                self.assertEqual(r.jogador.fichas, expected)

    def test_invalid_bets_leave_balance_and_phase_unchanged(self):
        r = Rodada(Jogador('Áurea'))
        for value in [0,-10,201,1.5,True,'10',None,float('inf')]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                r.agir('apostar', value)
            self.assertEqual(r.jogador.fichas,200)
            self.assertEqual(r.fase,'aposta')

    def test_double_draws_once_and_settles_once(self):
        r=start(['5','10','6','7','10'])
        r.agir('dobrar')
        self.assertEqual(r.jogador.maos[0].valor,21)
        self.assertEqual(r.jogador.maos[0].aposta,40)
        self.assertEqual(r.jogador.fichas,240)
        with self.assertRaises(ValueError):
            r.agir('dobrar')
        self.assertEqual(r.jogador.fichas,240)

    def test_unaffordable_actions_are_rejected(self):
        r=start(['8','10','8','7'],aposta=200)
        self.assertNotIn('dividir',r.acoes())
        self.assertNotIn('dobrar',r.acoes())
        with self.assertRaises(ValueError):
            r.agir('dividir')
        self.assertEqual(len(r.jogador.maos),1)

    def test_split_twenty_one_pays_one_to_one(self):
        r=start(['A','10','A','7','K','Q'])
        r.agir('dividir')
        self.assertEqual(r.fase,'resultado')
        self.assertTrue(all(not m.e_blackjack for m in r.jogador.maos))
        self.assertEqual(r.jogador.fichas,240)

    def test_free_resplits_stop_at_four_hands(self):
        r=start(['8','10','8','7']+['8']*6,Jogador('Áurea',itens=['joias_gemeas']),100)
        r.agir('dividir')
        r.agir('dividir')
        r.agir('dividir')
        self.assertEqual(r.jogador.fichas,0)
        self.assertEqual(len(r.jogador.maos),4)
        self.assertNotIn('dividir',r.acoes())
        for _ in range(4):
            r.agir('parar')
        self.assertEqual(r.fase,'resultado')

    def test_surrender_and_tyrant_mirror(self):
        r=start(['10','10','6','7'],Jogador('Áurea',itens=['espelho_tirano'],caminho='tirania'))
        r.agir('desistir')
        self.assertEqual(r.jogador.fichas,200)
        self.assertEqual(r.jogador.prestigio,5)
        self.assertEqual(r.resultados[0]['retorno'],10)
        self.assertEqual(r.jogador.desistencias_consecutivas,1)

    def test_insurance_and_dealer_natural(self):
        for action, balance in [('segurar',200),('recusar_seguro',180)]:
            r=start(['10','A','9','K'],Jogador('Áurea',itens=['manilha_sorte']))
            self.assertEqual(r.fase,'seguro')
            r.agir(action)
            self.assertEqual(r.jogador.fichas,balance)
            self.assertEqual(r.fase,'resultado')

    def test_oracle_double_uses_chosen_card_once(self):
        r=start(['5','10','6','7','2','3','K'],Jogador('Áurea',itens=['caleidoscopio_acaso']))
        r.agir('dobrar')
        self.assertEqual(r.fase,'oraculo')
        self.assertEqual(r.jogador.fichas,160)
        r.agir('escolher',0)
        self.assertEqual(r.fase,'resultado')
        self.assertEqual(r.jogador.maos[0].valor,21)
        self.assertEqual(r.jogador.fichas,240)

    def test_coronation_and_regent_limit(self):
        j=Jogador('Áurea',prestigio=10000,coroacao_ativa=True,coroacao_vitorias=2)
        r=start(['10','10','9','7','2'],j)
        self.assertEqual(r.dealer.limite,18)
        r.agir('parar')
        self.assertEqual(r.dealer.maos[0].valor,19)
        self.assertFalse(j.coroacao_concluida)
        r.agir('continuar')
        with patch('count_queen.rounds.Baralho',return_value=deck(['A','10','K','8'])), patch.object(Baralho,'embaralhar'):
            r.agir('apostar',20)
        self.assertTrue(j.coroacao_concluida)
        r.agir('continuar')
        self.assertEqual(r.acoes(),[])


class VisualSaveTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'visual.json'
        self.mesa=Mesa(self.path)
        self.mesa.agir({'acao':'nova','revisao':0,'nome':'Áurea','genero':'m'})

    def act(self, action, value=None):
        self.mesa.agir({'acao':action,'valor':value,'revisao':self.mesa.revisao})

    def test_hidden_card_and_deck_never_exposed_by_api(self):
        with patch('count_queen.rounds.Baralho',return_value=deck(['10','9','6','K'])), patch.object(Baralho,'embaralhar'):
            self.act('apostar',20)
        state=self.mesa.estado()
        self.assertEqual(state['dealer'][1],{'oculta':True})
        self.assertIsNone(state['dealer_valor'])
        self.assertNotIn('baralho',state)
        before=self.mesa.exportar()
        resumed=Mesa(self.path)
        self.assertEqual(resumed.exportar(),before)
        self.assertEqual(resumed.estado(),state)
        resumed.agir({'acao':'parar','revisao':resumed.revisao})
        self.assertEqual(resumed.estado()['dealer'][1]['valor'],'K')
        self.assertEqual(resumed.contador,1)

    def test_restart_during_oracle_keeps_choice_in_deck(self):
        self.mesa.rodada.jogador.itens=['caleidoscopio_acaso']
        with patch('count_queen.rounds.Baralho',return_value=deck(['5','10','6','7','2','3','K'])), patch.object(Baralho,'embaralhar'):
            self.act('apostar',20)
        self.act('dobrar')
        resumed=Mesa(self.path)
        resumed.agir({'acao':'escolher','valor':0,'revisao':resumed.revisao})
        self.assertEqual(resumed.rodada.jogador.fichas,240)
        self.assertTrue(resumed.rodada.jogador._oraculo_usado)

    def test_stale_requests_do_not_mutate_or_charge_twice(self):
        before=self.mesa.exportar()
        with self.assertRaises(ValueError):
            self.mesa.agir({'acao':'apostar','valor':20,'revisao':0})
        self.assertEqual(self.mesa.exportar(),before)

    def test_failed_disk_write_rolls_back_memory_and_preserves_save(self):
        before=self.mesa.exportar()
        saved=self.path.read_bytes()
        with patch('count_queen.web.os.replace',side_effect=OSError('Disk full')):
            with self.assertRaises(OSError):
                self.act('apostar',20)
        self.assertEqual(self.mesa.exportar(),before)
        self.assertEqual(self.path.read_bytes(),saved)
        self.assertEqual(list(self.path.parent.iterdir()),[self.path])

    def test_new_journey_cannot_overwrite_active_game(self):
        with self.assertRaises(ValueError):
            self.mesa.agir({'acao':'nova','nome':'Outro','revisao':self.mesa.revisao})
        self.assertEqual(self.mesa.rodada.jogador.nome,'Áurea')

    def test_http_state_actions_and_validation(self):
        server=criar_servidor(self.mesa,port=0)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        try:
            with urlopen(base+'/api/estado') as response:
                self.assertEqual(json.load(response)['jogador']['nome'],'Áurea')
            payload=json.dumps({'acao':'apostar','valor':10,'revisao':self.mesa.revisao}).encode()
            request=Request(base+'/api/acao',data=payload,headers={'Content-Type':'application/json'})
            with urlopen(request) as response:
                self.assertEqual(response.status,200)
            with self.assertRaises(HTTPError) as stale:
                urlopen(request)
            self.assertEqual(stale.exception.code,400)
            request=Request(base+'/api/acao',data=payload,headers={'Content-Type':'application/json','Origin':'https://example.com'})
            with self.assertRaises(HTTPError) as foreign:
                urlopen(request)
            self.assertEqual(foreign.exception.code,403)
            with self.assertRaises(HTTPError) as private:
                urlopen(base+'/save_visual.json')
            self.assertEqual(private.exception.code,404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__=='__main__':
    unittest.main()
