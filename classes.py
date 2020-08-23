from abc import ABC, abstractmethod
import numpy as np
import pygame


class Board:
    def __init__(self, square_size, sidebar):
        self.square_size = square_size
        self.sidebar = sidebar
        self.board = np.empty((8, 8), Piece)
        self.shape = self.board.shape
        self.white_pieces = []
        self.black_pieces = []
        self.white_king = None
        self.black_king = None
        self.white_spaces = np.zeros((8, 8))
        self.black_spaces = np.zeros((8, 8))
        self.en_passant = None
        self.en_passant_counter = 0
        self.check = False
        self.attacking_piece = None
        self.check_other_moves = []

    def __str__(self):
        return str(self.board)

    def flip(self, x, y):
        return 7 - x, 7 - y

    # Returns the contents of the specified space
    def get_space(self, x, y):
        return self.board[y][x]

    # Adds a piece to the board
    def add_piece(self, piece):
        self.board[piece.y][piece.x] = piece
        if piece.color == "White":
            self.white_pieces.append(piece)
            if piece.name == "King":
                self.white_king = piece
        else:
            self.black_pieces.append(piece)
            if piece.name == "King":
                self.black_king = piece

    # Removes a piece from the board
    def remove_piece(self, piece):
        self.board[piece.y][piece.x] = None
        if piece.color == "White":
            pieces = self.white_pieces
        else:
            pieces = self.black_pieces
        for i in range(len(pieces)):
            if pieces[i].x == piece.x and pieces[i].y == piece.y:
                pieces.pop(i)
                break

    # Places all pieces in their starting positions
    def fill_board(self):
        self.add_piece(Rook("Black", 0, 0))
        self.add_piece(Knight("Black", 1, 0))
        self.add_piece(Bishop("Black", 2, 0))
        self.add_piece(Queen("Black", 3, 0))
        self.add_piece(King("Black", 4, 0))
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
        self.add_piece(Queen("White", 3, 7))
        self.add_piece(King("White", 4, 7))
        self.add_piece(Bishop("White", 5, 7))
        self.add_piece(Knight("White", 6, 7))
        self.add_piece(Rook("White", 7, 7))
        for i in range(len(self.white_pieces)):
            self.white_pieces[i].get_valid_moves(self)
        for i in range(len(self.black_pieces)):
            self.black_pieces[i].get_valid_moves(self)

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
                piece = self.get_space(i, j)
                if piece is None:
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

    def get_check_moves(self):
        self.check_other_moves = []
        attacker = self.attacking_piece.name
        attack = self.attacking_piece.color
        blockable = False
        if attack == "White":
            defense = self.black_spaces
            defender = self.black_king
        else:
            defense = self.white_spaces
            defender = self.white_king
        check_king_moves = defender.get_valid_moves(self)
        self.check_other_moves.append((self.attacking_piece.x, self.attacking_piece.y))
        if defense[self.attacking_piece.y][self.attacking_piece.x] == 1:
            blockable = True
        if attacker == "Queen" or attacker == "Bishop" or attacker == "Rook":
            directions = ((0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1))
            x_dif = self.attacking_piece.x - defender.x
            y_dif = self.attacking_piece.y - defender.y
            if x_dif < 0:
                if y_dif < 0:
                    direction = directions[7]
                elif y_dif == 0:
                    direction = directions[6]
                else:
                    direction = directions[5]
            elif x_dif == 0:
                if y_dif < 0:
                    direction = directions[0]
                else:
                    direction = directions[4]
            else:
                if y_dif < 0:
                    direction = directions[1]
                elif y_dif == 0:
                    direction = directions[2]
                else:
                    direction = directions[3]
            dif = max(abs(x_dif), abs(y_dif))
            for i in range(1, dif):
                path_space = (defender.x + i * direction[0], defender.y + i * direction[1])
                self.check_other_moves.append(path_space)
                if defense[path_space[1]][path_space[0]] == 1:
                    blockable = True
        if not check_king_moves and not blockable:
            self.checkmate(attack)
            return [2,attack]
        return [0]

    def checkmate(self, winner):
        print("Checkmate")
        pass


