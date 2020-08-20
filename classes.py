from abc import ABC, abstractmethod
import numpy as np

class Board:
    def __init__(self):
        self.board = np.empty((8,8), Piece)
        self.shape = self.board.shape

    def __str__(self):
        return str(self.board)

    def get_space(self, x, y):
        return self.board[y][x]

    def add(self, piece):
        self.board[piece.y][piece.x] = piece

    def fill_board(self):
        self.add(Rook("White", 0, 0))
        self.add(Knight("White", 1, 0))
        self.add(Bishop("White", 2, 0))
        self.add(King("White", 3, 0))
        self.add(Queen("White", 4, 0))
        self.add(Bishop("White", 5, 0))
        self.add(Knight("White", 6, 0))
        self.add(Rook("White", 7, 0))
        for i in range(8):
            self.add(Pawn("White", i, 1))
        for i in range(8):
            self.add(Pawn("Black", i, 6))
        self.add(Rook("Black", 0, 7))
        self.add(Knight("Black", 1, 7))
        self.add(Bishop("Black", 2, 7))
        self.add(King("Black", 3, 7))
        self.add(Queen("Black", 4, 7))
        self.add(Bishop("Black", 5, 7))
        self.add(Knight("Black", 6, 7))
        self.add(Rook("Black", 7, 7))

    def print_board(self):
        for i in range(8):
            output = ""
            for j in range(8):
                output += "%13s " % self.board[i][j]
            print(output)

class Piece(ABC):
    def __init__(self, color, x, y):
        self.x = x
        self.y = y
        self.color = color
        super().__init__()

    def __str__(self):
        return "%s %s" % (self.color, self.name)

class Queen(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.name = "Queen"

class Pawn(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.name = "Pawn"

class Rook(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.name = "Rook"

class Bishop(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.name = "Bishop"

class Knight(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.name = "Knight"

class King(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.name = "King"


if __name__ == "__main__":
    board = Board()
    board.fill_board()
    board.print_board()
