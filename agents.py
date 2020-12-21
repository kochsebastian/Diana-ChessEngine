import time
import random
import math
from copy import deepcopy, copy
from studentagent import *
from pieces import *

class MrRandom:
    
    def __init__(self, delay=0):
        self.delay = delay
        
    def generate_next_move(self,gui):

        board = gui.chessboard
        
        moves = board.generate_valid_moves(board.player_turn)
        if len(moves) > 0:
            a = random.randint(0,len(moves)-1)
            board.update_move(moves[a])
            gui.perform_move()
        board.engine_is_selecting = False

        
class MrNovice:

    def __init__(self,delay=0, threshold=5):
        self.delay = delay
        self.TIME_THRESHOLD = threshold
    
    def evaluateGame(self,board, player_wins, enemy_wins):
        #print("Evaluation of board started.")
        SCORE_WIN    = 1000
        
        SCORE_PAWN   = 10
        SCORE_ROOK   = 50
        SCORE_BISHOP = 50
        SCORE_KNIGHT = 50
        SCORE_QUEEN  = 200
        
        SCORE_CHECK     = 20
        
        color = board.player_turn
        score = 0

        #print("Check winning")
        t1 = time.time()
        if player_wins:
            return SCORE_WIN
        elif enemy_wins:
            return -SCORE_WIN
        t2 = time.time()
        #print("Checking winning in evaluation: ", t2-t1)
        
        
        #print("Is in Check")
        t1 = time.time()
        if board.is_in_check(color):
            score -= SCORE_CHECK
        
        if board.is_in_check(board.get_enemy(color)):
            score += SCORE_CHECK
        
        t2 = time.time()
        #print("Checking Is in Check in evaluation: ", t2-t1)
        
        #print("Calc score")
        t1 = time.time()
        for coord in board.keys():
            if (board[coord] is not None):
                figure = board[coord]
                fig_color = board[coord].color
            
                figurescore = 0
                if figure.abbriviation=='p':
                    figurescore = SCORE_PAWN
                elif figure.abbriviation=='r':
                    figurescore = SCORE_ROOK
                elif figure.abbriviation=='b':
                    figurescore = SCORE_BISHOP
                elif figure.abbriviation=='n':
                    figurescore = SCORE_KNIGHT

                if fig_color == color:
                    score += figurescore
                else:
                    score -= figurescore

        t2 = time.time()
        #print("Checking Score Calc in evaluation: ", t2-t1)            
        
        #print("Evaluation of board ended.")
        
        return score

    def generate_next_move(self,gui):
        
        #print("Next move will now be generated:")
        
        board = gui.chessboard
        
        search_depth = 2
        maxscore = -math.inf
        
        bestmoves = []

        #print("First, valid moves are generated.")
        moves = board.generate_valid_moves(board.player_turn)
        random.shuffle(moves)
        
        if len(moves) > 0:
            # always have one move to to
            board.update_move(moves[0])


            #print("We will test ", len(moves), " main moves.")
            for m in moves:
                board_copy = deepcopy(board)
                board_copy._do_move(m[0],m[1])

                board_copy.player_turn = board_copy.get_enemy(board_copy.player_turn)

                #print("We test main move: ", m, " and the board looks like this:")
                #board_copy.pprint()
                #print("Main move test start.")
                score = self.min_func(board,board_copy, search_depth)
                #print("Main move test end.")

                if score > maxscore:
                    maxscore = score
                    bestmoves.clear()
                    bestmoves.append(m)
                    board.update_move(m)
                elif score == maxscore:
                    bestmoves.append(m)

            bestmove = bestmoves[random.randint(0,len(bestmoves)-1)]
            board.update_move(bestmove)
            gui.perform_move()
        board.engine_is_selecting = False
        
    

    def min_func(self,original_board,board,depth):
        
        color = board.player_turn
        
        player_wins = board.check_winning_condition(color)
        enemy_wins = board.check_winning_condition(board.get_enemy(color))
        game_ends = player_wins or enemy_wins 
        
        if ((depth <= 0) or game_ends or (original_board.get_time_left() < self.TIME_THRESHOLD)): 
            return self.evaluateGame(board,player_wins,enemy_wins)

        moves = board.generate_valid_moves(board.player_turn)
        random.shuffle(moves)

        minscore = math.inf

        for m in moves:
            board_copy = deepcopy(board)
            board_copy._do_move(m[0],m[1])

            board_copy.player_turn = board_copy.get_enemy(board_copy.player_turn)
            
            score = 0.99 * self.max_func(original_board,board_copy, depth - 1)

            if score < minscore:
                minscore = score
                
        return minscore
    
    def max_func(self,original_board,board,depth):
        
        color = board.player_turn
        
        player_wins = board.check_winning_condition(color)
        enemy_wins = board.check_winning_condition(board.get_enemy(color))
        game_ends = player_wins or enemy_wins 
        
        if ((depth <= 0) or game_ends or (original_board.get_time_left() < self.TIME_THRESHOLD)): 
            return self.evaluateGame(board,player_wins,enemy_wins)

        moves = board.generate_valid_moves(board.player_turn)
        random.shuffle(moves)

        maxscore = -math.inf

        for m in moves:
            board_copy = deepcopy(board)
            board_copy._do_move(m[0],m[1])

            board_copy.player_turn = board_copy.get_enemy(board_copy.player_turn)
            
            score = 0.99 * self.min_func(original_board,board_copy, depth - 1)

            if score < maxscore:
                maxscore = score
                
        return maxscore