class Piece(ABC):
    @abstractmethod
    def __init__(self, color, name, x, y):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.spaces = np.zeros((8, 8))
        self.path = "assets/" + color + name + ".png"
        self.img = pygame.image.load(self.path)
        super().__init__()

    # Returns a list of valid moves for the piece
    @abstractmethod
    def get_valid_moves(self, board, output):
        self.spaces = np.zeros((8, 8))
        for i in output:
            space = board.get_space(i[0], i[1])
            if space is not None and space.color != self.color and space.name == "King":
                self.spaces[i[1]][i[0]] = 1
                board.check = True
                board.attacking_piece = self
            else:
                self.spaces[i[1]][i[0]] = 1
            if self.color == "White":
                total_spaces = board.white_spaces
            else:
                total_spaces = board.black_spaces
            if self.name == "King" and total_spaces[i[1]][i[0]] == 0:
                total_spaces[i[1]][i[0]] = 2
            else:
                total_spaces[i[1]][i[0]] = 1
        if board.check and self.name != "King":
            restricted_output = []
            for i in output:
                for u in board.check_other_moves:
                    if i == u:
                        restricted_output.append(i)
            return restricted_output
        else:
            return output

    # Moves the piece to the specified space
    def move(self, board, new_x, new_y):
        captured = False
        board.check = False
        board.white_spaces = np.zeros((8, 8))
        board.black_spaces = np.zeros((8, 8))
        if board.en_passant_counter > 0:
            board.en_passant_counter -= 1
        if board.en_passant_counter == 0 and board.en_passant is not None:
            board.en_passant.en_passant = False
            board.en_passant = None
        other_piece = board.get_space(new_x, new_y)
        if other_piece is not None:
            captured = True
            board.remove_piece(other_piece)
        board.board[self.y][self.x] = None
        board.board[new_y][new_x] = self
        self.x = new_x
        self.y = new_y
        for i in range(len(board.white_pieces)):
            if board.white_pieces[i].name != "King":
                board.white_pieces[i].get_valid_moves(board)
        for i in range(len(board.black_pieces)):
            if board.black_pieces[i].name != "King":
                board.black_pieces[i].get_valid_moves(board)
        board.white_king.get_valid_moves(board)
        board.black_king.get_valid_moves(board)
        if board.check:
            return [*board.get_check_moves()]
        if captured:
            return [1, other_piece]
        return [0]

    def __str__(self):
        return "%s %s" % (self.color, self.name)


class Queen(Piece):
    def __init__(self, color, x, y):
        self.name = "Queen"
        super().__init__(color, self.name, x, y)

    def get_valid_moves(self, board, output=None):
        output = []
        if self.color == "White":
            spaces = board.white_spaces
        else:
            spaces = board.black_spaces

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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
                    break

        return super().get_valid_moves(board, output)


class Pawn(Piece):
    def __init__(self, color, x, y):
        self.name = "Pawn"
        super().__init__(color, self.name, x, y)
        self.moved = False
        self.en_passant = False
        if color == "White":
            self.direction = -1
        else:
            self.direction = 1

    def get_valid_moves(self, board, output=None):
        output = []
        if self.color == "White":
            spaces = board.white_spaces
        else:
            spaces = board.black_spaces

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
            elif space is not None and space.color == self.color:
                spaces[new_y][new_x] = 1

        new_x = self.x + 1
        new_y = self.y + self.direction
        if new_x < board.shape[1]:
            space = board.get_space(new_x, new_y)
            if space is not None and space.color != self.color:
                output.append((new_x, new_y))
            elif space is not None and space.color == self.color:
                spaces[new_y][new_x] = 1

        if board.en_passant is not None and board.en_passant.color != self.color and board.en_passant.y == self.y:
            if board.en_passant.x == self.x - 1:
                output.append((self.x - 1, self.y + self.direction))
            elif board.en_passant.x == self.x + 1:
                output.append((self.x + 1, self.y + self.direction))

        return super().get_valid_moves(board, output)

    def move(self, board, new_x, new_y):
        if new_x != self.x and board.get_space(new_x, new_y) is None:
            board.remove_piece(board.get_space(new_x, new_y - self.direction))
        return_value = super().move(board, new_x, new_y)
        if not self.moved and (new_y == 3 or new_y == 4):
            self.en_passant = True
            board.en_passant = self
        self.moved = True
        if new_y == 0 or new_y == 7:
            return [3, return_value]
        else:
            return return_value


