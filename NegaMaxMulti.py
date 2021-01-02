
import time
import random
import math
from copy import deepcopy, copy
import hashlib
from studentagent import *
from pieces import *
from SuperAgent import SuperAgent
import multiprocessing as mp

class PrincipalVariation():
    def __init__(self,nested_list,maxfjlkfj):
        # self.de =
        self.top = nested_list
        pass

class NegaMaxMulti(SuperAgent):
    def __init__(self,delay=0,threshold=5):
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
        maxDepth = 3
        bestmoves = []
        for i in range(1,maxDepth):
            i=4
            bestmoves = self.negaMax_root(self.board,self.copy_board,float("-inf"),float("inf"),depth=i,evaluated_moves=bestmoves)
            break
        score,bestmove = bestmoves[0]
        print(bestmove)
        board.update_move(bestmove)
        gui.perform_move()
        board.engine_is_selecting = False
        print(self.build_fen(board))


    def negaMax_root(self,orig_board,board,alpha,beta,depth=1,evaluated_moves=[]):
        
        if len(evaluated_moves)>0:
            moves = evaluated_moves
        else:
            moves = board.generate_valid_moves(board.player_turn)
            moves = self.sort_moves(moves,board)
        bestmoves = []
        manager = mp.Manager()
        return_list= manager.list()
        jobs = []
        print(moves)
        for m in moves:
            # obj = deepcopy(self)
            p = mp.Process(target=self.start_alphabeta, args=(orig_board,board,alpha,beta,depth,m,return_list))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()
        
        print(return_list)
        move_scores = list(zip(return_list,moves))
        move_scores.sort(key=lambda move_score: move_score[0],reverse=True)
        print(move_scores)
        print(f"Searched {self.counter} nodes")
        return move_scores

    def start_alphabeta(self,orig_board,board,alpha,beta,depth,m,return_list):
        board,before = self.do_move(board,m)
        score = -self.negaMax(orig_board,board, -beta, -alpha, depth-1 ,color=1,last_move=m)
        board = self.undo_move(board,m,before)
        return_list.append(score)

    def negaMax(self,orig_board,board,alpha,beta,depthleft,color=1,last_move=None):
        self.counter+=1
        if depthleft == 0:
            return self.qsearch(orig_board,board,alpha,beta,-color,last_move)
            # return self.evaluateGame(board) #* color
        elif orig_board.get_time_left()<=self.TIME_THRESHOLD:
            print('time up!!')
            # return self.qsearch(orig_board,board,beta,alpha,-color,last_move)
            return self.evaluateGame(board) #* color
            
        moves = board.generate_valid_moves(board.player_turn)
        sorted_moves = self.sort_moves(moves,board)
        if len(sorted_moves)==0:
            return self.evaluateGame(board) #* color
        bestscore =-9999999
        for m in sorted_moves:
            board,before = self.do_move(board,m)
            score = -self.negaMax(orig_board,board, -beta, -alpha, depthleft - 1 ,-color,last_move=m)
            board = self.undo_move(board,m,before)
            # if( score >= beta ):
            #     return score
            # if( score > bestscore ):
            #     bestscore = score
            #     if score>alpha:
            #         alpha = score
            if( score >= beta ):
                # if not self.is_capture_move(board,m):
                #     self.insert_killer(m,depthleft)
                return beta   #  fail hard beta-cutoff
            if( score > alpha ):
                alpha = score
            # alpha = max(alpha,score)
            # if( alpha >= beta ):
            #     # print('cutoff')
            #     break

        return alpha

