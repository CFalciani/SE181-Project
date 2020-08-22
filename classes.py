from abc import ABC, abstractmethod
import numpy as np
import pygame

class Board:
    def __init__(self, square_size, sidebar):
        self.square_size = square_size
        self.sidebar = sidebar
        self.board = np.empty((8,8), Piece)
        self.shape = self.board.shape
        self.en_passant = None
        self.en_passant_counter = 0

    def __str__(self):
        return str(self.board)

    def flip(self, x,y):
        return 7 - x, 7 - y

    # Returns the contents of the specified space
    def get_space(self, x, y):
        return self.board[y][x]

    # Adds a piece to the board
    def add_piece(self, piece):
        x = piece.x
        y = piece.y
        self.board[y][x] = piece

    # Removes a piece from the board
    def remove_piece(self, piece):
        x = piece.x
        y = piece.y
        self.board[y][x] = None

    # Places all pieces in their starting positions
    def fill_board(self):
        self.add_piece(Rook("Black", 0, 0))
        self.add_piece(Knight("Black", 1, 0))
        self.add_piece(Bishop("Black", 2, 0))
        self.add_piece(King("Black", 3, 0))
        self.add_piece(Queen("Black", 4, 0))
        self.add_piece(Bishop("Black", 5, 0))
        self.add_piece(Knight("Black", 6, 0))
        self.add_piece(Rook("Black", 7, 0))
        for i in range(8):
            self.add_piece(Pawn("Black", i, 1))
        for i in range(8):
            self.add_piece(Pawn("White", i, 6))
        self.add_piece(Rook("White", 0, 7))
        self.add_piece(Knight("White", 1, 7))
        self.add_piece(Bishop("White", 2, 7))
        self.add_piece(King("White", 3, 7))
        self.add_piece(Queen("White", 4, 7))
        self.add_piece(Bishop("White", 5, 7))
        self.add_piece(Knight("White", 6, 7))
        self.add_piece(Rook("White", 7, 7))

    # Used for testing
    def print_board(self):
        for i in range(8):
            output = ""
            for j in range(8):
                output += "| (%d, %d): %12s " % (j, i, self.board[i][j])
            print(output)

    def draw(self, window):
        for i in range(8):
            for j in range(8):
                piece = self.get_space(i,j)
                if (piece == None):
                    continue
                window.blit(piece.img, (i * self.square_size + self.sidebar + 10, j * self.square_size + 10))

    def draw_rev(self, window):
        for i in range(8): # For the black team the board must be reversed
            for j in range(8):
                piece = self.get_space(i,j)
                if (piece == None):
                    continue 
                # 7 - x and 7 - y gives us the reversed coords
                window.blit(piece.img, ((7-i) * self.square_size + self.sidebar + 10, (7-j) * self.square_size + 10))



class Piece(ABC):
    @abstractmethod
    def __init__(self, color, name, x, y):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.path = "assets/" + color + name + ".png"
        self.img = pygame.image.load(self.path)
        super().__init__()

    # Returns a list of valid moves for the piece
    @abstractmethod
    def get_valid_moves(self, board):
        # Implement check logic here
        pass

    # Moves the piece to the specified space
    def move(self, board, new_x, new_y):
        if board.en_passant_counter > 0:
            board.en_passant_counter -= 1
        if board.en_passant_counter == 0 and board.en_passant is not None:
            board.en_passant.en_passant = False
            board.en_passant = None
        board.remove_piece(self)
        self.x = new_x
        self.y = new_y
        board.add_piece(self)

    def __str__(self):
        return "%s %s" % (self.color, self.name)


class Queen(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, "Queen" ,x, y)
        self.name = "Queen"

    def get_valid_moves(self, board):
        output = []

        # Up
        new_x = self.x
        new_y = self.y - 1
        while True:
            if new_y < 0:
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_y -= 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Up-Right
        new_x = self.x + 1
        new_y = self.y - 1
        while True:
            if new_x > (board.shape[1] - 1) or new_y < 0:
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_x += 1
                    new_y -= 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Right
        new_x = self.x + 1
        new_y = self.y
        while True:
            if new_x > (board.shape[1] - 1):
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_x += 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Down-Right
        new_x = self.x + 1
        new_y = self.y + 1
        while True:
            if new_x > (board.shape[1] - 1) or new_y > (board.shape[0] - 1):
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_x += 1
                    new_y += 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Down
        new_x = self.x
        new_y = self.y + 1
        while True:
            if new_y > (board.shape[0] - 1):
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_y += 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Down-Left
        new_x = self.x - 1
        new_y = self.y + 1
        while True:
            if new_x < 0 or new_y > (board.shape[0] - 1):
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_x -= 1
                    new_y += 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Left
        new_x = self.x - 1
        new_y = self.y
        while True:
            if new_x < 0:
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_x -= 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Up-Left
        new_x = self.x - 1
        new_y = self.y - 1
        while True:
            if new_x < 0 or new_y < 0:
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_x -= 1
                    new_y -= 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        return output


