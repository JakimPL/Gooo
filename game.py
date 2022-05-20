import sys

import pygame
import pyspiel
from pygame import locals

from agent import get_bot
from state import State
from ui import UI


class Game:
    def __init__(self, board_size: int = 5, autoplay: tuple[bool, bool] = (False, False)):
        pygame.init()
        self.autoplay = autoplay
        self.board_size = board_size
        self.FPS = 60
        self.state = State(self.board_size)
        self.ui = UI(self.board_size + 1)
        self.clock = pygame.time.Clock()

        self.game: pyspiel.Game = pyspiel.load_game('gooo', {'board_size': board_size})
        self.az_state: pyspiel.State = self.game.new_initial_state()
        self.bot = get_bot(self.game, self.board_size)
        self.suggested_action = self._get_suggested_action()

        self.element = None
        self.position = None

        self.loop = None

    def _get_suggested_action(self):
        return self.bot.step(self.az_state)

    def _get_events(self):
        if not self.state.end and pygame.mouse.get_pressed(3)[0]:
            x, y = self.ui.get_mouse_positions(pygame.mouse.get_pos())
            self.element = (x if self.state.player else y) - 1
            self.position = y if self.state.player else x

        for event in pygame.event.get():
            if event.type == locals.QUIT:
                pygame.quit()
                sys.exit()

    def _make_move(self, element: int):
        if self.state.is_move_possible(element):
            self.state.move(element)
            self.az_state.apply_action(element)
            if not self.az_state.is_terminal():
                self.suggested_action = self.bot.step(self.az_state)

    def _frame(self):
        self.ui.draw_game(self.state)
        self.ui.draw_text("{turn} player turn.".format(turn="Red" if self.state.player else "Blue"))
        if self.state.points != 0:
            text = "{player} player wins by {points} point{plural}.".format(
                points=abs(self.state.points),
                plural="s" if abs(self.state.points) > 1 else "",
                player="Red" if self.state.points > 0 else "Blue"
            )
        else:
            text = "Draw."

        self.ui.draw_text(text)
        if self.suggested_action is not None:
            self.ui.draw_text("Suggested action: {action}.".format(action=self.suggested_action))

        self._get_events()
        if self.autoplay[self.state.player]:
            self._make_move(self.suggested_action)
        else:
            if self.element is not None and 0 <= self.element < self.board_size and \
                    self.state.positions[self.state.player][self.element] == self.position:
                self._make_move(self.element)

    def play(self):
        while True:
            self._frame()
            self.clock.tick(self.FPS)
            pygame.display.update()
