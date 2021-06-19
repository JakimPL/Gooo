import pygame
import sys
from state import State
from pygame import locals
from ui import UI
from trainer import Trainer


class Game:
    def __init__(self, n=3, autoplay=False):
        pygame.init()
        self.autoplay = autoplay
        self.n = n
        self.FPS = 60
        self.state = State(n)
        self.ui = UI(self.n + 1)
        self.clock = pygame.time.Clock()
        self.trainer = Trainer(n)
        self.trainer.load()

    def frame(self):
        self.ui.draw_game(self.state)
        self.ui.draw_text("Game {0}. {1} player turn.".format(self.trainer.agent.games + 1, "Red" if self.state.player else "Blue"))
        if self.autoplay:
            self.state = self.trainer.state
            self.trainer.train_step()
        else:
            if not self.state.end and pygame.mouse.get_pressed(3)[0]:
                x, y = self.ui.get_mouse_positions(pygame.mouse.get_pos())
                element = (x if self.state.player else y) - 1
                position = y if self.state.player else x
                if 0 <= element < self.n and self.state.positions[self.state.player][element] == position and self.state.is_move_possible(element):
                    self.state.move(element)

        if self.state.points != 0:
            text = "{2} player wins by {0} point{1}.".format(self.state.points, "s" if self.state.points > 1 else "", "Red" if self.state.points > 0 else "Blue")
        else:
            text = "Draw."

        self.ui.draw_text(text)

        np_state = self.trainer.agent.get_state(self.state)
        prediction_vector = [round(i.item(), 6) for i in self.trainer.agent.get_prediction_vector(np_state)]
        best_move = self.trainer.agent.get_prediction(np_state)
        self.ui.draw_text("{0} (best move: {1})".format(prediction_vector, best_move))

        for event in pygame.event.get():
            if event.type == locals.QUIT:
                self.trainer.agent.model.save()
                pygame.quit()
                sys.exit()
        self.clock.tick(self.FPS)
        pygame.display.update()
