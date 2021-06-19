import argparse
from agent import Agent
from state import State


class Trainer:
    def __init__(self, n: int, max_games=0):
        self.agent = Agent(n)
        self.state = State(n)
        self.train(max_games=max_games)

    def train(self, max_games=0):
        while max_games == 0 or self.agent.games < max_games:
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


parser = argparse.ArgumentParser(description="Deep reinforcement learning for Gooo game")
parser.add_argument('-s', '--size', metavar='size', type=int, nargs='?', default=3,
                    help='size of the board')
parser.add_argument('-g', '--games', metavar='games', type=int, nargs='?', default=0,
                    help='number of games')

args = parser.parse_args()
trainer = Trainer(args.size, max_games=args.games)
trainer.agent.model.save()