class Rook(Piece):
    def __init__(self, color, x, y):
        self.name = "Rook"
        super().__init__(color, self.name, x, y)
        self.moved = False

    def get_valid_moves(self, board, output=None):
        output = []
        if self.color == "White":
            spaces = board.white_spaces
        else:
            spaces = board.black_spaces

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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
                    break

        return super().get_valid_moves(board, output)

    def move(self, board, new_x, new_y):
        return_value = super().move(board, new_x, new_y)
        self.moved = True
        return return_value


class Bishop(Piece):
    def __init__(self, color, x, y):
        self.name = "Bishop"
        super().__init__(color, self.name, x, y)

    def get_valid_moves(self, board, output=None):
        output = []
        if self.color == "White":
            spaces = board.white_spaces
        else:
            spaces = board.black_spaces

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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
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
                    else:
                        spaces[new_y][new_x] = 1
                    break

        return super().get_valid_moves(board, output)


class Knight(Piece):
    def __init__(self, color, x, y):
        self.name = "Knight"
        super().__init__(color, self.name, x, y)

    def get_valid_moves(self, board, output=None):
        output = []
        if self.color == "White":
            spaces = board.white_spaces
        else:
            spaces = board.black_spaces

        new_x = self.x + 1
        new_y = self.y - 2
        if not (new_x > (board.shape[1] - 1) or new_y < 0):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))
            elif space is not None and space.color == self.color:
                spaces[new_y][new_x] = 1

        new_x = self.x + 2
        new_y = self.y - 1
        if not (new_x > (board.shape[1] - 1) or new_y < 0):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))
            elif space is not None and space.color == self.color:
                spaces[new_y][new_x] = 1

        new_x = self.x + 2
        new_y = self.y + 1
        if not (new_x > (board.shape[1] - 1) or new_y > (board.shape[0] - 1)):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))
            elif space is not None and space.color == self.color:
                spaces[new_y][new_x] = 1

        new_x = self.x + 1
        new_y = self.y + 2
        if not (new_x > (board.shape[1] - 1) or new_y > (board.shape[0] - 1)):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))
            elif space is not None and space.color == self.color:
                spaces[new_y][new_x] = 1

        new_x = self.x - 1
        new_y = self.y + 2
        if not (new_x < 0 or new_y > (board.shape[0] - 1)):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))
            elif space is not None and space.color == self.color:
                spaces[new_y][new_x] = 1

        new_x = self.x - 2
        new_y = self.y + 1
        if not (new_x < 0 or new_y > (board.shape[0] - 1)):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))
            elif space is not None and space.color == self.color:
                spaces[new_y][new_x] = 1

        new_x = self.x - 2
        new_y = self.y - 1
        if not (new_x < 0 or new_y < 0):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))
            elif space is not None and space.color == self.color:
                spaces[new_y][new_x] = 1

        new_x = self.x - 1
        new_y = self.y - 2
        if not (new_x < 0 or new_y < 0):
            space = board.get_space(new_x, new_y)
            if space is None or space.color != self.color:
                output.append((new_x, new_y))
            elif space is not None and space.color == self.color:
                spaces[new_y][new_x] = 1

        return super().get_valid_moves(board, output)


