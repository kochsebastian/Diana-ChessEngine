import tkinter as tk
from PIL import ImageTk

BOARD_SIZE = 6


class BoardGuiTk(tk.Frame):
    pieces = {}
    selected = None
    selected_piece = None
    hilighted = None
    icons = {}

    color1 = "white"
    color2 = "grey"

    rows = BOARD_SIZE
    columns = BOARD_SIZE
    
    current_engine_thread = None
    label = None

    @property
    def canvas_size(self):
        return (self.columns * self.square_size,
                self.rows * self.square_size)

    def __init__(self, parent, chessboard, square_size=64):
        
        self.chessboard = chessboard
        self.square_size = square_size
        self.parent = parent

        canvas_width = self.columns * square_size
        canvas_height = self.rows * square_size

        tk.Frame.__init__(self, parent)

        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height, background="grey")
        self.canvas.pack(side="top", fill="both", anchor="c", expand=True)

        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind("<Button-1>", self.click)

        
        self.statusbar = tk.Frame(self, height=64)
        """
        self.button_quit = tk.Button(self.statusbar, text="New", fg="black", command=self.reset)
        self.button_quit.pack(side=tk.LEFT, in_=self.statusbar)

        self.button_save = tk.Button(self.statusbar, text="Save", fg="black", command=self.chessboard.save_to_file)
        self.button_save.pack(side=tk.LEFT, in_=self.statusbar)
        """
        
        self.label_status = tk.Label(self.statusbar, text="   White's turn  ", fg="black")
        self.label_status.pack(side=tk.LEFT, expand=0, in_=self.statusbar)
        
        self.button_quit = tk.Button(self.statusbar, text="Quit", fg="black", command=self.quit_app)
        self.button_quit.pack(side=tk.RIGHT, in_=self.statusbar)
        self.statusbar.pack(expand=False, fill="x", side='bottom')
        
        
    def quit_app(self):

        self.chessboard.end_game(self)
        self.parent.destroy()
        

        
    # what happens when user clicks on board
    def click(self, event):
        

        
        if not self.chessboard.game_ended:

            if ((self.chessboard.player_turn == "white" and self.chessboard.PLAYER_1==1) or
               (self.chessboard.player_turn == "black" and self.chessboard.PLAYER_2==1)):
                # Figure out which square we've clicked
                col_size = row_size = event.widget.master.square_size

                current_column = event.x / col_size
                current_row = (BOARD_SIZE-1) - (event.y / row_size)

                #print("Click: ", current_row,current_column)

                position = self.chessboard.letter_notation((current_row, current_column))
                piece = self.chessboard[position]
                
                if self.selected_piece:
                    from_piece_position = self.selected_piece[1]
                    
                    if from_piece_position == position:
                        self.remove_highlighting()
                        return
                    valid_move = self.move(self.selected_piece[1], position)
                    
                    if not valid_move:
                        self.remove_highlighting()
                        return
                    
                    """
                    pawn, rook, knight ,bishop, king = self.chessboard.is_in_check(self.chessboard.player_turn)
                    
                    print("Situation for: ", self.chessboard.player_turn)
                    print("Pawn kills: ", pawn)
                    print("Rook kills: ", rook)
                    print("Knight kills: ", knight)
                    print("Bishop kills: ", bishop)
                    print("King kills: ", king)

                    pawn, rook, knight ,bishop, king = self.chessboard.is_in_check(self.chessboard.get_enemy(self.chessboard.player_turn))
                    print("Situation for: ", self.chessboard.get_enemy(self.chessboard.player_turn))
                    print("Pawn kills: ", pawn)
                    print("Rook kills: ", rook)
                    print("Knight kills: ", knight)
                    print("Bishop kills: ", bishop)
                    print("King kills: ", king)
                    """
                    self.chessboard.is_in_check(self.chessboard.get_enemy(self.chessboard.player_turn))
                    
                    
                    self.remove_highlighting()

                    movetext = (from_piece_position, position)
                    print(self.chessboard.get_enemy(self.chessboard.player_turn), " chose move: ",movetext)
                    self.chessboard.pprint()
                
                self.hilight(position)
                self.refresh()

    def move(self, p1, p2):
        piece = self.chessboard[p1]
        dest_piece = self.chessboard[p2]
        if dest_piece is None or dest_piece.color != piece.color:
                valid = self.chessboard.move(p1,p2,self)
                self.label_status["text"] = " " + piece.color.capitalize() +": "+ p1 + p2
                return valid

    def remove_highlighting(self):
        self.selected_piece = None
        self.hilighted = None
        self.pieces = {}
        self.refresh()
        self.draw_pieces()

                
    def hilight(self, pos):
        piece = self.chessboard[pos]
        if piece is not None and (piece.color == self.chessboard.player_turn):
            self.selected_piece = (self.chessboard[pos], pos)
            
            self.hilighted = [(pos,move) for move in self.chessboard[pos].possible_moves(pos)]
            self.hilighted = self.chessboard.is_in_check_after_move_filter(self.hilighted) 
            self.hilighted = [self.chessboard.number_notation(move[1]) for move in self.hilighted]

    def addpiece(self, name, image, row=0, column=0):
        '''Add a piece to the playing board'''
        self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c")
        self.placepiece(name, row, column)

    def placepiece(self, name, row, column):
        '''Place a piece at the given row/column'''
        self.pieces[name] = (row, column)
        x0 = (column * self.square_size) + int(self.square_size/2)
        y0 = (((BOARD_SIZE-1)-row) * self.square_size) + int(self.square_size/2)
        self.canvas.coords(name, x0, y0)

        
    def refresh(self, event={}):
        '''Redraw the board'''
        if event:
            xsize = int((event.width-1) / self.columns)
            ysize = int((event.height-1) / self.rows)
            self.square_size = min(xsize, ysize)

        self.canvas.delete("square")
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = (col * self.square_size)
                y1 = (((BOARD_SIZE-1)-row) * self.square_size)
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                if (self.selected_piece is not None) and self.chessboard.letter_notation((row, col)) == self.selected_piece[1]:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="orange", tags="square")
                elif(self.hilighted is not None and (row, col) in self.hilighted):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="spring green", tags="square")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2
        for name in self.pieces:
            self.placepiece(name, self.pieces[name][0], self.pieces[name][1])
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")
        
    
    def draw_pieces(self):
        self.canvas.delete("piece")
        for coord, piece in self.chessboard.items():
            x,y = self.chessboard.number_notation(coord)
            if piece is not None:
                filename = "./img/%s%s.png" % (piece.color, piece.abbriviation.lower())
                piecename = "%s%s%s" % (piece.abbriviation, x, y)
                

                if(filename not in self.icons):
                    self.icons[filename] = ImageTk.PhotoImage(file=filename, width=32, height=32)
                
                self.addpiece(piecename, self.icons[filename], x, y)
                self.placepiece(piecename, x, y)
    
    def perform_move(self):
        board = self.chessboard
        gui = self
        
        
        if (board.next_move is None):
            print("Engine wants to perform None: ", board.get_enemy(board.player_turn), " won!")
            self.label.configure(text="Engine wants to perform None: " + board.get_enemy(board.player_turn) + " won!")
            board.end_game(self)
        else:
            piece = board[board.next_move[0]]

            if not (board.next_move[1] in piece.possible_moves(board.next_move[0])):
                print("Invalid move chosen: ", board.get_enemy(board.player_turn), "wins!")
            else:
                print(board.player_turn," chose move: ", board.next_move)
                self.move(board.next_move[0],board.next_move[1])
                gui.selected_piece = None
                gui.hilighted = None
                gui.pieces = {}
                gui.refresh()
                gui.draw_pieces()
                #gui.refresh()

                board.pprint()
                #print(self.get_enemy(self.player_turn), ": ", movetext, "\n\n")
                board.next_move = None
