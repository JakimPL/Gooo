import argparse

import pygame

parser = argparse.ArgumentParser(description="Gooo game")
parser.add_argument(
    "-n", "--board-size", metavar="board_size", type=int, nargs="?", default=5,
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
parser.add_argument(
    "-e", "--end-policy", metavar="end_policy", type=str, nargs="?", const=True, default="soft",
    help="end policy, either 'soft' or 'hard'"
)

args = parser.parse_args()
size = args.board_size
autoplay = args.autoplay
suggestions = args.suggestions
end_policy = args.end_policy

if __name__ == "__main__":
    assert 1 < size <= 10, "invalid size: {size}; the size should be in the interval [2, 10]".format(size=size)
    assert end_policy in ["soft", "hard"], "end policy has to be either 'soft' or 'hard"

    from game import Game

    pygame.init()
    pygame.display.set_caption("Gooo")
    game = Game(
        board_size=size,
        autoplay=(False, autoplay),
        suggestions=suggestions,
        end_policy=end_policy
    )

    game.play()