class King(Piece):
    def __init__(self, color, x, y):
        self.name = "King"
        super().__init__(color, self.name, x, y)
        self.moved = False

    def get_valid_moves(self, board, output=None):
        output = []
        if self.color == "White":
            spaces = board.white_spaces
            blocked_spaces = board.black_spaces
        else:
            spaces = board.black_spaces
            blocked_spaces = board.white_spaces

        # Up
        new_x = self.x
        new_y = self.y - 1
        if new_y >= 0:
            if blocked_spaces[new_y][new_x] == 0:
                space = board.get_space(new_x, new_y)
                if space is None or space.color != self.color:
                    output.append((new_x, new_y))
            elif spaces[new_y][new_x] == 0:
                spaces[new_y][new_x] = 2

        # Up-Right
        new_x = self.x + 1
        new_y = self.y - 1
        if new_x < board.shape[1] and new_y >= 0:
            if blocked_spaces[new_y][new_x] == 0:
                space = board.get_space(new_x, new_y)
                if space is None or space.color != self.color:
                    output.append((new_x, new_y))
            elif spaces[new_y][new_x] == 0:
                spaces[new_y][new_x] = 2

        # Right
        new_x = self.x + 1
        new_y = self.y
        if new_x < board.shape[1]:
            if blocked_spaces[new_y][new_x] == 0:
                space = board.get_space(new_x, new_y)
                if space is None or space.color != self.color:
                    output.append((new_x, new_y))
            elif spaces[new_y][new_x] == 0:
                spaces[new_y][new_x] = 2

        # Down-Right
        new_x = self.x + 1
        new_y = self.y + 1
        if new_x < board.shape[1] and new_y < board.shape[0]:
            if blocked_spaces[new_y][new_x] == 0:
                space = board.get_space(new_x, new_y)
                if space is None or space.color != self.color:
                    output.append((new_x, new_y))
            elif spaces[new_y][new_x] == 0:
                spaces[new_y][new_x] = 2

        # Down
        new_x = self.x
        new_y = self.y + 1
        if new_y < board.shape[0]:
            if blocked_spaces[new_y][new_x] == 0:
                space = board.get_space(new_x, new_y)
                if space is None or space.color != self.color:
                    output.append((new_x, new_y))
            elif spaces[new_y][new_x] == 0:
                spaces[new_y][new_x] = 2

        # Down-Left
        new_x = self.x - 1
        new_y = self.y + 1
        if new_x >= 0 and new_y < board.shape[0]:
            if blocked_spaces[new_y][new_x] == 0:
                space = board.get_space(new_x, new_y)
                if space is None or space.color != self.color:
                    output.append((new_x, new_y))
            elif spaces[new_y][new_x] == 0:
                spaces[new_y][new_x] = 2

        # Left
        new_x = self.x - 1
        new_y = self.y
        if new_x >= 0:
            if blocked_spaces[new_y][new_x] == 0:
                space = board.get_space(new_x, new_y)
                if space is None or space.color != self.color:
                    output.append((new_x, new_y))
            elif spaces[new_y][new_x] == 0:
                spaces[new_y][new_x] = 2

        # Up-Left
        new_x = self.x - 1
        new_y = self.y - 1
        if new_x >= 0 and new_y >= 0:
            if blocked_spaces[new_y][new_x] == 0:
                space = board.get_space(new_x, new_y)
                if space is None or space.color != self.color:
                    output.append((new_x, new_y))
            elif spaces[new_y][new_x] == 0:
                spaces[new_y][new_x] = 2

        # Castling
        if not self.moved:
            left_corner = board.get_space(0, self.y)
            right_corner = board.get_space(7, self.y)
            if left_corner is not None and left_corner.color == self.color and left_corner.name == "Rook" \
                    and not left_corner.moved and board.get_space(1, self.y) is None \
                    and board.get_space(2, self.y) is None and board.get_space(3, self.y) is None \
                    and blocked_spaces[self.y][0] == 0:
                output.append((2, self.y))
            if right_corner is not None and right_corner.color == self.color and right_corner.name == "Rook" \
                    and not right_corner.moved and board.get_space(5, self.y) is None \
                    and board.get_space(6, self.y) is None and blocked_spaces[self.y][7] == 0:
                output.append((6, self.y))

        return super().get_valid_moves(board, output)

    def move(self, board, new_x, new_y):
        if not self.moved:
            if new_x == 2:
                rook = board.get_space(0, self.y)
                board.board[self.y][0] = None
                board.board[self.y][3] = rook
                rook.x = 3
                rook.y = self.y
            elif new_x == 6:
                rook = board.get_space(7, self.y)
                board.board[self.y][7] = None
                board.board[self.y][5] = rook
                rook.x = 5
                rook.y = self.y
        return_value = super().move(board, new_x, new_y)
        self.moved = True
        return return_value


