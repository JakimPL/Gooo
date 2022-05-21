import sys

import pygame
from pygame import locals

from agent import Agent
from state import State
from ui import UI

FPS = 60


class Game:
    def __init__(self, board_size: int = 5, autoplay: tuple[bool, bool] = (False, False), suggestions: bool = True):
        self._board_size: int = board_size
        self._state: State = State(self._board_size)

        self._ui: UI = UI(self._board_size + 1)

        self._clock: pygame.time.Clock = pygame.time.Clock()

        self._element = None
        self._position = None

        self._open_spiel: Agent = Agent(self._board_size)
        self._autoplay: tuple[bool, bool] = autoplay if self._open_spiel.is_initialized() else (False, False)
        self._suggestions: bool = suggestions

        self._history: list[str] = []

    def _reset_elements(self):
        self._element = None
        self._position = None

    def _get_events(self):
        if not self._state.end and pygame.mouse.get_pressed(3)[0]:
            x, y = self._ui.get_mouse_positions(pygame.mouse.get_pos())
            self._element = (x if self._state.player else y) - 1
            self._position = y if self._state.player else x

        for event in pygame.event.get():
            if event.type == locals.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN and event.unicode.isdigit():
                number = int(event.unicode) - 1
                if 0 <= number < self._board_size:
                    self._element = number
                    self._position = self._state.get_position(self._state.player, number)

    def _control_moves(self):
        if self._autoplay[self._state.player]:
            if self._open_spiel.suggested_action is not None:
                self._make_move(self._open_spiel.suggested_action)
        else:
            element = self._element
            position = self._position
            if element is not None and 0 <= element < self._board_size and \
                    self._state.get_position(self._state.player, element) == position and \
                    self._state.is_move_possible(element):
                self._make_move(element)

    def _make_move(self, action: int):
        if self._state.is_move_possible(action):
            player = self._state.player
            self._reset_elements()
            self._state.move(action)
            self._open_spiel.move(action)

            self._history.append("{player}: {action}".format(
                player="o" if player else "x",
                action=action + 1
            ))
        else:
            print("Tried to move: {move}".format(move=action), self._state, sep="\n")
            raise ValueError("move {move} is not possible".format(move=action))

        if self._open_spiel.get_board() != self._state.get_board():
            print(self._state.get_board(), "vs", self._open_spiel.get_board(), sep="\n")
            raise ValueError("state mismatch")

    def _draw(self):
        self._ui.draw_game(self._state)
        self._ui.draw_text("{turn} player turn.".format(turn="Red" if self._state.player else "Blue"))
        if self._state.points != 0:
            text = "{player} player wins by {points} point{plural}.".format(
                points=abs(self._state.points),
                plural="s" if abs(self._state.points) > 1 else "",
                player="Red" if self._state.points < 0 else "Blue"
            )
        else:
            text = "Draw."

        self._ui.draw_text(text)
        if self._suggestions and self._open_spiel.suggested_action is not None:
            self._ui.draw_text("Suggested action: {action}.".format(action=self._open_spiel.suggested_action + 1))

    def _frame(self):
        self._draw()
        self._get_events()
        self._control_moves()

    def play(self):
        while True:
            self._frame()
            self._clock.tick(FPS)
            pygame.display.update()
