
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

transposition_table = {}
killer_moves= {}

class NegaMaxTransposition(SuperAgent):
    def __init__(self,delay=0,threshold=1):
        super().__init__(delay, threshold)
        # print(transposition_table)
        # time.sleep(50)
    
    def generate_next_move(self,gui):
        board = gui.chessboard
        self.board = gui.chessboard
        # print(self.build_fen(board))
        # fen = 'k---r-/P-B-R-/-PKP--/------/-P---R/------ white'
        # self.set_fen(self.board,fen)
        self.copy_board = deepcopy(self.board)
        self.color = board.player_turn
        # time.sleep(3)
        bestmoves = []
        for i in range(1,self.max_depth):
            # i=4
            print(f"Depth {i}")
            self.depth = i
            new_bestmoves = self.negaMax_root(self.board,self.copy_board,float("-inf"),float("inf"),depth=i,evaluated_moves=bestmoves)
            if len(new_bestmoves)>0:
                bestmoves=new_bestmoves
            else:
                break
            if bestmoves[0][0]>=self.score_checkmate:
                break
            # break
        score,bestmove = 0,None
        if len(bestmoves)>0:
            score,bestmove = bestmoves[0]
        board.update_move(bestmove)
        gui.perform_move()
        board.engine_is_selecting = False
        print(self.build_fen(board))


    def negaMax_root(self,orig_board,board,alpha,beta,depth=1,evaluated_moves=[]):
        if len(evaluated_moves)>0:
            moves = list(zip(*evaluated_moves))[1]
        else:
            moves = board.generate_valid_moves(board.player_turn)
            moves = self.sort_moves(moves,board,transposition_table=transposition_table,depth=depth)
        bestmoves = []
        for m in moves:
            if orig_board.get_time_left()<=self.TIME_THRESHOLD:
                self.time_up=True
                return bestmoves
            board,before = self.do_move(board,m)
            score = -self.negaMax_lookup(orig_board,board, -beta, -alpha, depth-1 ,last_move=m)
            board = self.undo_move(board,m,before)
            if self.time_up:
                return bestmoves
            elif len(bestmoves) == 0:
                bestmoves.append((score,m))
                alpha = score
                print(f"New bestmove {m} with score {score}")
            elif score > bestmoves[0][0]:
                bestmoves.insert(0,(score,m))
                print(f"New bestmove {m} with score {score}")
                if score > alpha :
                    alpha = score
            elif score >= self.score_checkmate:
                return bestmoves                
            else:
                print(f"Move {m} is not better")
                bestmoves.append((score,m))
        print(f"Searched {self.counter} nodes")
        # self.counter=0
        return bestmoves


    def negaMax_lookup(self,orig_board,board,alpha,beta,depthleft,last_move=None):
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
        sorted_moves = self.sort_moves(moves,board,transposition_table=transposition_table,killer_moves=killer_moves,depth=depthleft)
        if len(sorted_moves)==0:
            return -self.score_checkmate*(self.depth-depthleft+1)
        score =-9999999
        killer = None
        for m in sorted_moves:
            board,before = self.do_move(board,m)
            score = max(score,-self.negaMax_lookup(orig_board,board, -beta, -alpha, depthleft - 1 ,last_move=m))
            board = self.undo_move(board,m,before)
            if( score > alpha ):
                alpha = score
                killer = m
            if( alpha >= beta ):
                if before[-1]==None:
                    if killer != None:
                        # print(f"new killer move with distance {self.depth-depthleft}")
                        killer_moves = self.insert_killer(killer,self.depth-depthleft,killer_moves)
                elif before[-1].color == board.get_enemy(board.player_turn):
                    if killer != None:
                        # print(f"new killer move with distance {self.depth-depthleft}")
                        killer_moves = self.insert_killer(killer,self.depth-depthleft,killer_moves)
                # print('cutoff')
                break
        tt_score = score
        tt_depth = depthleft
        if score <= alphaorig:
            tt_flag = 1
        elif score >= beta:
            tt_flag = -1
        else:
            tt_flag = 0
        transposition_table[hash_fen] = tt_score, tt_depth, tt_flag, fen, fen_color
        # print(transposition_table)
        return score

