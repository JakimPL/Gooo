from agent import Agent
from state import State


class Trainer:
    def __init__(self, n: int, max_games=0):
        self.agent = Agent(n)
        self.state = State(n)
        self.max_games = max_games

    def train(self):
        while self.max_games == 0 or self.agent.games < self.max_games:
            self.train_step()

    def train_step(self):
        current_player = self.state.player
        current_state = self.agent.get_state(self.state)
        move = self.agent.get_action(current_state)
        move_index = move.index(1)
        penalty = 0
        if not self.state.move(move_index):
            penalty = -1
        self.state.move(move_index)
        current_score = self.state.points
        end, score = self.state.end, self.state.points
        reward = ((-1) ** current_player) * (self.state.points - current_score) + penalty
        next_state = self.agent.get_state(self.state)

        self.agent.train_short(current_state, move, reward, next_state, end)
        self.agent.remember(current_state, move, reward, next_state, end)

        if end:
            self.state.reset()
            self.agent.games += 1
            self.agent.train_long()

            print("Game: {0}, Score: {1}".format(self.agent.games, score))

    def load(self):
        self.agent.model.load()
