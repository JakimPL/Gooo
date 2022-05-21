import os
import threading
import time
from typing import Union

import numpy as np
import pyspiel
from open_spiel.python.algorithms import mcts
from open_spiel.python.algorithms.alpha_zero import evaluator as az_evaluator
from open_spiel.python.algorithms.alpha_zero import model as az_model

from config import get_config


class OpenSpiel:
    def __init__(self, board_size: int):
        config = get_config()
        self._threading = config.threading
        self._sleep_time = config.sleep_time

        self._board_size: int = board_size
        self._game: pyspiel.Game = pyspiel.load_game("gooo", {"board_size": board_size})
        self._az_state: pyspiel.State = self._game.new_initial_state()
        self._bot = self._get_bot()

        self._lock = threading.Lock()

        self._suggested_action = None
        self.calculate_best_move()

    def _get_bot(self) -> Union[None, mcts.MCTSBot]:
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

        return None

    def _get_suggested_action(self):
        action = self._bot.step(self._az_state) if self.is_initialized() else None
        time.sleep(self._sleep_time)
        self._suggested_action = action

    def is_initialized(self) -> bool:
        return self._bot is not None

    def get_board(self) -> str:
        return str(self._az_state)

    def move(self, element: int):
        if self.is_initialized():
            self._az_state.apply_action(element)
            self.calculate_best_move()

    def calculate_best_move(self):
        self._suggested_action = None
        if not self._az_state.is_terminal():
            if self._threading:
                threading.Thread(
                    target=self._get_suggested_action,
                    args=(),
                    daemon=True
                ).start()
            else:
                self._get_suggested_action()

    @property
    def board_size(self) -> int:
        return self._board_size

    @property
    def suggested_action(self) -> int:
        return self._suggested_action
