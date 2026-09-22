import json
import unittest
from unittest.mock import patch

from count_queen.events import REGRAS_ENCONTROS, sortear_encontro, sortear_loja


class EventTests(unittest.TestCase):
    def test_nothing_before_first_eligible_round(self):
        with patch('count_queen.events.random.random', return_value=0) as rng:
            for tipo, (inicio, _, _) in REGRAS_ENCONTROS.items():
                self.assertFalse(sortear_encontro(tipo, inicio - 1, {}))
            rng.assert_not_called()

    def test_chance_boundaries_for_every_encounter(self):
        for tipo, (inicio, chance, _) in REGRAS_ENCONTROS.items():
            with self.subTest(tipo=tipo):
                with patch('count_queen.events.random.random', return_value=chance - 0.001):
                    self.assertTrue(sortear_encontro(tipo, inicio, {}))
                with patch('count_queen.events.random.random', return_value=chance):
                    self.assertFalse(sortear_encontro(tipo, inicio, {}))

    def test_guaranteed_encounter_after_maximum_failed_attempts(self):
        with patch('count_queen.events.random.random', return_value=1):
            for tipo, (inicio, _, limite) in REGRAS_ENCONTROS.items():
                with self.subTest(tipo=tipo):
                    state = {}
                    for rodada in range(inicio, inicio + limite - 1):
                        self.assertFalse(sortear_encontro(tipo, rodada, state))
                    self.assertTrue(sortear_encontro(tipo, inicio + limite - 1, state))
                    self.assertEqual(state['encontros'][tipo]['espera'], 0)

    def test_ineligible_rounds_do_not_advance_wait(self):
        state = {}
        self.assertFalse(sortear_encontro('desafio', 20, state, elegivel=False))
        self.assertEqual(state, {})

    def test_same_round_cannot_be_rerolled_after_reload(self):
        state = {}
        with patch('count_queen.events.random.random', return_value=1):
            self.assertFalse(sortear_encontro('andarilho', 10, state))
        state = json.loads(json.dumps(state))
        with patch('count_queen.events.random.random', return_value=0) as rng:
            self.assertFalse(sortear_encontro('andarilho', 10, state))
            rng.assert_not_called()
            self.assertTrue(sortear_encontro('andarilho', 11, state))

    def test_shops_can_appear_outside_old_multiples(self):
        with patch('count_queen.events.random.random', return_value=0):
            self.assertEqual(sortear_loja(4, {}), 'emporio')
            self.assertEqual(sortear_loja(7, {'ultima_loja': 'emporio'}), 'sacrario')

    def test_shop_priority_alternates(self):
        state = {}
        with patch('count_queen.events.random.random', return_value=0):
            self.assertEqual([sortear_loja(r, state) for r in range(5, 9)],
                             ['emporio', 'sacrario', 'emporio', 'sacrario'])

    def test_only_one_shop_per_round_even_after_reload(self):
        state = {}
        with patch('count_queen.events.random.random', return_value=0):
            self.assertEqual(sortear_loja(5, state), 'emporio')
            state = json.loads(json.dumps(state))
            self.assertIsNone(sortear_loja(5, state))
            self.assertEqual(sortear_loja(6, state), 'sacrario')

    def test_unlucky_run_still_has_every_encounter(self):
        state = {}
        seen = set()
        with patch('count_queen.events.random.random', return_value=1):
            for rodada in range(1, 61):
                seen.add(sortear_loja(rodada, state))
                for tipo in ('andarilho', 'desafio'):
                    if sortear_encontro(tipo, rodada, state):
                        seen.add(tipo)
        self.assertTrue(set(REGRAS_ENCONTROS).issubset(seen))
