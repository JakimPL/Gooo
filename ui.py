import pygame
from state import State
from config import Config


class UI:
    def __init__(self, board_size):
        config = Config()
        self.line = 0
        self.x_offset = config.x_offset
        self.y_offset = config.y_offset
        self.size = config.tile_size
        self.rim = config.rim_size
        self.panel = config.panel_width
        self.board_size = board_size

        self.game_width = 2 * self.x_offset + self.size * self.board_size + self.panel
        self.game_height = 2 * self.y_offset + self.size * self.board_size

        self.sprites = [pygame.image.load("car{0}.png".format(i + 1)) for i in range(2)]
        self.TURN = [(64, 64, 128), (128, 64, 64)]
        self.COLOR = [[(180, 192, 180) for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.LT_GREY = (210, 210, 210)
        self.DK_GREY = (112, 112, 112)
        self.BLACK = (0, 0, 0)
        self.RIM_COLOR = [[(220, 220, 220) for _ in range(self.board_size)] for _ in range(self.board_size)]

        for i in range(self.board_size - 1):
            self.COLOR[0][1 + i] = (112, 112, 255)
            self.RIM_COLOR[0][1 + i] = (192, 192, 255)
            self.COLOR[1 + i][0] = (255, 112, 112)
            self.RIM_COLOR[1 + i][0] = (255, 192, 192)

        self.font = pygame.font.SysFont(config.font, 14)
        self.DISPLAYSURF = pygame.display.set_mode((self.game_width, self.game_height), 0, 32)

    def draw_game(self, state: State):
        self.line = 0
        pygame.draw.rect(self.DISPLAYSURF, self.DK_GREY if state.end else self.TURN[state.player], (0, 0, self.game_width, self.game_height))
        for i in range(self.board_size):
            for j in range(self.board_size):
                pygame.draw.rect(self.DISPLAYSURF, self.RIM_COLOR[i][j], (self.x_offset + i * self.size + 1, self.y_offset + j * self.size + 1, self.size - 2, self.size - 2))
                if self.is_mouse_in_region(pygame.mouse.get_pos(), i, j):
                    color = self.LT_GREY
                else:
                    color = self.COLOR[i][j]
                if not state.end:
                    pygame.draw.rect(self.DISPLAYSURF, color, (self.x_offset + i * self.size + self.rim, self.y_offset + j * self.size + self.rim, self.size - 2 * self.rim, self.size - 2 * self.rim))

        for i in range(self.board_size - 1):
            for player in [0, 1]:
                position = state.positions[player][i]
                if position < self.board_size:
                    x = self.x_offset + self.size * (position if player == 0 else i + 1)
                    y = self.y_offset + self.size * (position if player == 1 else i + 1)
                    self.DISPLAYSURF.blit(self.sprites[player], (x, y))

    def draw_text(self, text):
        label = self.font.render(text, True, (255, 255, 255))
        self.DISPLAYSURF.blit(label, (self.game_width - self.panel, self.y_offset + 15 * self.line))
        self.line += 1

    def get_mouse_positions(self, pos):
        return [(pos[i] - self.x_offset) // self.size for i in [0, 1]]

    def is_mouse_in_region(self, pos, i, j):
        return self.x_offset + i * self.size + 1 < pos[0] <= self.x_offset + (i + 1) * self.size and self.y_offset + j * self.size + 1 < pos[1] <= self.y_offset + (j + 1) * self.size
