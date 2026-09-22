import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from count_queen.game import jogar_blackjack
from count_queen.models import Baralho, Carta, Dealer, Jogador, Mao
from count_queen.persistence import carregar_estado_do_jogo, salvar_estado_do_jogo


class GameTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'save.json'
        patcher = patch('count_queen.persistence.SAVE_FILENAME', self.path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def play(self, player, cards, answers, state=None):
        deck = Baralho()
        deck.cartas = [Carta('Copas', value) for value in reversed(cards)]
        if state is None:
            state = {'jogador_atual': None, 'herois_caidos': [], 'herois_verdadeiros': []}
        with patch('count_queen.game.menu_principal', side_effect=[(player, state), (None, None)]), \
             patch('count_queen.game.Baralho', return_value=deck), \
             patch.object(deck, 'embaralhar'), \
             patch('count_queen.game.limpar_tela'), \
             patch('count_queen.game.time.sleep'), \
             patch('count_queen.game.random.random', return_value=1), \
             patch('builtins.input', side_effect=answers), \
             contextlib.redirect_stdout(io.StringIO()):
            jogar_blackjack()
        return carregar_estado_do_jogo()

    def test_save_on_exit_before_first_round(self):
        state = self.play(Jogador('Rainha Áurea'), [], ['s'])
        self.assertEqual(state['jogador_atual']['nome'], 'Rainha Áurea')
        self.assertEqual(state['contador_rodadas'], 0)

    def test_dealer_blackjack_saves_and_ends_bankrupt_game(self):
        state = self.play(Jogador('Ana'), ['10', 'A', '9', 'K'], ['j', '200', '', ''])
        self.assertIsNone(state['jogador_atual'])
        self.assertEqual(state['herois_caidos'], ['Ana'])
        self.assertEqual(state['contador_rodadas'], 1)

    def test_insurance_returns_three_times_its_cost(self):
        state = self.play(Jogador('Ana', itens=['manilha_sorte']),
                          ['10', 'A', '9', 'K'], ['j', '100', 's', '', 's'])
        self.assertEqual(state['jogador_atual']['fichas'], 200)

    def test_natural_beats_three_card_twenty_one(self):
        state = self.play(Jogador('Ana'), ['A', '7', 'K', '7', '7'], ['j', '100', '', 's'])
        self.assertEqual(state['jogador_atual']['fichas'], 350)

    def test_natural_pays_three_to_two_when_dealer_busts(self):
        state = self.play(Jogador('Ana'), ['A', '10', 'K', '6', 'K'], ['j', '100', '', 's'])
        self.assertEqual(state['jogador_atual']['fichas'], 350)

    def test_two_naturals_push(self):
        state = self.play(Jogador('Ana'), ['A', 'A', 'K', 'K'], ['j', '100', '', 's'])
        self.assertEqual(state['jogador_atual']['fichas'], 200)

    def test_split_twenty_one_is_not_natural(self):
        hand = Mao()
        hand.veio_de_split = True
        hand.adicionar_carta(Carta('Copas', 'A'))
        hand.adicionar_carta(Carta('Paus', 'K'))
        self.assertEqual(hand.valor, 21)
        self.assertFalse(hand.e_blackjack)

    def test_empty_deck_does_not_trap_dealer(self):
        deck = Baralho()
        deck.cartas = []
        Dealer().jogar(deck)

    def test_failed_save_keeps_previous_file(self):
        salvar_estado_do_jogo({'nome': 'Áurea'})
        with patch('count_queen.persistence.os.replace', side_effect=OSError('falha')):
            with self.assertRaises(OSError):
                salvar_estado_do_jogo({'nome': 'Novo'})
        self.assertEqual(carregar_estado_do_jogo(), {'nome': 'Áurea'})
        self.assertEqual(list(Path(self.temp.name).iterdir()), [self.path])

    def test_new_game_resets_rounds_and_encounters_preserving_legends(self):
        from count_queen.ui.view import menu_principal
        salvar_estado_do_jogo({'jogador_atual': {'nome': 'Antigo'},
                              'contador_rodadas': 80, 'encontros': {'andarilho': {}},
                              'ultima_loja': 'emporio', 'herois_caidos': ['Caído'],
                              'herois_verdadeiros': ['Lenda']})
        with patch('builtins.input', side_effect=['2', 'Nova', 'm', '']), \
             patch('count_queen.ui.view.limpar_tela'), \
             contextlib.redirect_stdout(io.StringIO()):
            player, state = menu_principal()
        self.assertEqual(player.nome, 'Nova')
        self.assertEqual(state['contador_rodadas'], 0)
        self.assertEqual(state['encontros'], {})
        self.assertNotIn('ultima_loja', state)
        self.assertEqual(state['herois_caidos'], ['Caído'])
        self.assertEqual(state['herois_verdadeiros'], ['Lenda'])
        self.assertEqual(carregar_estado_do_jogo(), state)

    def test_continue_preserves_rounds_and_encounters(self):
        from count_queen.ui.view import menu_principal
        state = {'jogador_atual': {'nome': 'Ana', 'fichas': 400},
                 'contador_rodadas': 30, 'encontros': {'andarilho': {'espera': 4, 'ultima_tentativa': 30}}}
        salvar_estado_do_jogo(state)
        with patch('builtins.input', return_value='1'), \
             patch('count_queen.ui.view.limpar_tela'), \
             patch('count_queen.ui.view.time.sleep'), \
             contextlib.redirect_stdout(io.StringIO()):
            player, resumed = menu_principal()
        self.assertEqual(resumed, state)
        self.assertEqual(player.fichas, 400)

    def test_shop_opens_after_dealer_blackjack(self):
        state = {'contador_rodadas': 9,
                 'encontros': {'emporio': {'espera': 7, 'ultima_tentativa': 9}}}
        with patch('count_queen.game.mostrar_loja') as shop:
            saved = self.play(Jogador('Ana'), ['10', 'A', '9', 'K'],
                              ['j', '10', '', '', 's'], state)
        shop.assert_called_once()
        self.assertEqual(saved['contador_rodadas'], 10)
        self.assertEqual(saved['encontros']['emporio']['espera'], 0)

    def test_sanctuary_opens_and_changes_are_saved(self):
        state = {'contador_rodadas': 18,
                 'encontros': {'sacrario': {'espera': 14, 'ultima_tentativa': 18}}}
        def purchase(player, state):
            player.caminho = 'tirania'
            player.prestigio = -250
            player.itens.append('pacto_tirano')
        with patch('count_queen.game.mostrar_sacrario_do_segredo', side_effect=purchase) as shop:
            saved = self.play(Jogador('Ana'), ['10', '10', '8', '8'],
                              ['j', '10', 's', '', '', 's'], state)
        shop.assert_called_once()
        self.assertEqual(saved['jogador_atual']['caminho'], 'tirania')
        self.assertIn('pacto_tirano', saved['jogador_atual']['itens'])

    def test_wanderer_gambling_loss_ends_game_immediately(self):
        state = {'contador_rodadas': 24,
                 'encontros': {'andarilho': {'espera': 19, 'ultima_tentativa': 24}}}
        with patch('count_queen.game.random.choice', return_value={'texto': 'Aposta', 'tipo': 'aposta'}):
            saved = self.play(Jogador('Ana', fichas=500), ['10', '10', '8', '8'],
                              ['j', '10', 's', '', 's', '', ''], state)
        self.assertIsNone(saved['jogador_atual'])
        self.assertEqual(saved['herois_caidos'], ['Ana'])
        self.assertEqual(saved['contador_rodadas'], 25)

    def test_wanderer_gambling_is_saved(self):
        state = {'contador_rodadas': 24,
                 'encontros': {'andarilho': {'espera': 19, 'ultima_tentativa': 24}}}
        with patch('count_queen.game.random.choice', return_value={'texto': 'Aposta', 'tipo': 'aposta'}):
            saved = self.play(Jogador('Ana', fichas=600), ['10', '10', '8', '8'],
                              ['j', '10', 's', '', 's', '', 's'], state)
        self.assertEqual(saved['jogador_atual']['fichas'], 100)
        self.assertEqual(saved['encontros']['andarilho']['espera'], 0)

    def test_wanderer_unlocks_crown_instead_of_skipping_finale(self):
        state = {'contador_rodadas': 24,
                 'encontros': {'andarilho': {'espera': 19, 'ultima_tentativa': 24}}}
        offer = {'texto': 'Troca', 'fichas': -200, 'prestigio': 100}
        with patch('count_queen.game.random.choice', return_value=offer):
            saved = self.play(Jogador('Ana', fichas=500, prestigio=9900), ['10', '10', '8', '8'],
                              ['j', '10', 's', '', 's', '', 's'], state)
        self.assertTrue(saved['jogador_atual']['coroacao_ativa'])
        self.assertFalse(saved['jogador_atual']['coroacao_concluida'])

    def test_high_risk_challenge_loss_ends_game(self):
        state = {'contador_rodadas': 34,
                 'encontros': {'desafio': {'espera': 24, 'ultima_tentativa': 34}}}
        with patch('count_queen.game.random.randint', return_value=500):
            saved = self.play(Jogador('Ana', fichas=100, prestigio=5000), ['10', '10', '8', '8'],
                              ['j', '10', 's', '', 's', '', ''], state)
        self.assertIsNone(saved['jogador_atual'])
        self.assertEqual(saved['herois_caidos'], ['Ana'])

    def test_high_risk_challenge_requires_minimum_chips(self):
        state = {'contador_rodadas': 34,
                 'encontros': {'desafio': {'espera': 24, 'ultima_tentativa': 34}}}
        saved = self.play(Jogador('Ana', fichas=99, prestigio=5000), ['10', '10', '8', '8'],
                          ['j', '10', 's', '', 's'], state)
        self.assertEqual(saved['encontros']['desafio']['espera'], 24)

    def test_balance_below_minimum_bet_ends_game(self):
        saved = self.play(Jogador('Ana', fichas=0.5), [], [''])
        self.assertIsNone(saved['jogador_atual'])
        self.assertEqual(saved['herois_caidos'], ['Ana'])

    def test_last_crown_win_archives_hero_for_both_paths(self):
        for caminho, prestigio in [('nobreza', 10000), ('tirania', -10000)]:
            with self.subTest(caminho=caminho):
                player = Jogador('Ana', prestigio=prestigio, caminho=caminho,
                                 coroacao_ativa=True, coroacao_vitorias=2)
                saved = self.play(player, ['A', '10', 'K', '8'], ['j', '10', '', ''])
                self.assertIsNone(saved['jogador_atual'])
                self.assertEqual(saved['herois_verdadeiros'], ['Ana'])

    def test_fast_mode_and_repeat_bet_need_no_pause_inputs(self):
        saved = self.play(Jogador('Ana', ultima_aposta=20), ['10', '10', '8', '8'],
                          ['r', '', '', 's', 's'])
        self.assertTrue(saved['jogador_atual']['modo_rapido'])
        self.assertEqual(saved['jogador_atual']['ultima_aposta'], 20)
        self.assertEqual(saved['contador_rodadas'], 1)

    def test_skipping_shop_does_not_open_menu(self):
        state = {'contador_rodadas': 9,
                 'encontros': {'emporio': {'espera': 7, 'ultima_tentativa': 9}}}
        with patch('count_queen.game.mostrar_loja') as shop:
            self.play(Jogador('Ana'), ['10', 'A', '9', 'K'], ['j', '10', '', 's', 's'], state)
        shop.assert_not_called()

    def test_twin_jewels_allow_free_resplit_without_remaining_chips(self):
        player = Jogador('Ana', itens=['joias_gemeas'])
        saved = self.play(player, ['8', '10', '8', '7', '8', '10', '2', '10'],
                          ['j', '100', 'sp', 'sp', 's', 's', 's', '', 's'])
        self.assertEqual(len(player.maos), 3)
        self.assertEqual(saved['jogador_atual']['fichas'], 400)


if __name__ == '__main__':
    unittest.main()
