

import time
import random
import math
from copy import deepcopy, copy
import hashlib
from studentagent import *
from pieces import *
from SuperAgent import SuperAgent


# After perform_move(), make sure that the agent does not continue searching for moves!


class MiniMaxAgent(SuperAgent):

    def __init__(self,delay=0,threshold=2):
        super().__init__(delay, threshold)
    


    def generate_next_move(self,gui):
        
        #print("Next move will now be generated:")
        
        board = gui.chessboard
        color = "white"
        self.board = gui.chessboard 
        self.copy_board = deepcopy(self.board)
        self.color = board.player_turn
        self.score_origBoard = self.evaluateGame(self.board)
        bestmove = self.select_move(self.board,self.copy_board,4)

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
        color = board.player_turn
        moves = board.generate_valid_moves(board.player_turn)
        moves = self.sort_moves(moves,board)
        if maximize:
            if ((depthleft <= 0) or (orig_board.get_time_left() < self.TIME_THRESHOLD)):
                score = self.evaluateGame(board)
                return score,None
            value = -99999
            move = moves[0]
            for m in tqdm(moves):
                board,before = self.do_move(board,m)
                score, _ = self.alphabeta_move(orig_board,board,alpha,beta,depthleft-1, False)
                board = self.undo_move(board,m,before)
                value = max(value,score)
                if value > alpha:
                    move = m
                    alpha = value
                if  beta <= alpha:
                    # print("cut branch")
                    break
                    # return value, move
            return value, move

        else:
            if ((depthleft <= 0) or (orig_board.get_time_left() < self.TIME_THRESHOLD)):
                score = -self.evaluateGame(board)
                return score,None
            value = 99999
            move = moves[0]
            for m in tqdm(moves):
                board,before = self.do_move(board,m)
                score, _ = self.alphabeta_move(orig_board,board,alpha,beta,depthleft-1, True)
                board = self.undo_move(board,m,before)
                value = min(value,score)
                if value < beta:
                    beta = value
                    move = m
                if beta <= alpha:
                    # print("cut branch")
                    break
            return value, move

    
   


    


    


