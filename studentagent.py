"""   

- Generally, coordinates/positions are 'A3', 'B3',...
- board[coord] returns the piece at coord
- Try to always have a move to do (just take a random one at the beginning with update_move)

- IMPORTANT: ALWAYS USE COPIES OF THE GAME BOARD VIA DEEPCOPY() IF YOU WANT TO MANIPULATE THE BOARD,
             THIS IS SHOWN IN MR. NOVICE
             
- You can get the board from the gui via gui.chessboard

- DO NOT CHANGE OR ADD THE PARAMS OF THE GENERATE FUNCTION OR ITS NAME!



        -------------------- Useful methods  ---------------------------------------

-------------------- Board methods:

# converts coordinates in the form '(x,y)' (tuple) to 'A4' (string)
def letter_notation(self,coord)

# converts coordinates in the from 'A4' (string) to '(x,y)' (tuple)
def number_notation(self, coord):

# looks through the whole board to check for the king, outputs pos of king like this 'A5' (string)
def get_king_position(self, color):

# get the enemy, color is "white" or "black"
def get_enemy(self, color):

# manually check from the king if other pieces can attack it
# output is boolean
def is_in_check(self, color, debug=False):

def is_in_checkmate(self, color):

# returns a list of all valid moves in the format [('A1','A4'),..], left: from, right: to
def generate_valid_moves(self, color):

# returns a list of all possible moves in the format [('A1','A4'),..], left: from, right: to
def all_possible_moves(self, color):

# checks for limit turn count and checkmate, returns boolean (won/not won)
def check_winning_condition(self,color,end_game=False,print_result=False,gui = None):

# filter out invalid moves for moves of a color, returns list of valid moves
def is_in_check_after_move_filter(self,moves):

# returns boolean (still in check after p1->p2)
def is_in_check_after_move(self, p1, p2):

# time left for choosing move (in seconds)
def get_time_left(self):

# executes move without checking
# !   You have to manually change to the next player 
# with board.player_turn=board.get_enemy(board.player_turn) after this !
def _do_move(self, p1, p2):

# Pretty print board
def pprint(self):

# update the move that will be done (has to be a tuple (from, to))
def update_move(self,move):


---------------GUI methods

# performs the selected move (should ideally be at the end of generate function)
def perform_move(self):


--------------- Piece methods


# returns the landing positions, if the piece were at pos
# ! only landing positions !
def possble_moves(pos)

"""
import time
import random
import math
from copy import deepcopy, copy
from studentagent import *
from pieces import *

# After perform_move(), make sure that the agent does not continue searching for moves!

pieces = {  'P': Pawn("white"),
            'p': Pawn("black"),
            'R': Rook("white"),
            'r': Rook("black"),
            'N': Knight("white"),
            'n': Knight("black"),
            'B': Bishop("white"),
            'b': Bishop("black"),
            'K': King("white"),
            'k': King("black"),
            '-': None
        }

SCORE_WIN    = 1000
        
SCORE_PAWN   = 20
SCORE_ROOK   = 50
SCORE_BISHOP = 20
SCORE_KNIGHT = 40
SCORE_QUEEN  = 0

SCORE_CHECK     = 50

piece_values = {    'p': SCORE_PAWN,
                    'r': SCORE_ROOK,
                    'k': SCORE_KING,
                    'n': SCORE_KNIGHT,
                    'b': SCORE_BISHOP,
                }

