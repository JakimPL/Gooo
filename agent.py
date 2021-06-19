import torch
import random
import numpy as np
from collections import deque
from state import State
from model import LQN, QTRN
from config import Config

config = Config()


class Agent:
    def __init__(self, n, learning_rate=config.alpha, gamma=config.gamma, hidden_layers=config.layers,
                 max_len=config.max_len, alpha=config.alpha, batch_size=config.batch_size, power=config.power):
        self.power = power
        self.size = n
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.games = 0
        self.eps = 0
        self.gamma = gamma
        self.memory = deque(maxlen=max_len)
        self.model = LQN(2 * self.size + 1, hidden_layers, self.size)
        self.trainer = QTRN(self.model, alpha, gamma=self.gamma)

    @staticmethod
    def get_state(state: State):
        return np.array([state.player] + state.positions[0] + state.positions[1], dtype=int)

    def remember(self, state, move, reward, next_state, end):
        self.memory.append((state, move, reward, next_state, end))

    def train_short(self, current_state, move, reward, next_state, end):
        self.trainer.train_step(current_state, move, reward, next_state, end)

    def train_long(self):
        sample = random.sample(self.memory, self.batch_size) if len(self.memory) > self.batch_size else self.memory

        current_state, move, reward, next_state, end = zip(*sample)
        self.trainer.train_step(current_state, move, reward, next_state, end)

    def get_prediction_vector(self, state: np.array):
        return self.model(torch.tensor(state, dtype=torch.float))

    def get_prediction(self, state: np.array):
        return torch.argmax(self.get_prediction_vector(state)).item()

    def get_action(self, state: np.array):
        game_state = self.state_from_array(state)
        self.eps = 1 / ((self.games + 1) ** self.power)
        move = [0] * self.size
        if random.random() < self.eps:
            index = random.choice(game_state.get_possible_moves())
        else:
            index = self.get_prediction(state)

        move[index] = 1
        return move

    @staticmethod
    def state_from_array(array: np.array) -> State:
        size = (len(array) - 1) // 2
        state = State(size)
        state.player = array[0]
        state.positions = [array[1:size + 1], array[size + 1:]]
        return state
