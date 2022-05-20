class State:
    def __init__(self, size: int):
        self.size: int = size
        self.moves: int = 0
        self.points: int = 0
        self.player: int = 0
        self.positions: list[list[int]] = [[0] * size, [0] * size]
        self.end: bool = False

    def __str__(self):
        return "Size: {size}\nMoves: {moves}\nPoints: {points}\n{player} player turn{end}\n{board}".format(
            size=self.size,
            moves=self.moves,
            points=self.points,
            player="Red" if self.player else "Blue",
            end="\nThe game has ended" if self.end else "",
            board=self.get_board()
        )

    def __repr__(self):
        return self.__str__()

    def reset(self):
        self.__init__(self.size)

    def get_board(self) -> str:
        string = ""
        for i in range(self.size + 1):
            line = ""
            for j in range(self.size + 1):
                sign = ' '
                if i > 0 and j > 0:
                    sign = '.'
                if j > 0 and self.positions[1][j - 1] == i:
                    sign = 'x'
                if i > 0 and self.positions[0][i - 1] == j:
                    sign = 'o'
                line += sign
            line += '\n'
            string += line

        return string

    def is_move_possible(self, i) -> bool:
        if i < 0 or i >= self.size:
            return False

        position = self.positions[self.player][i]
        return self.positions[self.player][i] == self.size or \
               (self.positions[self.player][i] < self.size and self.positions[1 - self.player][position] != i + 1)

    def get_possible_moves(self) -> list[int]:
        return [] if self.end else [i for i in range(self.size) if self.is_move_possible(i)]

    def is_end(self) -> bool:
        for position in self.positions[self.player]:
            if position < self.size:
                return False

        return True

    def move(self, i) -> bool:
        if not self.end and self.is_move_possible(i):
            self.moves += 1

            self.positions[self.player][i] += 1
            if self.positions[self.player][i] > self.size:
                self.end = self.is_end()

            if not self.end:
                self.player = 1 - self.player
                if not self.get_possible_moves():
                    self.points += 1 - 2 * self.player
                    self.player = 1 - self.player

            return True

        return False
