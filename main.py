import argparse

from game import Game

parser = argparse.ArgumentParser(description="Gooo game")
parser.add_argument('-s', '--size', metavar='size', type=int, nargs='?', default=5,
                    help='size of the board')
parser.add_argument('-a', '--autoplay', metavar='autoplay', type=bool, nargs='?', const=True, default=False,
                    help='autoplay')

args = parser.parse_args()
size = args.size
autoplay = args.autoplay

if __name__ == '__main__':
    game = Game(size, autoplay=(False, True))
    while True:
        game.frame()
