import os
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Union

import numpy as np

from config import get_config


class Agent:
    def __init__(self, board_size: int):
        config = get_config()
        self._threading = config.threading
        self._sleep_time = config.sleep_time

        self._board_size: int = board_size

        try:
            import pyspiel
            self._game: pyspiel.Game = pyspiel.load_game("gooo", {"board_size": board_size})
            self._state: pyspiel.State = self._game.new_initial_state()
            self._bot = self._get_bot()
        except ModuleNotFoundError:
            self._game = None
            self._state = None
            self._bot = None
            print("Module pyspiel not found. Agent is disabled")

        self._executor = ThreadPoolExecutor(max_workers=1)

        self._suggested_action = None
        self.calculate_best_move()

    def _get_bot(self):
        from open_spiel.python.algorithms import mcts
        from open_spiel.python.algorithms.alpha_zero import evaluator as az_evaluator
        from open_spiel.python.algorithms.alpha_zero import model as az_model

        rng = np.random.RandomState()
        model_directory = "model_{size}x{size}".format(size=self._board_size)
        model_path = os.path.join(model_directory, "{size}x{size}".format(size=self._board_size))

        if os.path.isdir(model_directory):
            model = az_model.Model.from_checkpoint(model_path)
            evaluator = az_evaluator.AlphaZeroEvaluator(self._game, model)
            return mcts.MCTSBot(
                game=self._game,
                uct_c=2,
                max_simulations=1000,
                evaluator=evaluator,
                random_state=rng,
                child_selection_fn=mcts.SearchNode.puct_value,
                solve=True,
                verbose=False
            )
        else:
            print("Model {size}x{size} does not exist".format(size=self._board_size))

    def _calculate_suggested_action(self, state) -> Union[None, int]:
        if self.is_initialized():
            time.sleep(self._sleep_time)
            action = self._bot.step(state)
            if self._state.is_terminal() or state.observation_string() != self._state.observation_string():
                return None

            return action

    def _set_suggested_action(self, future: Future):
        self._suggested_action = future.result()

    def is_initialized(self) -> bool:
        return self._bot is not None

    def get_board(self) -> str:
        return str(self._state) if self._state is not None else ''

    def move(self, element: int):
        if self.is_initialized():
            self._state.apply_action(element)
            self.calculate_best_move()

    def calculate_best_move(self):
        if self.is_initialized():
            self._suggested_action = None
            if not self._state.is_terminal():
                if self._threading:
                    state = self._state.clone()
                    future = self._executor.submit(self._calculate_suggested_action, state)
                    future.add_done_callback(self._set_suggested_action)
                else:
                    self._suggested_action = self._calculate_suggested_action(self._state)

    @property
    def board_size(self) -> int:
        return self._board_size

    @property
    def suggested_action(self) -> int:
        return self._suggested_action
