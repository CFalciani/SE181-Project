from classes import *
import pygame
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time

class Game:
    def __init__(self):
        pygame.init()
        self.messageAvailable = False # set to true if a new message is recieved. Should be set to false once read
        self.message = "" # Contains the new message, will be overwritten only when messageAvailable is false
        self.team = "" # Will be set with wich team the player is on upon connection. Eg: "white" or "black"
        self.ready = False # Are both players connected?
        self.my_turn = False # True if it is this players turn
        #websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("ws://claytonfalciani.com", # Connect the web server to my server
                                on_message = lambda ws,msg: self.on_message(ws,msg), # Function to handle messages
                                on_error = lambda ws,err: self.on_error(ws,err), #Function to handle errors
                                on_close = lambda ws: self.on_close(ws), #Function to handle close the server
                                on_open = lambda ws: self.on_open(ws)) # Function to handle opening the server

        #UNCOMMENT BELOW LINE TO CONNECT TO SERVER!
        thread.start_new_thread(self.ws.run_forever, ()) # Start listening for messages on a new thread so we don't block the game
        self.square_size = 100
        self.white_color = (240,240,240)
        self.black_color = (20,20,20)
        self.sidebar_size = 250
        self.left_sidebar = self.sidebar_size # X coordinate of the left side bar (it starts at 0 and ends at this point)
        self.board = Board(self.square_size, self.sidebar_size)
        self.board.fill_board()
        self.right_sidebar = self.sidebar_size + self.board.shape[0] * self.square_size # X coordinate of the right sidebar
        self.header_font = pygame.font.Font('freesansbold.ttf', int(self.board.shape[1] * self.square_size * .03))
        self.text_font = pygame.font.Font('freesansbold.ttf', int(self.board.shape[1] * self.square_size * .015))
        #self.team = "white"
        self.moves = []
        self.selected_piece = None
        # Text format: (coords, string, text_color, font)
        self.activity_texts = [((0,0),"Activity Log", (134,134,134), self.header_font)] # Append to this list to add text to the screen
        self.horizontal_label = []
        self.vertical_label = []

        self.window = pygame.display.set_mode(
            (self.board.shape[0] * self.square_size + self.sidebar_size * 2, 
            (self.board.shape[1] + 1) * self.square_size))

        #MAIN MENU COMPONENTS
        #Conecting Animation images
        self.loadingAnimation = []
        self.chessAnimation = []
        for i in range(0, 31):
            self.loadingAnimation.append(pygame.image.load("assets/connectingAnimation/frame-" + str(i) + ".png"))
            self.chessAnimation.append(pygame.image.load("assets/chessAnimation/frame-" + str(i) + ".png"))
        self.frame = 0

        while 1:
            if (self.ready):
                # Run the game
                if self.messageAvailable: # check if theres a message available
                    print(self.message) 
                    self.activity_texts.append(((0, self.activity_texts[-1][0][1] + 30), "Opponent: " + self.message, (134,134,134), self.text_font))
                    # And processing with the message should go here
                    origin = ord(self.message[0]) - 97, int(self.message[1])
                    dest = ord(self.message[3]) - 97, int(self.message[4])
                    piece = self.board.get_space(*origin)
                    piece.move(self.board, *dest)
                    self.messageAvailable = False # make sure to tell the game you have read the message
                    self.my_turn = True

                self.draw()

                for event in pygame.event.get():
                    # Test for any user input
                    if event.type == pygame.MOUSEBUTTONUP:
                        if self.my_turn:
                            coords = pygame.mouse.get_pos()
                            if self.left_sidebar < coords[0] < self.right_sidebar:
                                if self.team == "black":
                                    square = self.board.flip(*self.coords_to_square(coords))
                                else:
                                    square = self.coords_to_square(coords)
                                if square in self.moves:
                                    move_str = chr(self.selected_piece.x + 97) + str(self.selected_piece.y) + " " + chr(square[0] + 97) + str(square[1])
                                    self.ws.send(move_str)
                                    self.selected_piece.move(self.board, *square)  
                                    self.selected_piece = None
                                    self.moves = []
                                    self.my_turn = False
                                    continue
                                self.selected_piece = self.board.get_space(*square)
                                
                                if self.selected_piece is not None and self.selected_piece.color.lower() == self.team.lower():
                                    self.moves = self.selected_piece.get_valid_moves(self.board)
                                else:
                                    self.selected_piece = None
                                    self.moves = []
                            else:
                                self.selected_piece = None
                                self.moves = []
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            # Press escape to quit
                            try:
                                self.ws.send("quit")
                            except websocket._exceptions.WebSocketConnectionClosedException:
                                pass
                            pygame.quit()
                            quit()
            #Main Menu               
            else:
                self.drawMainMenu()
                
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            # Press escape to quit
                            try:
                                self.ws.send("quit")
                            except websocket._exceptions.WebSocketConnectionClosedException:
                                pass
                            pygame.quit()
                            quit()

    def drawMainMenu(self):
        self.window.fill(self.white_color)

        #Text
        loadingText = self.text_font.render("Waiting for other player to connect...", True, (255,0,0), self.white_color)
        self.window.blit(loadingText, (550, 340))

        #Title & Connecting animation
        pygame.time.delay(25)
        self.window.blit(self.loadingAnimation[self.frame], (540, 400))
        self.window.blit(self.chessAnimation[self.frame], (505, 150))
        self.frame += 1
        if (self.frame > 30):
            self.frame = 0
    
        pygame.display.update()
        

    def draw(self):
        self.draw_board()
        text = self.header_font.render("Your Turn" if self.my_turn else "Opponents Turn", True, (255,0,0), self.white_color)
        self.window.blit(text, (self.right_sidebar + 20,0))
        for text in self.activity_texts:
            self.draw_text(*text)
        for move in self.moves:
            if self.team == "black":
                self.draw_square((150,180,255), *self.board.flip(*move))
            else:
                self.draw_square((150,180,255), *move)
        if self.team == "black":
            self.board.draw_rev(self.window)
        else:
            self.board.draw(self.window)
        pygame.display.update()
    
    def draw_board(self):
        self.window.fill(self.white_color)
        start = 1
        for i in range(self.board.shape[0]):
            for j in range(start, self.board.shape[1], 2):
                # Form a grid shape
                self.draw_square(self.black_color, j, i)
            start = int(not start) #Alternate a between 0 and 1
        #Draw the border lines on the left and right sidebar
        pygame.draw.line(self.window, (0,0,0), (self.left_sidebar,0), (self.left_sidebar, self.board.shape[1] * self.square_size), 2)
        pygame.draw.line(self.window, (0,0,0), (self.right_sidebar,0), (self.right_sidebar, self.board.shape[1] * self.square_size), 2)
        pygame.draw.line(self.window, (0,0,0), (self.left_sidebar, self.board.shape[1] * self.square_size), (self.right_sidebar, self.board.shape[1] * self.square_size), 2)
        for index,label in enumerate(self.vertical_label):
            self.window.blit(label, (self.left_sidebar - 100, index * self.square_size))
        for index,label in enumerate(self.horizontal_label):
            self.window.blit(label, (self.left_sidebar + (index - 1) * self.square_size, self.board.shape[1]))

    def draw_text(self, coords, text, color, font):
        text = font.render(text, True, color, self.white_color)
        self.window.blit(text, coords)

    def draw_square(self, color, x, y):
        # Input a color to make the square, 
        # and the x and y index of the board
        corner = self.get_corner_coords(x,y)
        rect = (corner[0], corner[1], self.square_size, self.square_size)
        pygame.draw.rect(self.window, color, rect)

    def get_corner_coords(self, x, y):
        return x * self.square_size + self.sidebar_size, y*self.square_size

    def get_center_coords(self, x, y):
        corner = self.get_corner_coords(x,y)
        return (corner[0] + (self.square_size // 2)), (corner[1] + (self.square_size // 2))

    def coords_to_square(self, coords):
        x = (coords[0] - self.left_sidebar) // self.square_size
        y = coords[1] // self.square_size
        return x,y

    def on_message(self,ws, incMessage):
        if "Waiting for opponent" == incMessage:
            print("Waiting...")
            return
        if "You are team" in incMessage: # Means that both players are connected
            self.team = incMessage.split(": ")[-1] #Grab the team this client is on
            print("You are on team: " + self.team)
            self.ready = True # Both players are in so we are ready to start
            self.my_turn = (self.team == "white")
            return 
        if "quit" == incMessage:
            print("Opponent Quit!")
            return
        while (self.messageAvailable == True):
            pass # We need to wait for the client to read the message before overwriting it
        self.messageAvailable = True 
        self.message = incMessage

    def on_error(self,ws,error):
        err = str(error)
        if err == "[Errno -2] Name or service not known": # DNS resolve error or client not connected to internet
            print("ERROR: Please check your network, there was an error connecting to the server")
        elif err == "[Errno 111] Connection refused": # Server did not except the request. Maybe the server is not running?
            print("ERROR: Had a hard time connecting to the server, contact the server admin.")
        else:
            print(error)

    def on_close(self, ws):
        print("Connection closed!")

    def on_open(self, ws):
        def heartbeat(): # A heartbeat so the server knows the client is still alive
            while 1:
                try:
                    self.ws.send("hb")
                except websocket._exceptions.WebSocketConnectionClosedException:
                    break
                time.sleep(2)
        thread.start_new_thread(heartbeat, ())

game = Game()
