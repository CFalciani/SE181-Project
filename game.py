import pygame
import numpy as np


class Game:
    def __init__(self):

        self.board = np.zeros((8,8))
        self.square_size = 100
        self.white_color = (255,255,255)
        self.black_color = (0,0,0)
        self.window = pygame.display.set_mode(
            (self.board.shape[0] * self.square_size, 
            self.board.shape[1] * self.square_size))

        while 1:
            # Run the game
            self.draw_board()
            pygame.display.update()

            for event in pygame.event.get():
                # Test for any user input

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Press escape to quit
                        pygame.quit()
        
    def draw_board(self):
        self.window.fill(self.white_color)
        start = 1
        for i in range(self.board.shape[0]):
            for j in range(start, self.board.shape[1], 2):
                # Form a grid shape
                self.draw_square(self.black_color, j, i)
            start = int(not start) #Alternate a between 0 and 1

    def draw_square(self, color, x, y):
        # Input a color to make the square, 
        # and the x and y index of the board
        rect = (x * self.square_size, y * self.square_size, self.square_size, self.square_size)
        pygame.draw.rect(self.window, color, rect)

game = Game()