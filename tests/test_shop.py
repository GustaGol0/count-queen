import contextlib
import io
import unittest
from unittest.mock import patch

from count_queen.models import Jogador
from count_queen.ui.view import mostrar_loja


class ShopTests(unittest.TestCase):
    def test_invalid_input_does_not_reroll_offers(self):
        offers = [('forca_sete', {'nome': 'Força do Sete', 'preco': 777, 'descricao': 'Teste'})]
        with patch('count_queen.ui.view.random.sample', return_value=offers) as sample, \
             patch('count_queen.ui.view.random.choice', side_effect=['forca_sete', .15]) as choice, \
             patch('count_queen.ui.view.limpar_tela'), \
             patch('count_queen.ui.view.pausar'), \
             patch('builtins.input', side_effect=['erro', 's']), \
             contextlib.redirect_stdout(io.StringIO()):
            mostrar_loja(Jogador('Ana'), {})
        sample.assert_called_once()
        self.assertEqual(choice.call_count, 2)

    def test_affinity_purchase_charges_selected_card(self):
        player = Jogador('Ana', fichas=1000, afinidades={'A': 4})
        state = {'contador_rodadas': 5}
        with patch('count_queen.ui.view.limpar_tela'), \
             patch('count_queen.ui.view.pausar'), \
             patch('count_queen.ui.view.salvar_jogador') as save, \
             patch('builtins.input', side_effect=['e', '7', 's', 's']), \
             contextlib.redirect_stdout(io.StringIO()):
            mostrar_loja(player, state)
        self.assertEqual(player.fichas, 850)
        self.assertEqual(player.afinidades['7'], 1)
        save.assert_called_once_with(state, player, 5)

    def test_maxed_affinity_cannot_be_purchased(self):
        player = Jogador('Ana', fichas=1000, afinidades={'A': 5})
        with patch('count_queen.ui.view.limpar_tela'), \
             patch('count_queen.ui.view.pausar'), \
             patch('builtins.input', side_effect=['e', 'A', 's']), \
             contextlib.redirect_stdout(io.StringIO()):
            mostrar_loja(player, {})
        self.assertEqual(player.fichas, 1000)
        self.assertEqual(player.afinidades['A'], 5)
