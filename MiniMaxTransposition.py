

import time
import random
import math
from copy import deepcopy, copy
import hashlib
from studentagent import *
from pieces import *
from SuperAgent import SuperAgent


# After perform_move(), make sure that the agent does not continue searching for moves!

transposition_table = {}
class MiniMaxTransposition(SuperAgent):

    def __init__(self,delay=0,threshold=5):
        super().__init__(delay, threshold)
    


    def generate_next_move(self,gui):
        
        #print("Next move will now be generated:")
        
        board = gui.chessboard
        color = "white"
        self.board = gui.chessboard 
        self.copy_board = deepcopy(self.board)
        self.color = board.player_turn
        self.score_origBoard = self.evaluateGame(self.board)
        bestmove = self.select_move(self.board,self.copy_board,2)

        board.update_move(bestmove)
        gui.perform_move()
        board.engine_is_selecting = False
        print(self.build_fen(board))

  

    
    def select_move(self,orig_board,board,depth, maximize=True):

        bestmoves = []

        score, move = self.alphabeta_move(orig_board,board,-100000,100000,depth,True)
        print(f"Move {move} has Score {score}")
        return move
       

    def alphabeta_move(self,orig_board,board,alpha,beta,depthleft,maximize,incoming_move=None):
        fen = self.build_fen(board).encode('utf-8')
        hash_fen = int(hashlib.md5(fen).hexdigest(), 16)
        color = board.player_turn
        moves = board.generate_valid_moves(board.player_turn)
        moves = self.sort_moves(moves,board)
        if maximize:
            if ((depthleft <= 0) or (orig_board.get_time_left() < self.TIME_THRESHOLD)):
                score = self.evaluateGame(board)
                transposition_table[hash_fen] = score
                return score, None
            value = -99999
            move = moves[0]
            for m in moves:
                board,before = self.do_move(board,m)
                value, _ = self.alphabeta_move(orig_board,board,alpha,beta,depthleft-1, False)
                board = self.undo_move(board,m,before)
                if value >= beta:
                    move = m
                    return beta, move
                if value > alpha:
                    move = m
                    alpha=value

            return alpha, move

        else:
            if ((depthleft <= 0) or (orig_board.get_time_left() < self.TIME_THRESHOLD)):
                score = -self.evaluateGame(board)
                transposition_table[hash_fen] = score
                return score,None
            value = 99999
            move = moves[0]
            for m in moves:
                board,before = self.do_move(board,m)
                value, _ = self.alphabeta_move(orig_board,board,alpha,beta,depthleft-1, True)
                board = self.undo_move(board,m,before)
                if value <= alpha:
                    move = m
                    return alpha, move
                if value < beta:
                    move = m
                    beta = value
            return beta, move

    
   


    


    


