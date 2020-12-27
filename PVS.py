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
from collections import Counter

transposition_table = {}

class PVS(SuperAgent):

    def __init__(self,delay=0,threshold=2):
        super().__init__(delay, threshold)
    


    def generate_next_move(self,gui):
        self.board = gui.chessboard
        self.copy_board = deepcopy(self.board)
        self.color = board.player_turn
        self.score_origBoard = self.evaluateGame(self.board)
        #print("Next move will now be generated:")
        score,bestmove = self.PVS(self.board,self.copy_board,float("-inf"),float("inf"),4,firstsearch=True)
        self.board.update_move(bestmove)
        gui.perform_move()
        self.board.engine_is_selecting = False
        print(self.build_fen(self.board))



    def PVS(self,orig_board,board,alpha,beta,depthleft,firstsearch=False,color=1,moves_record=[]):
        fen = self.build_fen(board).encode('utf-8')
        hash_fen = int(hashlib.md5(fen).hexdigest(), 16)
        if( depthleft <= 0 ):
            if transposition_table.get(hash_fen, None) != None:
                print('lookup')
                score = transposition_table[hash_fen]*color
                return score, None
            # score, searches = self.qsearch(orig_board,board,alpha, beta,moves_record=moves_record)
            score=self.evaluateGame(board)*color
            transposition_table[hash_fen] = score
            # print(f"qseraches: {searches}")

            return score, None
        
        if orig_board.get_time_left() < self.TIME_THRESHOLD:
            print('time up')
            if transposition_table.get(hash_fen, None) != None:
                print('lookup')
                score = transposition_table[hash_fen]*color
                return score, None
            score = self.evaluateGame(board)*color
            transposition_table[hash_fen] = score
            return score, None

        moves = board.generate_valid_moves(board.player_turn)
        if len(moves)<0:
            return -100000*color,None
        sorted_moves = self.sort_moves(moves,board)
        bestmove=sorted_moves[0]
        bestscore=float("-inf")
        if not firstsearch:
            # using fail soft with negamax:
            move = sorted_moves.pop(0)
            
            board,before = self.do_move(board,move)
            moves_record.append(move)
            # moves_record=[k for k, v in Counter(moves_record).items() if v <= 1]
            bestscore, _ = self.PVS(orig_board,board,-beta, -alpha, depthleft-1,moves_record=moves_record,color=-color)
            bestscore=-bestscore
            board = self.undo_move(board,move,before)

            if( bestscore > alpha ):
                if( bestscore >= beta ):
                    return bestscore, move
                alpha = bestscore

        for m in sorted_moves :
            board,before = self.do_move(board,m)
            moves_record.append(m)
            # moves_record=[k for k, v in Counter(moves_record).items() if v <= 1]
            score,_ = self.PVS(orig_board,board,-alpha-1, -alpha, depthleft-1,moves_record=moves_record,color=-color) 
            score=-score
            if( score > alpha and score < beta ):
                # research with window [alpha;beta]
                moves_record.append(m)
                # moves_record=[k for k, v in Counter(moves_record).items() if v <= 1]
                score,_ = self.PVS(orig_board,board,-beta, -alpha, depthleft-1,moves_record=moves_record,color=-color)
                score=-score
                if score > alpha :
                    alpha = score
            board = self.undo_move(board,m,before)
            if score > bestscore :
                bestmove = m
                if score >= beta :
                    return score, bestmove
                bestscore = score
            
        
        return bestscore,bestmove
        
    def qsearch(self,orig_board,board, alpha, beta,searches=0,moves_record=[]):
        fen = self.build_fen(board).encode('utf-8')
        hash_fen = int(hashlib.md5(fen).hexdigest(), 16)
        searches +=1
        color = board.player_turn
        if transposition_table.get(hash_fen, None) != None:
            print('lookup')
            stand_pat = transposition_table[hash_fen]
        else:
            stand_pat = self.evaluateGame(board)
            transposition_table[hash_fen] = stand_pat
        # stand_pat = self.evaluateGame(board)
        if( stand_pat >= beta ):
            return beta,searches
        if( alpha < stand_pat ):
            alpha = stand_pat

        moves = board.generate_valid_moves(board.player_turn)
        # sorted_moves = self.sort_moves_nonquiet(moves,board)
        for move in moves:
            if self.is_capture_move(board,move):
                board,before = self.do_move(board,move)
                moves_record.append(move)
                # moves_record=[k for k, v in Counter(moves_record).items() if v <= 1]
                score, searches = self.qsearch(orig_board,board, -beta, -alpha, searches,moves_record=moves_record)
                score=-score
                board = self.undo_move(board,move,before)
                if( score >= beta ):
                    return beta,searches
                if( score > alpha ):
                    alpha = score  
        return alpha,searches