# Testing
if __name__ == "__main__":
    board = Board(100, 250)
    board.fill_board()
    print("Intial board:\n")
    board.print_board()
    
    # TEST 5.1: Queen
    print("\nQUEEN TESTS...\n")
    board.get_space(3, 6).move(board, 3, 4)
    board.get_space(3, 7).move(board, 3, 5)
    board.print_board()
    print("\nTesting valid moves for White Queen:")
    # White Queen at D3
    # Valid Moves:  [(4, 4), (5, 3), (6, 2), (7, 1), (4, 5), (5, 5), (6, 5), (7, 5), (3, 6), (3, 7), (2, 5), (1, 5), (0, 5), (2, 4), (1, 3), (0, 2)]
    print(board.get_space(3, 5).get_valid_moves(board))

    # Move pawn to (2, 3) to test that jumps aren't valid moves
    board.get_space(2, 6).move(board, 2, 5)
    board.print_board()
    print("\nTesting jump moves for White Queen:")
    # Valid Moves: [(4, 4), (5, 3), (6, 2), (7, 1), (4, 5), (5, 5), (6, 5), (7, 5), (3, 6), (3, 7), (2, 4), (1, 3), (0, 2)]
    print(board.get_space(3, 5).get_valid_moves(board))

    # Move white queen to f8 to test pawn capture
    board.print_board()
    print("\nTesting queen pawn capture:")
    capturedPiece = board.get_space(3, 5).move(board, 7, 1)[1].name
    print(capturedPiece, "was captured")
    board.print_board()
    print("END OF QUEEN TESTS\n\n")



    # TEST 5.2: Pawn
    # new board
    board.remove_piece(board.get_space(2, 5))
    board.remove_piece(board.get_space(3, 4))
    board.fill_board()
    print("\nPAWN TESTS...\n")
    board.print_board()
    print("\nTesting initial valid moves for Pawn:")

    # move black pawn 2 spaces forward and white pawn 1 space
    board.get_space(3, 6).move(board, 3, 5)
    board.get_space(3, 1).move(board, 3, 3)

    # White pawn at e1
    # valid moves: [(4,5), (4,4)]
    print(board.get_space(4, 6).get_valid_moves(board))
    board.get_space(4, 6).move(board, 4, 4)
    # black pawn at e6
    # valid moves: [(4,2), (4,3)]
    print(board.get_space(4, 1).get_valid_moves(board))
    board.get_space(4, 1).move(board, 4, 3)
    board.print_board()

    # test diagonal pawn capture
    # white pawn at e3, black pawn at d4
    # valid moves: [(3,3)]
    print("\nTesting pawn capture:")
    print(board.get_space(4, 4).get_valid_moves(board))
    # Move white pawn to d4 to test pawn capture
    capturedPiece = board.get_space(4, 4).move(board, 3, 3)[1].name
    print(capturedPiece, "was captured")
    board.print_board()

    # test en passant
    print("\nTesting en passant:")
    board.get_space(2, 1).move(board, 2, 3)
    board.print_board()
    print(board.get_space(3, 3).get_valid_moves(board))
    # Move white pawn to c5 to test en passant pawn capture
    print(board.get_space(3, 3).move(board, 2, 2))
    # print(capturedPiece, "was captured") 
    board.print_board()

    # Move black pawn to g4 to test en passant pawn capture 
    board.get_space(6, 1).move(board, 6, 4)
    board.get_space(7, 7).move(board,7, 4)
    # valid moves: [(6, 5), (7,5)]
    print(board.get_space(6, 4).get_valid_moves(board))
    print(board.get_space(6, 4).move(board, 7, 5))
    # print(capturedPiece, "was captured") 
    board.print_board()


    # test pawn promotion 
    board.get_space(2, 0).move(board, 1, 3)
    # should return (3, [0])
    print(board.get_space(2, 2).move(board, 2, 0))
