import argparse
from game import Game
from trainer import Trainer

parser = argparse.ArgumentParser(description="Deep reinforcement learning for Gooo game")
parser.add_argument('-s', '--size', metavar='size', type=int, nargs='?', default=3,
                    help='size of the board')
parser.add_argument('-a', '--autoplay', metavar='autoplay', type=bool, nargs='?', const=True, default=False,
                    help='autoplay')
parser.add_argument('-t', '--train', metavar='train', type=bool, nargs='?', const=True, default=False,
                    help='train the model')
parser.add_argument('-g', '--games', metavar='games', type=int, nargs='?', default=0,
                    help='number of games (for training)')

args = parser.parse_args()
size = args.size
autoplay = args.autoplay
train = args.train

if train:
    trainer = Trainer(args.size, max_games=args.games)
    try:
        trainer.train()
    except KeyboardInterrupt:
        print("\nEnding...")
        trainer.agent.model.save()

else:
    game = Game(size, autoplay=autoplay)
    while True:
        game.frame()