class Pawn(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, "Pawn", x, y)
        self.name = "Pawn"
        self.moved = False
        self.en_passant = False
        if color == "White":
            self.direction = -1
        else:
            self.direction = 1

    def get_valid_moves(self, board):
        output = []

        new_x = self.x
        new_y = self.y + self.direction
        if board.get_space(new_x, new_y) is None:
            output.append((new_x, new_y))
            if not self.moved and board.get_space(new_x, new_y + self.direction) is None:
                output.append((new_x, new_y + self.direction))

        new_x = self.x - 1
        new_y = self.y + self.direction
        if new_x >= 0:
            space = board.get_space(new_x, new_y)
            if space is not None and space.color != self.color:
                output.append((new_x, new_y))

        new_x = self.x + 1
        new_y = self.y + self.direction
        if new_x < board.shape[1]:
            space = board.get_space(new_x, new_y)
            if space is not None and space.color != self.color:
                output.append((new_x, new_y))

        if board.en_passant is not None and board.en_passant.color != self.color and board.en_passant.y == self.y:
            if board.en_passant.x == self.x - 1:
                output.append((self.x - 1, self.y + self.direction))
            elif board.en_passant.x == self.x + 1:
                output.append((self.x + 1, self.y + self.direction))

        return output

    def move(self, board, new_x, new_y):
        if new_x != self.x and board.get_space(new_x, new_y) is None:
            board.remove_piece(board.get_space(new_x, new_y - self.direction))
        super().move(board, new_x, new_y)
        if not self.moved and (new_y == 3 or new_y == 4):
            self.en_passant = True
            board.en_passant = self
        self.moved = True
        if new_y == 0 or new_y == 7:
            # Implement promotion here
            pass


class Rook(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, "Rook", x, y)
        self.name = "Rook"
        self.moved = False

    def get_valid_moves(self, board):
        output = []

        # Up
        new_x = self.x
        new_y = self.y - 1
        while True:
            if new_y < 0:
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_y -= 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Right
        new_x = self.x + 1
        new_y = self.y
        while True:
            if new_x > (board.shape[1] - 1):
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_x += 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Down
        new_x = self.x
        new_y = self.y + 1
        while True:
            if new_y > (board.shape[0] - 1):
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_y += 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Left
        new_x = self.x - 1
        new_y = self.y
        while True:
            if new_x < 0:
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_x -= 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        return output

    def move(self, board, new_x, new_y):
        super().move(board, new_x, new_y)
        self.moved = True


class Bishop(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, "Bishop", x, y)
        self.name = "Bishop"

    def get_valid_moves(self, board):
        output = []

        # Up-Right
        new_x = self.x + 1
        new_y = self.y - 1
        while True:
            if new_x > (board.shape[1] - 1) or new_y < 0:
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_x += 1
                    new_y -= 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Down-Right
        new_x = self.x + 1
        new_y = self.y + 1
        while True:
            if new_x > (board.shape[1] - 1) or new_y > (board.shape[0] - 1):
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_x += 1
                    new_y += 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Down-Left
        new_x = self.x - 1
        new_y = self.y + 1
        while True:
            if new_x < 0 or new_y > (board.shape[0] - 1):
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_x -= 1
                    new_y += 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        # Up-Left
        new_x = self.x - 1
        new_y = self.y - 1
        while True:
            if new_x < 0 or new_y < 0:
                break
            else:
                space = board.get_space(new_x, new_y)
                if space is None:
                    output.append((new_x, new_y))
                    new_x -= 1
                    new_y -= 1
                else:
                    if space.color != self.color:
                        output.append((new_x, new_y))
                    break

        return output


class Knight(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, "Knight", x, y)
        self.name = "Knight"

    def get_valid_moves(self, board):
        output = []

        new_x = self.x + 1
        new_y = self.y - 2
        if not (new_x > (board.shape[1] - 1) or new_y < 0):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))

        new_x = self.x + 2
        new_y = self.y - 1
        if not (new_x > (board.shape[1] - 1) or new_y < 0):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))

        new_x = self.x + 2
        new_y = self.y + 1
        if not (new_x > (board.shape[1] - 1) or new_y > (board.shape[0] - 1)):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))

        new_x = self.x + 1
        new_y = self.y + 2
        if not (new_x > (board.shape[1] - 1) or new_y > (board.shape[0] - 1)):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))

        new_x = self.x - 1
        new_y = self.y + 2
        if not (new_x < 0 or new_y > (board.shape[0] - 1)):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))

        new_x = self.x - 2
        new_y = self.y + 1
        if not (new_x < 0 or new_y > (board.shape[0] - 1)):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))

        new_x = self.x - 2
        new_y = self.y - 1
        if not (new_x < 0 or new_y < 0):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))

        new_x = self.x - 1
        new_y = self.y - 2
        if not (new_x < 0 or new_y < 0):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))

        return output


class King(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, "King", x, y)
        self.name = "King"
        self.moved = False

    def get_valid_moves(self, board):
        # Implement
        pass

    def move(self, board, new_x, new_y):
        # Implement
        super().move(board, new_x, new_y)
        self.moved = True


# Testing
if __name__ == "__main__":
    board = Board()
    board.fill_board()
    test_piece = Pawn("White", 2, 6)
    board.add_piece(test_piece)
    test_piece.move(board, 2, 5)
    test_piece.move(board, 2, 4)
    test_piece.move(board, 2, 3)
    board.get_space(3, 1).move(board, 3, 3)
    test_piece.move(board, 3, 2)
    board.print_board()
    print(test_piece.get_valid_moves(board))
