import time
import random
import math
from copy import deepcopy, copy
from studentagent import *
from NegaMaxMoveAgent import *
from MiniMaxAgent import *
from PVS import *
from MiniMaxTransposition import *


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

    def __init__(self,color,delay=0, threshold=5):
        self.delay = delay
        self.TIME_THRESHOLD = threshold
        self.color = color
    
    def evaluateGame(self,board, player_wins, enemy_wins):
        #print("Evaluation of board started.")
        SCORE_WIN    = 1000
        
        SCORE_PAWN   = 10
        SCORE_ROOK   = 50
        SCORE_BISHOP = 30
        SCORE_KNIGHT = 30
        
        SCORE_CHECK     = 5
        
        color = self.color
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
                fig_name = (figure.abbriviation).lower() 
                if fig_name == 'p':
                    figurescore = SCORE_PAWN
                elif fig_name=='r':
                    figurescore = SCORE_ROOK
                elif fig_name=='b':
                    figurescore = SCORE_BISHOP
                elif fig_name=='n':
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
        
        board = deepcopy(gui.chessboard)
        
        search_depth = 2
        maxscore = -math.inf
        
        bestmoves = []

        #print("First, valid moves are generated.")
        moves = board.generate_valid_moves(board.player_turn)
        random.shuffle(moves)
        
        if len(moves) > 0:
            # always have one move to to
            gui.chessboard.update_move(moves[0])


            #print("We will test ", len(moves), " main moves.")
            for m in moves:

                
                # COPY
                _from_fig = board[m[0]]
                _to_fig = board[m[1]]
                player, move_number = board.get_current_state()        

                # PERFORM
                board._do_move(m[0],m[1])
                board.switch_players()

                #print("We test main move: ", m, " and the board looks like this:")
                #board_copy.pprint()
                #print("Main move test start.")
                
                #board.board_states.append(board.to_string())
                
                score = self.min_func(gui.chessboard,board, search_depth)
                """
                print("\n\n----------------------\n\n")
                print("Main move " + "(" +m[0] + ", " + m[1] + ")" + " with score " + str(score) + " test end.\n\n")
                for state in board.board_states:
                    print(state)
                print("\n\n----------------------\n\n")
                board.board_states.pop()
                """


                 # RESET
                board[m[0]] = _from_fig
                board[m[1]] = _to_fig
                board.player_turn = player
                board.fullmove_number = move_number 
                
                if score > maxscore:
                    maxscore = score
                    bestmoves.clear()
                    bestmoves.append(m)
                    gui.chessboard.update_move(m)
                elif score == maxscore:
                    bestmoves.append(m)

            bestmove = bestmoves[random.randint(0,len(bestmoves)-1)]
            gui.chessboard.update_move(bestmove)
            gui.perform_move()
        gui.chessboard.engine_is_selecting = False
        
    

    def min_func(self,original_board,board,depth):
        
        color = self.color
        
        player_wins = board.check_winning_condition(color)
        enemy_wins = board.check_winning_condition(board.get_enemy(color))
        game_ends = player_wins or enemy_wins 
        
        if ((depth <= 0) or game_ends or (original_board.get_time_left() < self.TIME_THRESHOLD)): 
            return self.evaluateGame(board,player_wins,enemy_wins)

        moves = board.generate_valid_moves(board.player_turn)
        random.shuffle(moves)

        minscore = math.inf

        for m in moves:
            # COPY
            _from_fig = board[m[0]]
            _to_fig = board[m[1]]
            player, move_number = board.get_current_state()        

            # PERFORM
            board._do_move(m[0],m[1])
            board.switch_players()
            
            #board.board_states.append(board.to_string())
            
            score = 0.99 * self.max_func(original_board,board, depth - 1)

            """
            print("\n\n----------------------\n\n")
            print("Score for this move sequence is: ", score)
            for state in board.board_states:
                print(state)
            print("\n\n----------------------\n\n")
            board.board_states.pop()
            """
            
            # RESET
            board[m[0]] = _from_fig
            board[m[1]] = _to_fig
            board.player_turn = player
            board.fullmove_number = move_number 

            if score < minscore:
                minscore = score
                
        return minscore
    
    def max_func(self,original_board,board,depth):
        
        color = self.color
        
        player_wins = board.check_winning_condition(color)
        enemy_wins = board.check_winning_condition(board.get_enemy(color))
        game_ends = player_wins or enemy_wins 
        
        if ((depth <= 0) or game_ends or (original_board.get_time_left() < self.TIME_THRESHOLD)): 
            return self.evaluateGame(board,player_wins,enemy_wins)

        moves = board.generate_valid_moves(board.player_turn)
        random.shuffle(moves)

        maxscore = -math.inf

        for m in moves:
            # COPY
            _from_fig = board[m[0]]
            _to_fig = board[m[1]]
            player, move_number = board.get_current_state()        

            # PERFORM
            board._do_move(m[0],m[1])
            board.switch_players()
            
            #board.board_states.append(board.to_string())
            
            score = 0.99 * self.min_func(original_board,board, depth - 1)
            
            """
            print("\n\n----------------------\n\n")
            print("Score for this move sequence is: ", score)
            for state in board.board_states:
                print(state)
            print("\n\n----------------------\n\n")
            board.board_states.pop()
            """
            
            # RESET
            board[m[0]] = _from_fig
            board[m[1]] = _to_fig
            board.player_turn = player
            board.fullmove_number = move_number 

            if score > maxscore:
                maxscore = score
                
        return maxscore
