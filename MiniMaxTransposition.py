

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
        self.board = gui.chessboard
        # self.set_fen(self.board,'rbnkbr/p---pp/--p---/--B---/PP--PP/RBNK-R white')
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
        time.sleep(2)
        score, move = self.alphabeta_move(orig_board,board,-100000,100000,depth,True)
        print(f"Move {move} has Score {score}")
        return move
       

    def alphabeta_move(self,orig_board,board,alpha,beta,depthleft,maximize,incoming_move=None):
        origalpha = alpha
        fen = self.build_fen(board).encode('utf-8')
        hash_fen = int(hashlib.md5(fen).hexdigest(), 20)
        # if transposition_table.get(hash_fen, None) != None:
        #     tt_score,tt_move,tt_depth,tt_flag,tt_fen = transposition_table[hash_fen]
        #     if tt_fen==fen and tt_depth >= depthleft:
        #         if tt_flag == 0:
        #             return tt_score,tt_move
        #         elif tt_flag ==-1:
        #             alpha = max(alpha,tt_score)
        #         elif tt_flag ==1:
        #             beta = min(beta,tt_score)
        #         if alpha >= beta:
        #             return tt_score,tt_move
        moves = board.generate_valid_moves(board.player_turn)
        moves = self.sort_moves(moves,board)

        if maximize:
            if ((depthleft <= 0)):
                score = self.evaluateGame(board)
                return score, None

            value = -99999
            move = moves[0]
            for m in moves:
                board,before = self.do_move(board,m)
                value, _ = self.alphabeta_move(orig_board,board,alpha,beta,depthleft-1, False)
                board = self.undo_move(board,m,before)
                if value >= beta:
                    return beta, None
                if value > alpha:
                    move = m
                    alpha=value

            return alpha, move



        else:
            if ((depthleft <= 0) ):
                score = -self.evaluateGame(board)
                return score, None

            value = 99999
            move = moves[0]
            for m in moves:
                board,before = self.do_move(board,m)
                value, _ = self.alphabeta_move(orig_board,board,alpha,beta,depthleft-1, True)
                negaMax,_ = self.negaMax_move(orig_board,board, -beta, -alpha,depthleft - 1 ,-1)
                negaMax=-negaMax
                if value != negaMax :
                    print('wrong')
                
                board = self.undo_move(board,m,before)
                if value <= alpha:
                    # move = m
                    return alpha, None
                if value < beta:
                    move = m
                    beta = value
            return beta, move

    def negaMax_move(self,orig_board,board,alpha,beta,depthleft,color):
        bestscore = -9999
        if depthleft == 0:
            return self.evaluateGame(board)*color,None
            # return self.quiesce(orig_board,board, alpha, beta, depth,2),None
        # if  orig_board.get_time_left()<=self.TIME_THRESHOLD:
        #     print('time up!!')
        #     return self.evaluateGame(board),None
        moves = board.generate_valid_moves(board.player_turn)
        sorted_moves = self.sort_moves(moves,board)
        move = None
        branch = 0
        for m in sorted_moves:
            board,before = self.do_move(board,m)
            branch +=1
            score,_ = self.negaMax_move(orig_board,board, -beta, -alpha,depthleft - 1 ,-color)
            score=-score
            board = self.undo_move(board,m,before)
            if( score >= beta ):
                # print(f"branches before cut off: {branch}")
                return score, move
            if( score > bestscore ):
                move = m
                bestscore = score
                if( score > alpha ):
                    alpha = score           
        # print(f"branches before cut off: {branch}")
        return bestscore, move

    
   


    


    


