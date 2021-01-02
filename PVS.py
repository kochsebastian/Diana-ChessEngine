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
        board = gui.chessboard
        self.board = gui.chessboard
        print(self.build_fen(board))
        # fen = 'rbnk-r/pPp-pp/--bp--/----P-/-PPP-P/RBNKBR white'
        # self.set_fen(self.board,fen)
        self.copy_board = deepcopy(self.board)
        self.color = board.player_turn
        # self.score_origBoard = self.evaluateGame(self.board)
        # time.sleep(3)
        maxDepth = 10
        bestmoves = []
        for i in range(1,maxDepth):
            # i=4
            print(f"Depth {i}")
            self.depth = i
            new_bestmoves = self.pvs_root(self.board,self.copy_board,float("-inf"),float("inf"),depth=i,evaluated_moves=bestmoves)
            if len(new_bestmoves)>0:
                bestmoves=new_bestmoves
            else:
                break
            # break
        score,bestmove = bestmoves[0]
        board.update_move(bestmove)
        gui.perform_move()
        board.engine_is_selecting = False
        print(self.build_fen(board))


    def pvs_root(self,orig_board,board,alpha,beta,depth=1,evaluated_moves=[]):
        if len(evaluated_moves)>0:
            moves_t = list(zip(*evaluated_moves))[1]
        else:
            moves_t = board.generate_valid_moves(board.player_turn)
            moves_t = self.sort_moves(moves_t,board)
        bestmoves = []
        moves = list(moves_t)
        m = moves.pop(0)
        board,before = self.do_move(board,m)
        bestscore = -self.pvs(orig_board,board,-beta, -alpha, depth-1,color=-1,last_move=m) 
        board = self.undo_move(board,m,before)
        if self.time_up:
            return bestmoves
        if bestscore > alpha :
            alpha = bestscore
        bestmoves.append((bestscore,m))
        if bestscore > self.score_checkmate:
            return bestmoves
        print(f"New bestmove {m} with score {bestscore}")
        for m in moves:
            if orig_board.get_time_left()<=self.TIME_THRESHOLD:
                self.time_up=True
                return bestmoves
            board,before = self.do_move(board,m)
            score = -self.pvs(orig_board,board,-alpha-1,-alpha,depth-1,last_move=m)
            if( score > alpha and score < beta ):
                score = -self.pvs(orig_board,board,-beta, -alpha, depth-1,last_move=m) 
                if score > alpha:
                    alpha = score
            board = self.undo_move(board,m,before)
            if self.time_up:
                return bestmoves
            if score > bestscore:
                bestscore=score

            if len(bestmoves) == 0:
                bestmoves.append((score,m))
                print(f"New bestmove {m} with score {score}")
            elif score > bestmoves[0][0]:
                bestmoves.insert(0,(score,m))
                print(f"New bestmove {m} with score {score}")
            else:
                print(f"Move {m} is not better")
                bestmoves.append((score,m))
            if bestscore > self.score_checkmate:
                return bestmoves
        print(f"Searched {self.counter} nodes")
        return bestmoves

    def pvs(self,orig_board,board,alpha,beta,depthleft,color=1,last_move=None):
        global killer_moves
        self.counter+=1
        alphaorig = alpha
        fen = self.build_fen(board)
        fen, fen_color = fen.split(" ")
        fen = fen.encode('utf-8')
        hash_fen = int(hashlib.md5(fen).hexdigest(), self.hash_precision)
        if transposition_table.get(hash_fen, None) != None:
            # print('lookup probabile')
            tt_score,tt_depth,tt_flag,tt_fen,tt_color = transposition_table[hash_fen]
            if tt_fen==fen:
                tt_score = tt_score * (1 if fen_color==tt_color else -1)
                # print('lookup possible')
                if tt_depth >= depthleft:
                    # print('restore')
                    if tt_flag == 0:
                        return tt_score
                    elif tt_flag == -1:
                        alpha = max(alpha,tt_score)
                    elif tt_flag ==1:
                        beta = min(beta,tt_score)
                    if alpha >= beta:
                        return tt_score
            else:
                print('conflict')
        if depthleft == 0:
            return self.qsearch(orig_board,board,alpha,beta,last_move)
        elif orig_board.get_time_left()<=self.TIME_THRESHOLD:
            print('time up!!')
            self.time_up=True
            return 0
            # return self.evaluateGame(board) 

        moves = board.generate_valid_moves(board.player_turn)
        sorted_moves_t = self.sort_moves(moves,board)
        sorted_moves = list(sorted_moves_t)
        if len(sorted_moves)<=0:
            return -self.score_checkmate*(self.depth-depthleft)
        m = sorted_moves.pop(0)
        board,before = self.do_move(board,m)
        bestscore = -self.pvs(orig_board,board,-beta, -alpha, depthleft-1,last_move=m) 
        board = self.undo_move(board,m,before)
        if bestscore > alpha :
            if bestscore >= beta:
                tt_score = bestscore
                tt_depth = depthleft
                tt_flag = -1
                transposition_table[hash_fen] = tt_score, tt_depth, tt_flag, fen, fen_color
                return bestscore
            alpha = bestscore
        for m in sorted_moves:
            board,before = self.do_move(board,m)
            score = -self.pvs(orig_board,board,-alpha-1,-alpha,depthleft-1,last_move=m)
            if( score > alpha and score < beta ):
                score = -self.pvs(orig_board,board,-beta, -alpha, depthleft-1,last_move=m) 
                if score >alpha:
                    alpha = score
            board = self.undo_move(board,m,before)
            if score > bestscore:
                if score >= beta:
                    tt_score = score
                    tt_depth = depthleft
                    tt_flag = -1
                    transposition_table[hash_fen] = tt_score, tt_depth, tt_flag, fen, fen_color
                    return score
                bestscore=score
        
        tt_score = bestscore
        tt_depth = depthleft
        if bestscore <= alphaorig:
            tt_flag = 1
        elif bestscore >= beta:
            tt_flag = -1
        else:
            tt_flag = 0
        transposition_table[hash_fen] = tt_score, tt_depth, tt_flag, fen, fen_color
       
        return bestscore
        
   

