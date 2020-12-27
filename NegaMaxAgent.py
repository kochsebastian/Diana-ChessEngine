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
import hashlib
from studentagent import *
from pieces import *
from SuperAgent import SuperAgent

class NegaMaxAgent(SuperAgent):

    def __init__(self,delay=0,threshold=5):
        print('Student is playing')
        self.delay = delay
        self.TIME_THRESHOLD = threshold
    


    def generate_next_move(self,gui):
        
        #print("Next move will now be generated:")
        
        board = gui.chessboard
        color = "white"
        copy_board = deepcopy(board)
        for search_depth in range(1,12):
            if board.get_time_left()>self.TIME_THRESHOLD*search_depth:
                bestmove = self.choose_move_negaMax(board,copy_board,search_depth)

        board.update_move(bestmove)
        gui.perform_move()
        board.engine_is_selecting = False
        print(self.build_fen(board))

  

    def choose_move_negaMax(self,orig_board,board,depth):
        bestMove = None
        bestValue = -99999
        alpha = -100000
        beta = 100000
        moves = board.generate_valid_moves(board.player_turn)
        sorted_moves = self.sort_moves(moves,board)
        for move in sorted_moves:
            board ,before = self.do_move(board,move)
            fen = self.build_fen(board).encode('utf-8')
            hash_fen = int(hashlib.md5(fen).hexdigest(), 16)
            # if transposition_table.get(hash_fen, None) != None:
            #     score, depth_score = transposition_table[hash_fen]
            #     if depth_score > depth:
            #         print('restored position')
            #         boardValue = score
            #     else:
            #         boardValue = -self.negaMax(orig_board,board,-beta, -alpha, depth-1)
            #         transposition_table[hash_fen] = boardValue, depth
            # else:
            boardValue = -self.negaMax(orig_board,board,-beta, -alpha, depth-1)
            transposition_table[hash_fen]= boardValue, depth
            board = self.undo_move(board,move,before)
            if boardValue > bestValue:
                bestValue = boardValue
                bestMove = move
            if( boardValue > alpha ):
                alpha = boardValue
        return bestMove

    def negaMax(self,orig_board,board, alpha, beta, depthleft, depth=1 ) :
        bestscore = -9999
        if( depthleft == 0 or orig_board.get_time_left()<=self.TIME_THRESHOLD):
            return self.quiesce(board, alpha, beta, depth,2)
        
        moves = board.generate_valid_moves(board.player_turn)
        sorted_moves = self.sort_moves(moves,board)
        for move in sorted_moves:
            board,before = self.do_move(board,move)
            fen = self.build_fen(board).encode('utf-8')
            hash_fen = int(hashlib.md5(fen).hexdigest(), 16)
            # if transposition_table.get(hash_fen, None) != None:
            #     score, depth_score = transposition_table[hash_fen]
            #     if depth_score > depth:
            #         print('restored position')
            #         boardValue = score
            #     else:
            #         boardValue = -self.negaMax(orig_board,board,-beta, -alpha, depth-1)
            #         transposition_table[hash_fen] = boardValue, depth
            # else:
            score = -self.negaMax(orig_board,board, -beta, -alpha, depthleft - 1, depth+1 )
            transposition_table[hash_fen]=score, depth+1
            board = self.undo_move(board,move,before)
            if( score >= beta ):
                print("cut branch")
                return score
            if( score > bestscore ):
                bestscore = score
                if( score > alpha ):
                    alpha = score   
        return bestscore

    
    
    def quiesce(self,board, alpha, beta, depth, depthleft ):
        color = board.player_turn
        if depthleft<=0:
            return self.evaluateGame(board)
        stand_pat = self.evaluateGame(board)
        if( stand_pat >= beta ):
            return beta
        if( alpha < stand_pat ):
            alpha = stand_pat

        moves = board.generate_valid_moves(board.player_turn)
        sorted_moves = self.sort_moves(moves,board)
        for move in sorted_moves:
            if self.is_capture_move(board,move):
                board,before = self.do_move(board,move)
              
                score = -self.quiesce(board, -beta, -alpha,depth+1,depthleft-1)
                board = self.undo_move(board,move,before)
                if( score >= beta ):
                    print("cut branch")
                    return beta
                if( score > alpha ):
                    alpha = score  
        return alpha


    


