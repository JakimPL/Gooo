import pygame
import sys
from state import State
from pygame import locals
from ui import UI


class Game:
    def __init__(self, n=3):
        pygame.init()
        self.n = n
        self.FPS = 60
        self.state = State(n)
        self.ui = UI(self.n + 1)
        self.clock = pygame.time.Clock()

    def frame(self):
        self.ui.draw_game(self.state)
        if not self.state.end and pygame.mouse.get_pressed(3)[0]:
            x, y = self.ui.get_mouse_positions(pygame.mouse.get_pos())
            element = (x if self.state.player else y) - 1
            position = y if self.state.player else x
            if 0 <= element < self.n and self.state.positions[self.state.player][element] == position and self.state.is_move_possible(element):
                self.state.move(element)
        for event in pygame.event.get():
            if event.type == locals.QUIT:
                pygame.quit()
                sys.exit()
        self.clock.tick(self.FPS)
        pygame.display.update()


game = Game()
while True:
    game.frame()
