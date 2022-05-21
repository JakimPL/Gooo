class State:
    def __init__(self, size: int, end_policy: str = "hard"):
        self._size: int = size
        self._moves: int = 0
        self._points: int = 0
        self._player: int = 0
        self._positions: list[list[int]] = [[0] * size, [0] * size]
        self._end: bool = False
        self._end_policy: str = end_policy

    def __str__(self):
        return "Size: {size}\nMoves: {moves}\nPoints: {points}\n{board}".format(
            size=self._size,
            moves=self._moves,
            points=self._points,
            end="\nThe game has ended" if self._end else "",
            board=self.get_board()
        )

    def __repr__(self):
        return self.__str__()

    def reset(self):
        self.__init__(self._size)

    def get_board(self) -> str:
        string = "Red" if self._player else "Blue"
        string += " player turn\n"
        for i in range(self._size + 1):
            line = ""
            for j in range(self._size + 1):
                sign = " "
                if i > 0 and j > 0:
                    sign = "."
                if j > 0 and self._positions[1][j - 1] == i:
                    sign = "x"
                if i > 0 and self._positions[0][i - 1] == j:
                    sign = "o"
                line += sign
            line += "\n"
            string += line

        string += "Points: {points}".format(points=self._points)
        return string

    def is_move_possible(self, i) -> bool:
        if i < 0 or i >= self._size:
            return False

        position = self._positions[self._player][i]
        return self._positions[self._player][i] == self._size or \
               (self._positions[self._player][i] < self._size and self._positions[1 - self._player][position] != i + 1)

    def get_possible_moves(self) -> list[int]:
        return [] if self._end else [i for i in range(self._size) if self.is_move_possible(i)]

    def is_end(self) -> bool:
        return self.is_soft_end() if self._end_policy == "soft" else self.is_hard_end()

    def is_hard_end(self) -> bool:
        for position in self._positions[self._player]:
            if position <= self._size:
                return False

        return True

    def is_soft_end(self) -> bool:
        for player in [0, 1]:
            for i in range(self._size):
                position = self._positions[player][i]
                for j in range(position, self._size):
                    if self._positions[1 - player][j] <= i + 1:
                        return False

        return True

    def move(self, i) -> bool:
        if not self._end and self.is_move_possible(i):
            self._moves += 1

            self._positions[self._player][i] += 1
            if self._positions[self._player][i] > self._size:
                self._end = self.is_hard_end()

            if not self._end:
                self._player = 1 - self._player
                if not self.get_possible_moves():
                    self._points += 2 * self._player - 1
                    self._player = 1 - self._player

            return True

        return False

    def get_position(self, player: int, action: int) -> int:
        return self._positions[player][action]

    @property
    def points(self) -> int:
        return self._points

    @property
    def moves(self) -> int:
        return self._moves

    @property
    def end(self) -> bool:
        return self._end

    @property
    def player(self) -> int:
        return self._player
