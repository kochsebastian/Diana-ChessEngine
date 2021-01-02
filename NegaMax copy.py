
import time
import random
import math
from copy import deepcopy, copy
import hashlib
from studentagent import *
from pieces import *
from SuperAgent import SuperAgent

class PrincipalVariation():
    def __init__(self,nested_list,maxfjlkfj):
        # self.de =
        self.top = nested_list
        pass


class NegaMaxPV(SuperAgent):
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
            i=3
            bestmoves = self.negaMax_root(self.board,self.copy_board,float("-inf"),float("inf"),depth=i,evaluated_moves=bestmoves)
            break
        score,bestmove = bestmoves[0]
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
        for m in moves:
            board,before = self.do_move(board,m)
            score = -self.negaMax(orig_board,board, -beta, -alpha, depth-1,last_move=m)
            board = self.undo_move(board,m,before)
            if len(bestmoves) == 0:
                bestmoves.append((score,m))
                alpha = score
                print(f"New bestmove {m} with score {score}")
            elif score > bestmoves[0][0]:
                bestmoves.insert(0,(score,m))
                print(f"New bestmove {m} with score {score}")
                if score > alpha :
                    alpha = score
            else:
                print(f"Move {m} is not better")
                bestmoves.append((score,m))
            if score > self.score_checkmate:
                break
        print(f"Searched {self.counter} nodes")
        return bestmoves

    def negaMax(self,orig_board,board,alpha,beta,depthleft,last_move=None):
        self.counter+=1
        if depthleft == 0:
            return self.qsearch(orig_board,board,alpha,beta,last_move)
            # return self.evaluateGame(board) #* color
        elif orig_board.get_time_left()<=self.TIME_THRESHOLD:
            print('time up!!')
            # return self.qsearch(orig_board,board,beta,alpha,last_move)
            return self.evaluateGame(board) #* color
            
        moves = board.generate_valid_moves(board.player_turn)
        sorted_moves = self.sort_moves(moves,board)
        if len(sorted_moves)==0:
            return -self.score_checkmate

        bestscore = -9999999
        score = -9999999
        for m in sorted_moves:
            board,before = self.do_move(board,m)
            # score = -self.negaMax(orig_board,board, -beta, -alpha, depthleft - 1 last_move=m)
            score = max(score,-self.negaMax(orig_board,board, -beta, -alpha, depthleft - 1 ,last_move=m))
            board = self.undo_move(board,m,before)
            # if( score >= beta ):
            #     return score
            # if( score > bestscore ):
            #     bestscore = score
            #     if score>alpha:
            #         alpha = score
            # if( score >= beta ):
            #     # if not self.is_capture_move(board,m):
            #     #     self.insert_killer(m,depthleft)
            #     return beta   #  fail hard beta-cutoff
            # if( score > alpha ):
            #     alpha = score
            alpha = max(alpha,score)
            if( alpha >= beta ):
                # print('cutoff')
                break

        return score

