import argparse

import pygame

parser = argparse.ArgumentParser(description="Gooo game")
parser.add_argument(
    "-n", "--board_size", metavar="board_size", type=int, nargs="?", default=5,
    help="size of the board"
)
parser.add_argument(
    "-a", "--autoplay", metavar="autoplay", type=bool, nargs="?", const=True, default=False,
    help="is second player a bot?"
)
parser.add_argument(
    "-s", "--suggestions", metavar="suggestions", type=bool, nargs="?", const=True, default=False,
    help="show suggestions"
)

args = parser.parse_args()
size = args.board_size
autoplay = args.autoplay
suggestions = args.suggestions

if __name__ == "__main__":
    assert 1 < size <= 10, "invalid size: {size}; the size should be in the interval [2, 10]".format(size=size)

    from game import Game

    pygame.init()
    pygame.display.set_caption("Gooo")
    game = Game(size, autoplay=(False, autoplay), suggestions=suggestions)
    game.play()
