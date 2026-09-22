import contextlib
import io
import unittest
from unittest.mock import patch

from count_queen.campaign import atualizar_coroacao, multiplicador_lucro, custo_afinidade, aposta_desafio
from count_queen.logic import calcular_prestigio_ganho, obter_fator_risco
from count_queen.models import Jogador, Mao, Carta, Baralho, Dealer
from count_queen.ui import terminal


class CampaignTests(unittest.TestCase):
    def test_crown_requires_three_wins_and_pushes_do_not_count(self):
        player = Jogador('Ana', prestigio=10000)
        self.assertEqual(atualizar_coroacao(player), 'inicio')
        for result in [1, 0, -1, 1, 0]:
            atualizar_coroacao(player, result)
        self.assertFalse(player.coroacao_concluida)
        self.assertEqual(atualizar_coroacao(player, 1), 'vitoria')

    def test_failed_crown_can_be_retried(self):
        player = Jogador('Ana', prestigio=-10000, caminho='tirania')
        atualizar_coroacao(player)
        for _ in range(3):
            outcome = atualizar_coroacao(player, -1)
        self.assertEqual(outcome, 'recuo')
        self.assertEqual(player.prestigio, -9000)
        self.assertFalse(player.coroacao_ativa)
        player.prestigio = -10000
        self.assertEqual(atualizar_coroacao(player), 'inicio')

    def test_wrong_direction_does_not_unlock_crown(self):
        self.assertIsNone(atualizar_coroacao(Jogador('Ana', prestigio=10000, caminho='tirania')))

    def test_bonus_stacking_is_bounded_even_for_old_affinities(self):
        player = Jogador('Ana', itens=['forca_sete', 'bencao_reinos_v2'], afinidades={'7': 100})
        hand = Mao()
        for suit, rank in [('Copas', '7'), ('Ouros', '2'), ('Paus', '3'), ('Espadas', '4')]:
            hand.adicionar_carta(Carta(suit, rank))
        self.assertEqual(multiplicador_lucro(player, hand), 3)

    def test_affinity_price_depends_on_chosen_card_and_wealth(self):
        player = Jogador('Ana', afinidades={'A': 4})
        self.assertLess(custo_afinidade(player, '7'), custo_afinidade(player, 'A'))
        player.fichas = 1000000
        self.assertEqual(custo_afinidade(player, '7'), 20000)

    def test_challenge_scales_with_wealth(self):
        self.assertEqual(aposta_desafio(Jogador('Ana', fichas=100)), 100)
        self.assertEqual(aposta_desafio(Jogador('Ana', fichas=1000000)), 100000)

    def test_oracle_skips_initial_deal_and_is_once_per_round(self):
        player = Jogador('Ana', itens=['caleidoscopio_acaso'])
        deck = Baralho()
        with patch('builtins.input', return_value='1') as choose, \
             patch('count_queen.models.limpar_tela'), contextlib.redirect_stdout(io.StringIO()):
            player.pedir_carta(deck)
            player.pedir_carta(deck)
            choose.assert_not_called()
            player.pedir_carta(deck)
            player.pedir_carta(deck)
            choose.assert_called_once()
            self.assertEqual(len(deck.cartas), 48)
            player.limpar_maos()
            self.assertFalse(player._oraculo_usado)

    def test_risk_is_based_on_balance_before_round_not_payout(self):
        player = Jogador('Ana')
        player.limpar_maos()
        hand = player.maos[0]
        hand.aposta = 200
        initial = calcular_prestigio_ganho(player, hand, 25)
        player.fichas = 1000000
        self.assertEqual(calcular_prestigio_ganho(player, hand, 25), initial)
        self.assertEqual(obter_fator_risco(200, 200), 3.5)

    def test_regent_draws_at_seventeen(self):
        dealer = Dealer('Regente', 18)
        for rank in ['10', '7']:
            dealer.maos[0].adicionar_carta(Carta('Paus', rank))
        deck = Baralho()
        deck.cartas = [Carta('Paus', '2')]
        dealer.jogar(deck)
        self.assertEqual(dealer.maos[0].valor, 19)

    def test_fast_mode_skips_only_pauses_and_delays(self):
        with patch.object(terminal, 'MODO_RAPIDO', True), \
             patch('builtins.input') as input_mock, patch('time.sleep') as sleep:
            terminal.pausar()
            terminal.aguardar(2)
            input_mock.assert_not_called()
            sleep.assert_not_called()