class MrCustom:

    def __init__(self,delay=0,threshold=5):
        print('Student is playing')
        self.delay = delay
        self.TIME_THRESHOLD = threshold
    

    def set_fen(self,board,fen):
        position, turn = fen.split(' ')
        rows = position.split('/')
        rows.reverse()
        
        for i,x in enumerate(board.axis_x):
            for j,y in enumerate(board.axis_y):
                board[y+str(x)] = pieces[rows[i][j]]

        return board

    def evaluateGame(self, board, player_wins, enemy_wins):
        #print("Evaluation of board started.")
        
        
        color = board.player_turn
        score = 0

        #print("Check winning")
        t1 = time.time()
        if player_wins:
            return SCORE_WIN
        elif enemy_wins:
            return -SCORE_WIN
        t2 = time.time()
        #print("Checking winning in evaluation: ", t2-t1)
        
        
        #print("Is in Check")
        t1 = time.time()
        if board.is_in_check(color):
            score -= SCORE_CHECK
        
        if board.is_in_check(board.get_enemy(color)):
            score += SCORE_CHECK
        
        t2 = time.time()
        #print("Checking Is in Check in evaluation: ", t2-t1)
        
        #print("Calc score")
        t1 = time.time()
        # fen = "rbnk-r/pPp-pp/---p--/-P----/-P-PPP/RBNKBR " +color
        # self.set_fen(board,fen)
        for coord in board.keys(): # this maybe improved, faster iteration
            if (board[coord] is not None):
                figure = board[coord]
                fig_color = board[coord].color
                piece = figure.abbriviation.lower()
                figurescore = 0
                score = piece_values[piece]
                if fig_color == color:
                    score += figurescore
                else:
                    score -= figurescore

        t2 = time.time()
        #print("Checking Score Calc in evaluation: ", t2-t1)            
        
        #print("Evaluation of board ended.")
        
        return score

    def sort_moves(self,moves,board):
        color = board.player_turn
        
        player_wins = board.check_winning_condition(color)
        enemy_wins = board.check_winning_condition(board.get_enemy(color))
        game_ends = player_wins or enemy_wins 

        scores = []
        for m in moves:
            board_copy = deepcopy(board)
            board_copy._do_move(m[0],m[1])
            scores.append(self.evaluateGame(board,player_wins,enemy_wins))
        scores, moves = zip(*sorted(zip(scores, moves)))
        return scores, moves


    def generate_next_move(self,gui):
        
        #print("Next move will now be generated:")
        
        board = gui.chessboard
        
        search_depth = 3
        maxscore = -math.inf
        
        bestmoves = []

        #print("First, valid moves are generated.")
        moves = board.generate_valid_moves(board.player_turn)

        orig_board = deepcopy(board)
        copy_board = deepcopy(board)
        bestmove = self.select_move(orig_board,copy_board,search_depth)

        board.update_move(bestmove)
        gui.perform_move()
        board.engine_is_selecting = False

  

    
    def select_move(self,orig_board,board,depth, maximize=True):
        bestMove = -9999
        bestMoveFinal = None
        moves = board.generate_valid_moves(board.player_turn)
        for m in moves:
            board_copy = deepcopy(board)
            board_copy._do_move(m[0],m[1])
            board_copy.player_turn = board_copy.get_enemy(board_copy.player_turn)
            value = max(bestMove,self.alphabeta(orig_board,board_copy,-100000,-100000,depth, not maximize))
            if value > bestMove:
                print("Best score: " ,str(bestMove))
                print("Best move: ",str(bestMoveFinal))
                bestMove = value
                bestMoveFinal = m 
            
        return bestMoveFinal

    def alphabeta(self,orig_board,board,alpha,beta,depthleft,maximize):
        bestscore = -9999
        color = board.player_turn

        player_wins = board.check_winning_condition(color)
        enemy_wins = board.check_winning_condition(board.get_enemy(color))
        game_ends = player_wins or enemy_wins 
        
        if ((depthleft <= 0) or game_ends or (orig_board.get_time_left() < self.TIME_THRESHOLD)): # here hey used orig board
            return self.evaluateGame(board,player_wins,enemy_wins)

        moves = board.generate_valid_moves(board.player_turn)
        if maximize:
            bestMove = -9999
            for m in moves:
                board_copy = deepcopy(board)
                board_copy._do_move(m[0],m[1])
                board_copy.player_turn = board_copy.get_enemy(board_copy.player_turn)
                
                bestMove = max(bestMove,self.alphabeta(orig_board,board_copy,beta,alpha,depthleft-1, not maximize))
                if bestMove >= beta:
                    return bestMove
                alpha = max(alpha,bestMove)
                
            return bestMove

        else:
            bestMove = 9999
            for m in moves:
                board_copy = deepcopy(board)
                board_copy._do_move(m[0],m[1])
                board_copy.player_turn = board_copy.get_enemy(board_copy.player_turn)
                
                bestMove = min(bestMove,self.alphabeta(orig_board,board_copy,beta,alpha,depthleft-1, not maximize))
                if bestMove <= beta:
                    return bestMove
                beta = min(bestMove,beta)
         
            return bestMove

    


    


