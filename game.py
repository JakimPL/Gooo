import sys

import pygame
from pygame import locals

from agent import OpenSpiel
from state import State
from ui import UI

FPS = 60


class Game:
    def __init__(self, board_size: int = 5, autoplay: tuple[bool, bool] = (False, False)):
        pygame.init()
        self.autoplay = autoplay
        self.board_size = board_size
        self.state = State(self.board_size)
        self.ui = UI(self.board_size + 1)

        self.clock = pygame.time.Clock()

        self.element = None
        self.position = None

        self.open_spiel = OpenSpiel(self.board_size)

    def _get_events(self):
        if not self.state.end and pygame.mouse.get_pressed(3)[0]:
            x, y = self.ui.get_mouse_positions(pygame.mouse.get_pos())
            self.element = (x if self.state.player else y) - 1
            self.position = y if self.state.player else x

        for event in pygame.event.get():
            if event.type == locals.QUIT:
                pygame.quit()
                sys.exit()

    def _control_moves(self):
        if self.autoplay[self.state.player]:
            if self.open_spiel.suggested_action is not None:
                self._make_move(self.open_spiel.suggested_action)
        else:
            if self.element is not None and 0 <= self.element < self.board_size and \
                    self.state.positions[self.state.player][self.element] == self.position:
                self._make_move(self.element)

    def _make_move(self, element: int):
        if self.state.is_move_possible(element):
            self.state.move(element)
            self.open_spiel.move(element)

    def _draw(self):
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
        if self.open_spiel.suggested_action is not None:
            self.ui.draw_text("Suggested action: {action}.".format(action=self.open_spiel.suggested_action))

    def _frame(self):
        self._draw()
        self._get_events()
        self._control_moves()

    def play(self):
        while True:
            self._frame()
            self.clock.tick(FPS)
            pygame.display.update()
