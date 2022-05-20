import numpy as np
import pyspiel
from open_spiel.python.algorithms import mcts
from open_spiel.python.algorithms.alpha_zero import evaluator as az_evaluator
from open_spiel.python.algorithms.alpha_zero import model as az_model


class OpenSpiel:
    def __init__(self, board_size: int):
        self.board_size = board_size
        self.game: pyspiel.Game = pyspiel.load_game('gooo', {'board_size': board_size})
        self.az_state: pyspiel.State = self.game.new_initial_state()

        self.bot = self._get_bot()
        self.suggested_action = self._get_suggested_action()

    def _get_bot(self) -> mcts.MCTSBot:
        rng = np.random.RandomState()
        model_path = 'model_{size}x{size}/checkpoint--1'.format(size=self.board_size)
        model = az_model.Model.from_checkpoint(model_path)
        evaluator = az_evaluator.AlphaZeroEvaluator(self.game, model)
        return mcts.MCTSBot(
            self.game,
            2,
            1000,
            evaluator,
            random_state=rng,
            child_selection_fn=mcts.SearchNode.puct_value,
            solve=True,
            verbose=False
        )

    def _get_suggested_action(self):
        return self.bot.step(self.az_state)

    def move(self, element: int):
        self.az_state.apply_action(element)
        if not self.az_state.is_terminal():
            self.suggested_action = self.bot.step(self.az_state)
