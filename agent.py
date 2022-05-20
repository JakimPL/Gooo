import numpy as np
from open_spiel.python.algorithms import mcts
from open_spiel.python.algorithms.alpha_zero import evaluator as az_evaluator
from open_spiel.python.algorithms.alpha_zero import model as az_model


def get_bot(game, size: int) -> mcts.MCTSBot:
    rng = np.random.RandomState()
    model_path = 'model_{size}x{size}/checkpoint--1'.format(size=size)
    model = az_model.Model.from_checkpoint(model_path)
    evaluator = az_evaluator.AlphaZeroEvaluator(game, model)
    return mcts.MCTSBot(
        game,
        2,
        1000,
        evaluator,
        random_state=rng,
        child_selection_fn=mcts.SearchNode.puct_value,
        solve=True,
        verbose=False
    )
