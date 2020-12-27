from copy import deepcopy, copy
import time
import math
import re
from pieces import *


# Board width and height
BOARD_SIZE = 6

class ChessError(Exception): pass
class InvalidCoord(ChessError): pass
class InvalidColor(ChessError): pass
class InvalidMove(ChessError): pass
class Check(ChessError): pass
class CheckMate(ChessError): pass
class Draw(ChessError): pass
class NotYourTurn(ChessError): pass

# helpful to check if a position like 'A4' is a valid one
RANK_REGEX = re.compile(r"^[A-Z][1-"+str(BOARD_SIZE)+"]$")

class Board(dict):
    '''
       Board

       A simple chessboard class

    '''
    
    board_states = []
    
    # both axes of the board
    axis_y = tuple([chr(ord('A')+i) for i in range(BOARD_SIZE)])
    axis_x = tuple(range(1,BOARD_SIZE+1)) # (1,2,3,...8)

    player_turn = None
    
    # counting the moves (1 move = white and black have moved)
    fullmove_number = 1
    
    # this is where the move that the agent updates is saved
    next_move = None
    # the clock saves the current time left in this variable
    timer = None
    
    # flag to check whether or not the agent has finished
    engine_is_selecting = False
    
    # default during init.: Human players
    PLAYER_1 = None
    PLAYER_2 = None
    
    # flag to check end of the game (avoid user or engine input after game end)
    game_ended = False

    
    # --------------------------------Most important methods (functionality, evaluation of board)--------------------------------
    
    
    # Does not return timer
    # Returns state variables for copying
    def get_current_state(self):
        return self.player_turn, self.fullmove_number
    
    # ---------------------------------------functionality
    
    # moves the figure at p1 to p2 (e.g. p1 = 'A5', p2 = 'A7')
    # gui only used for output
    
    def move(self, p1, p2, gui=None):
        
        #print(p1)
        #print(p2)
        p1, p2 = p1.upper(), p2.upper()
        piece = self[p1]
        dest  = self[p2]

        #print(p1,  "   ", p2)
        
        if self.player_turn != piece.color:
            raise NotYourTurn("Not " + piece.color + "'s turn!")

        enemy = self.get_enemy(piece.color)
        possible_moves = piece.possible_moves(p1)

        # 0. Check if p2 is in the possible moves
        if p2 not in possible_moves:
            return False

        #print(self.all_possible_moves(enemy))
        
        # If enemy has any moves look for check
        if self.all_possible_moves(enemy):
            if self.is_in_check_after_move(p1,p2):
                return False

        #print(p1,p2)
        self._do_move(p1, p2)
        self.switch_players()
        
        game_ends = self.check_winning_condition(piece.color,True,True,gui)
        
        return True
    
    # this marks the end of the game and stops the agent's calculations
    def end_game(self,gui):
        board = self
        thread = gui.current_engine_thread
        
        board.game_ended = True
        if thread is not None:
            thread.kill()
            thread.join()
            gui.current_engine_thread = None
    
    def update_move(self,move):
        self.next_move = move
        
    # Pretty print board
    def pprint(self):
        
        print("\n")
        
        
        col = BOARD_SIZE
        row = BOARD_SIZE
        
        row_placement = str(row)+" "
        for coord in self.keys():
            
            #print(coord)
            
            if col == 0:
                
                print(row_placement)
                
                col = BOARD_SIZE
                row -= 1
                row_placement = str(row)+" "
                
            piece = self[coord]
            
            if piece is not None:
                color = piece.color
                fig = piece.abbriviation
                row_placement += "["+ fig +"]"
            else:
                row_placement += "["+ " " + "]"
                
            col -= 1
            
        print(row_placement)      
        
        letters = [chr(ord('A')+i) for i in range(BOARD_SIZE)]
        last_row = "  "
        for letter in letters:
            last_row += " "+letter+" "
        print(last_row)
        print("\n")
        
    def to_string(self):
        
        state = ""
        
        state += "\n"
        
        
        col = BOARD_SIZE
        row = BOARD_SIZE
        
        row_placement = str(row)+" "
        for coord in self.keys():
            
            #print(coord)
            
            if col == 0:
                
                state += row_placement
                state += "\n"
                
                col = BOARD_SIZE
                row -= 1
                row_placement = str(row)+" "
                
            piece = self[coord]
            
            if piece is not None:
                color = piece.color
                fig = piece.abbriviation
                row_placement += "["+ fig +"]"
            else:
                row_placement += "["+ " " + "]"
                
            col -= 1
            
        state += row_placement
        state += "\n"
                
        
        
        letters = [chr(ord('A')+i) for i in range(BOARD_SIZE)]
        last_row = "  "
        for letter in letters:
            last_row += " "+letter+" "

        state += last_row
        state += "\n"
        
        return state
    
    def switch_players(self):
        color = self.player_turn
        enemy = self.get_enemy(color)
        if color == 'black':
            self.fullmove_number += 1
        self.player_turn = enemy
        
    def _do_move(self, p1, p2):
        
        '''
            Move a piece without validation
        '''
        
        piece = self[p1]
        dest  = self[p2]
        
        self[p1] = None
        self[p2] = piece
        
        # Check Promotion
        number_coord = self.number_notation(p2)
        if piece.color == "white" and piece.abbriviation == "P" and number_coord[0] == BOARD_SIZE-1:
            self[p2] = Rook("white")
            self[p2].place(self)
        elif piece.color == "black" and piece.abbriviation == "p" and number_coord[0] == 0:
            self[p2] = Rook("black")
            self[p2].place(self)
        


    def generate_move_text(self, p1, p2):
        '''
            Set next player turn, count moves, log moves, etc.
        '''
        
        _from = self[p1]
        _to = self[p2]
        
        abbr = _from.abbriviation
        if abbr == 'P':
            # Pawn has no letter
            abbr = ''
        if _to is None:
            # No capturing
            movetext = abbr +  p2.lower()
        else:
            # Capturing
            movetext = abbr + 'x' + p2.lower()
            
    def get_time_left(self):
        return self.timer
    
    
    
    
    
    # -----------------------------------board state evaluation
        
    def is_in_check_after_move(self, p1, p2):
        # Create a temporary board
        #t1 = time.time()
        #tmp = deepcopy(self)
        #t2 = time.time()
        
        #print("is in check after move deepcopy: ", t2-t1)
        
        from_fig = self[p1]
        to_fig = self[p2]
        color = self[p1].color
        
        self._do_move(p1,p2)
        
        
        res = self.is_in_check(color)
        
        self[p1] = from_fig
        self[p2] = to_fig
        
        
        return res

    def is_in_check_after_move_filter(self,moves):
        
        filtered = []

        for m in moves:
            # Create a temporary board
            #tmp = deepcopy(self)
            from_fig = self[m[0]]
            to_fig = self[m[1]]
            color = from_fig.color
            
            self._do_move(m[0],m[1])
            if not self.is_in_check(color):
                filtered.append(m)
            
            self[m[0]] = from_fig
            self[m[1]] = to_fig
            
        return filtered
    
    def check_winning_condition(self,color,end_game=False,print_result=False,gui = None):
        
        enemy = self.get_enemy(color)
        if self.is_in_checkmate(enemy):
            if print_result:
                print("Checkmate: ", color, " won!")
            if gui is not None:
                gui.label.configure(text="Checkmate: " + color + " won!")
            if end_game and gui is not None:
                self.end_game(gui)
            return True
        elif self.fullmove_number == (50 + 1):
            if print_result:
                print("Move Count exceeded: ", color, " won!")
            if gui is not None:
                gui.label.configure(text="Move Count exceeded: " + color + " won!")
            if end_game and gui is not None:
                self.end_game(gui)
            return True
        else:
            return False
        
    def all_possible_moves(self, color):
        '''
            Return a list of `color`'s possible moves.
            Does not check for check.
        '''
        
        #print("Check no moves possible")
        
        if(color not in ("black", "white")): raise InvalidColor
        result = []
        for coord in self.keys():
            #print(coord)
            if (self[coord] is not None) and self[coord].color == color:
                moves = self[coord].possible_moves(coord)
                if moves: result += moves
        return result
    
    # returns a list of moves in the format [('A1','A4'),..], left: from, right: to
    def generate_valid_moves(self, color):
        
        
        '''
            Return a list of `color`'s possible moves.
            This one only outputs valid moves
        '''
        
        if(color not in ("black", "white")): raise InvalidColor
        result = []
        for coord in self.keys():
            #print(coord)
            if (self[coord] is not None) and self[coord].color == color:
                moves = None
                
                moves = [(coord, coord2) for coord2 in self[coord].possible_moves(coord)]
                #print(moves)
                moves = self.is_in_check_after_move_filter(moves)
                #print(moves)
                if moves: result += moves
        return result
    
    def is_in_checkmate(self, color):
        '''
            look for checkmate
        '''
        #print("Check Checkmate")
        
        if(color not in ("black", "white")): raise InvalidColor
        for p1 in self.keys():
            if (self[p1] is not None) and self[p1].color == color:
                for p2 in self[p1].possible_moves(p1):
                    if not self.is_in_check_after_move(p1,p2):
                        return False
        return True
    
    
    # manually check from the king if other pieces can attack it
    def is_in_check(self, color, debug=False):
        if(color not in ("black", "white")): raise InvalidColor
        kingPos = self.number_notation(self.get_king_position(color))
        x = kingPos[0]
        y = kingPos[1]
        enemy = self.get_enemy(color)
        
        # Pawn
        if enemy == "white":
            pawn_pos = [self.letter_notation((x-1,y-1)),self.letter_notation((x-1,y+1))]
        else:
            pawn_pos = [self.letter_notation((x+1,y-1)),self.letter_notation((x+1,y+1))]
       
        pawn_attack_list = [coord is not None and
                        self[coord] is not None and 
                        self[coord].color == enemy and 
                        (self[coord].abbriviation).upper() == "P" for coord in pawn_pos] 
        
        pawn_attack = False
        for attack in pawn_attack_list:
            pawn_attack = pawn_attack or attack
        
        # Rook
        if debug:
            print("King: ", self.letter_notation((x,y)))
            print("Rechts")
        rook_attack = False
        for i in range(int(BOARD_SIZE-1)):
            coord = self.letter_notation((x,y+(i+1)))
            if coord is not None and self[coord] is not None:
                rook_attack = rook_attack or (self[coord].color == enemy and (self[coord].abbriviation).upper() == "R")
                break
                
        if debug:
            print("Rook rechts kills: ", rook_attack)
        
        for i in range(int(BOARD_SIZE-1)):
            coord = self.letter_notation((x,y-(i+1)))
            if coord is not None and self[coord] is not None:
                rook_attack = rook_attack or (self[coord].color == enemy and (self[coord].abbriviation).upper() == "R")
                break
        if debug:
            print("Rook links kills: ", rook_attack)
            
        for i in range(int(BOARD_SIZE-1)):
            coord = self.letter_notation((x+(i+1),y))
            if coord is not None and self[coord] is not None:
                rook_attack = rook_attack or (self[coord].color == enemy and (self[coord].abbriviation).upper() == "R")
                break
        if debug:
            print("Rook oben kills: ", rook_attack)
            
        for i in range(int(BOARD_SIZE-1)):
            coord = self.letter_notation((x-(i+1),y))
            if coord is not None and self[coord] is not None:
                rook_attack = rook_attack or (self[coord].color == enemy and (self[coord].abbriviation).upper() == "R")
                break
        if debug:
            print("Rook unten kills: ", rook_attack)
        
        # King
        king_pos = [self.letter_notation((x-1,y-1)),self.letter_notation((x-1,y+1)),self.letter_notation((x+1,y-1)),self.letter_notation((x+1,y+1)),self.letter_notation((x,y-1)),self.letter_notation((x,y+1)),self.letter_notation((x-1,y)),self.letter_notation((x+1,y))]
        
        king_attack_list = [(coord is not None and
                             self[coord] is not None and 
                             self[coord].color == enemy and 
                             (self[coord].abbriviation).upper() == "K") for coord in king_pos
                           ] 
        
        king_attack = False
        for attack in king_attack_list:
            king_attack = king_attack or attack
            
        # Bishop
        bishop_attack = False
        for i in range(int(BOARD_SIZE-1)):
            coord = self.letter_notation((x+(i+1),y+(i+1)))
            if coord is not None and self[coord] is not None:
                bishop_attack = bishop_attack or (self[coord].color == enemy and (self[coord].abbriviation).upper() == "B")
                break

        for i in range(int(BOARD_SIZE-1)):
            coord = self.letter_notation((x-(i+1),y-(i+1)))
            if coord is not None and self[coord] is not None:
                bishop_attack = bishop_attack or (self[coord].color == enemy and (self[coord].abbriviation).upper() == "B")
                break

        for i in range(int(BOARD_SIZE-1)):
            coord = self.letter_notation((x+(i+1),y-(i+1)))
            if coord is not None and self[coord] is not None:
                bishop_attack = bishop_attack or (self[coord].color == enemy and (self[coord].abbriviation).upper() == "B")
                break

        for i in range(int(BOARD_SIZE-1)):
            coord = self.letter_notation((x-(i+1),y+(i+1)))
            if coord is not None and self[coord] is not None:
                bishop_attack = bishop_attack or (self[coord].color == enemy and (self[coord].abbriviation).upper() == "B")
                break

        # Knight
        knight_pos = [self.letter_notation((x-2,y-1)),self.letter_notation((x-2,y+1)),self.letter_notation((x-1,y-2)),self.letter_notation((x-1,y+2)),self.letter_notation((x+1,y-2)),self.letter_notation((x+1,y+2)),self.letter_notation((x+2,y-1)),self.letter_notation((x+2,y+1))]
        
        knight_attack_list = [(coord is not None and
                             self[coord] is not None and 
                             self[coord].color == enemy and 
                             (self[coord].abbriviation).upper() == "N") for coord in knight_pos] 
        
        knight_attack = False
        for attack in knight_attack_list:
            knight_attack = knight_attack or attack
            
        return pawn_attack or rook_attack or knight_attack or bishop_attack or king_attack
        #return pawn_attack,rook_attack,knight_attack,bishop_attack,king_attack
        
    
    
    
    
    
    
    
    # ------------------------------------------------------------- Rest -----------------------------------------------------
    def __init__(self, player1=1, player2=1,fen = None):
        # Diana Chess:
        self.loadDianaChessConfig()
        self.PLAYER_1 = player1
        self.PLAYER_2 = player2

    def __getitem__(self, coord):
        if isinstance(coord, str):
            coord = coord.upper()
            if not re.match(RANK_REGEX, coord.upper()): raise KeyError
        elif isinstance(coord, tuple):
            coord = self.letter_notation(coord)
        try:
            return super(Board, self).__getitem__(coord)
        except KeyError:
            return None

    def save_to_file(self): pass
    
    # get the enemy, color is "white" or "black"
    def get_enemy(self, color):
        if color == "white": return "black"
        else: return "white"

    def is_king(self, piece):
        return isinstance(piece, King)

    # looks through the whole board to check for the king, outputs pos of king like this 'A5' (string)
    def get_king_position(self, color):
        for pos in self.keys():
            if self.is_king(self[pos]) and self[pos].color == color:
                return pos

    def get_king(self, color):
        if(color not in ("black", "white")): raise InvalidColor
        return self[self.get_king_position(color)]
    
    # converts coordinates in the form '(x,y)' (tuple) to 'A4' (string)
    def letter_notation(self,coord):
        if not self.is_in_bounds(coord): return
        try:
            #print(coord[0], coord[1])
            return self.axis_y[math.floor(coord[1])] + str(self.axis_x[math.ceil(coord[0])])
        except IndexError:
            raise InvalidCoord

    # converts coordinates in the from 'A4' (string) to '(x,y)' (tuple)
    def number_notation(self, coord):
        return int(coord[1])-1, self.axis_y.index(coord[0])

    def is_in_bounds(self, coord):
        if coord[1] < 0 or coord[1] >= BOARD_SIZE or\
           coord[0] <= -1 or coord[0] > (BOARD_SIZE-1):
            return False
        else: return True

    def loadDianaChessConfig(self):
        
        BOARD_INIT = [["r","b","n","k","b","r"],["p"]*6,[None]*6,[None]*6,["P"]*6,["R","B","N","K","B","R"]]
        
        self.clear()
        
        for x, row in enumerate(BOARD_INIT):
            for y, letter in enumerate(row):
                coord = self.letter_notation(((BOARD_SIZE-1)-x,y))
                if letter is None:
                    self[coord] = None
                else:
                    self[coord] = piece(letter)
                    self[coord].place(self)

        self.player_turn = 'white'

        self.fullmove_number = 1   

#---------------------------------------------------------------------------------------------------



    
#------------------------------------------------------------------------------------------------------------------



