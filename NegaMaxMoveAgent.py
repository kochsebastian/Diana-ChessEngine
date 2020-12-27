
import time
import random
import math
from copy import deepcopy, copy
import hashlib
from studentagent import *
from pieces import *
from SuperAgent import SuperAgent


class NegaMaxMoveAgent(SuperAgent):
    def __init__(self,delay=0,threshold=1):
        print('Student is playing')
        self.delay = delay
        self.TIME_THRESHOLD = threshold
    
    def generate_next_move(self,gui):
        board = gui.chessboard
        score, bestmove,nodes = self.negaMax_move(board,deepcopy(board),-100000,100000,1,5,1)
        print(f"nodes searched: {nodes}")
        board.update_move(bestmove)
        gui.perform_move()
        board.engine_is_selecting = False
        print(self.build_fen(board))

    def negaMax_move(self,orig_board,board,alpha,beta,depth,depthleft,color,nodes=0):
        nodes+=1
        bestscore = -9999
        if depthleft == 0:
            return self.evaluateGame(board),None,nodes
            # return self.quiesce(orig_board,board, alpha, beta, depth,2),None
        if  orig_board.get_time_left()<=self.TIME_THRESHOLD:
            print('time up!!')
            return self.evaluateGame(board),None,nodes
        moves = board.generate_valid_moves(board.player_turn)
        sorted_moves = self.sort_moves(moves,board)
        move = None
        branch = 0
        for m in sorted_moves:
            board,before = self.do_move(board,m)
            branch +=1
            score,_,nodes = self.negaMax_move(orig_board,board, -beta, -alpha, depth+1,depthleft - 1 ,color*-1,nodes)
            score=-score
            board = self.undo_move(board,m,before)
            if( score >= beta ):
                # print(f"branches before cut off: {branch}")
                return score, move,nodes
            if( score > bestscore ):
                move = m
                bestscore = score
                if( score > alpha ):
                    alpha = score           
        # print(f"branches before cut off: {branch}")
        return bestscore, move,nodes
    
    def quiesce(self,orig_board,board, alpha, beta, depth, depthleft ):
        color = board.player_turn
        if depthleft<=0 or orig_board.get_time_left()<=self.TIME_THRESHOLD:
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

                score = -self.quiesce(orig_board,board, -beta, -alpha,depth+1,depthleft-1)
                board = self.undo_move(board,move,before)
                if( score >= beta ):
                    print("cut branch")
                    return beta
                if( score > alpha ):
                    alpha = score  
        return alpha
