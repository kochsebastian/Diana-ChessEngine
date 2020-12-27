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

# After perform_move(), make sure that the agent does not continue searching for moves!

pieces = {  'P': Pawn("white"),
            'p': Pawn("black"),
            'R': Rook("white"),
            'r': Rook("black"),
            'N': Knight("white"),
            'n': Knight("black"),
            'B': Bishop("white"),
            'b': Bishop("black"),
            'K': King("white"),
            'k': King("black"),
            '-': None
        }
transposition_table = {}
# SCORE_WIN    = 100000
        
# SCORE_PAWN   = 20
# SCORE_ROOK   = 50
# SCORE_BISHOP = 25
# SCORE_KNIGHT = 40
# SCORE_QUEEN  = 0
# SCORE_KING  = 100000

# SCORE_CHECK     = 80


SCORE_WIN    = 1000
        
SCORE_PAWN   = 10
SCORE_ROOK   = 40
SCORE_BISHOP = 30
SCORE_KNIGHT = 28
SCORE_KING  = 0

SCORE_CHECK     = 20

piece_values = {    'p': SCORE_PAWN,
                    'r': SCORE_ROOK,
                    'k': SCORE_KING,
                    'n': SCORE_KNIGHT,
                    'b': SCORE_BISHOP,
                }

class MrCustom:

    def __init__(self,delay=0,threshold=5):
        print('Student is playing')
        self.delay = delay
        self.TIME_THRESHOLD = threshold
    

    def set_fen(self,board,fen):
        position, turn = fen.split(' ')
        rows = position.split('/')
        # rows.reverse()
        
        # for i,x in enumerate(board.axis_x):
        #     for j,y in enumerate(board.axis_y):
        #         board[y+str(x)] = pieces[rows[i][j]]
        # BOARD_INIT = [["r","b","n","k","b","r"],["p"]*6,[None]*6,[None]*6,["P"]*6,["R","B","N","K","B","R"]]
        
        board.clear()
        
        for x, row in enumerate(rows):
            for y, letter in enumerate(row):
                coord = board.letter_notation(((6-1)-x,y))
                if letter is '-':
                    board[coord] = None
                else:
                    board[coord] = piece(letter)
                    board[coord].place(board)

        board.player_turn = turn
        
        board.castling = "-"
        board.en_passant = "-"
        board.halfmove_clock = 0
        board.fullmove_number = 1   

        return board
    
    def build_fen(self,board):

        fen_rows = []
        for i,x in enumerate(board.axis_x):
            fen_row=''
            for j,y in enumerate(board.axis_y):
                try:
                    fen_row+=board[y+str(x)].abbriviation
                except Exception:
                    fen_row+='-'
            fen_row+='/'
            fen_rows.append(fen_row)
        fen_rows.reverse()
        fen=''.join(fen_rows)
            
        fen = fen[:-1]
        fen += ' '
        fen += board.player_turn
        return fen


    def evaluateGame(self, board):
        #print("Evaluation of board started.")
        
        
        color = board.player_turn
        score = 0

        #print("Check winning score")
        t1 = time.time()
        score+=self.checkmate_score(board)
        t2 = time.time()
        #print("Checking winning in evaluation: ", t2-t1)
        
        
        #print("Is in Check score")
        score +=self.check_score(board)
        t2 = time.time()
        #print("Checking Is in Check in evaluation: ", t2-t1)
        
        #print("Calc material score")
        t1 = time.time()
        # fen = "r-n-br/-pbkpp/pPp---/P-PpP-/---PNP/RB-KBR "+color
        # self.set_fen(board,fen)
        score +=self.material_score(board)
        t2 = time.time()
        #print("Checking Score Calc in evaluation: ", t2-t1)            
        
        #print("calc attack score")
        score += self.attack_score(board)
        #print("Evaluation of board ended.")
        
        return score

    def material_score(self,board):
        color = board.player_turn
        score = 0
        for coord in board.keys(): 
            if (board[coord] is not None):
                figure = board[coord]
                fig_color = board[coord].color
                piece = figure.abbriviation.lower()
                figurescore = 0
                figurescore = piece_values[piece]
                if fig_color == color:
                    score += figurescore
                else:
                    score -= figurescore
        return score
    
    def attack_score(self,board):
        return self.threats(board)

    def checkmate_score(self,board):
        color = board.player_turn
        player_wins = board.check_winning_condition(color)
        enemy_wins = board.check_winning_condition(board.get_enemy(color))
        game_ends = player_wins or enemy_wins
        if player_wins:
            return SCORE_WIN
        elif enemy_wins:
            return -SCORE_WIN
        else:
            return 0
    
    def check_score(self,board):
        color = board.player_turn
        score = 0
        if board.is_in_check(color):
            score -= SCORE_CHECK
        
        if board.is_in_check(board.get_enemy(color)):
            score += SCORE_CHECK
        return score

    def sort_moves(self,moves,board):
        #encorage taking with lower valued pieces
        tick = time.time()
        color = board.player_turn

        sorted_moves = []
        check_moves = []
        threat_moves = []
        threatened_pieces = []
        capture_moves = []
        last_moves =[]
        for m in moves:
            board_copy,before = self.do_move(board,m)
            
            if board_copy.check_winning_condition(color):
                sorted_moves.insert(0,m)
                
            elif board_copy.is_in_check(board.get_enemy(color)):
                check_moves.append(m)
                
            elif self.is_capture_move(board,m):
                capture_moves.append(m)
                
            elif self.is_threatening_move(board_copy,m):
                threat_moves.append(m)
                
            elif board_copy.check_winning_condition(board.get_enemy(color)):
                last_moves.append(m)
            
            else:
                last_moves.insert(0,m)
            board = self.undo_move(board_copy,m,before)
        # print(f"Sorting took {tick-time.time()}s")
        return (sorted_moves+check_moves+threat_moves+capture_moves+last_moves)


    def generate_next_move(self,gui):
        
        #print("Next move will now be generated:")
        
        board = gui.chessboard
        color = "white"
        # fen = "rb-kbr/pppppp/-n----/P-----/-PPPPP/RBNKBR "+color
        # self.set_fen(board,fen)
        
        # search_depth = 1

        # bestmove = self.select_move(board,deepcopy(board),search_depth)

        # for search_depth in range(1,12):
        #     if board.get_time_left()>self.TIME_THRESHOLD*search_depth:
        #         bestmove = self.choose_move_negaMax(board,deepcopy(board),search_depth)

        score, bestmove = self.negaMax_move(board,deepcopy(board),-100000,100000,1,3,1)
        board.update_move(bestmove)
        gui.perform_move()
        board.engine_is_selecting = False
        print(self.build_fen(board))

  

    
    # def select_move(self,orig_board,board,depth, maximize=True):
    #     # bestMove = -9999
    #     # bestMoveFinal = None
    #     maxscore = -math.inf
    #     bestmoves = []

    #     score, move = self.alphabeta_move(orig_board,board,-100000,100000,depth,True)
    #     print(f"Move {move} has Score {score}")
    #     return move
       

    # def alphabeta_move(self,orig_board,board,alpha,beta,depthleft,maximize,incoming_move=None):
    #     fen = self.build_fen(board).encode('utf-8')
    #     hash_fen = int(hashlib.md5(fen).hexdigest(), 16)


    #     color = board.player_turn
    #     player_wins = board.check_winning_condition(color)
    #     enemy_wins = board.check_winning_condition(board.get_enemy(color))
    #     game_ends = player_wins or enemy_wins 
        
    #     moves = board.generate_valid_moves(board.player_turn)
    #     # scores,moves = self.sort_moves(moves,board)
    #     if maximize:
    #         if ((depthleft <= 0) or game_ends or (orig_board.get_time_left() < self.TIME_THRESHOLD)):
    #             score = self.quiesce(board, alpha, beta )
    #             transposition_table[hash_fen] = score
    #             return score,None
    #         value = -99999
    #         move = None
    #         for m in moves:
    #             board,before = self.do_move(board,m)
    #             score, _ = self.alphabeta_move(orig_board,board,alpha,beta,depthleft-1, False,m)
    #             board = self.undo_move(board,m,before)
    #             # value = max(value,score)
    #             value = score
               
    #             # alpha = max(alpha,value)
    #             if value > alpha:
    #                 move = m
    #                 alpha = value
    #             if  beta <= alpha:
    #                 print("cut branch")
    #                 break
    #                 # return value, move
                
                
    #         return value, move

    #     else:
    #         if ((depthleft <= 0) or game_ends or (orig_board.get_time_left() < self.TIME_THRESHOLD)):
    #             score = -self.quiesce(board, alpha, beta )
    #             transposition_table[hash_fen] = score
    #             return score,None
    #         value = 99999
    #         move = None
    #         for m in moves:
    #             board,before = self.do_move(board,m)
    #             score, _ = self.alphabeta_move(orig_board,board,alpha,beta,depthleft-1, True,m)
    #             board = self.undo_move(board,m,before)
    #             # value = min(value,score)
    #             value = score
    #             # beta = min(value,beta)
    #             if value < beta:
    #                 beta = value
    #                 move = m
    #             if beta <= alpha:
    #                 print("cut branch")
    #                 break
    #                 # return value, move
                
         
    #         return value, move

    def choose_move_negaMax(self,orig_board,board,depth):
        bestMove = None
        bestValue = -99999
        alpha = -100000
        beta = 100000
        moves = board.generate_valid_moves(board.player_turn)
        sorted_moves = self.sort_moves(moves,board)
        for move in sorted_moves:
            board ,before = self.do_move(board,move)
            fen = self.build_fen(board).encode('utf-8')
            hash_fen = int(hashlib.md5(fen).hexdigest(), 16)
            if transposition_table.get(hash_fen, None) != None:
                score, depth_score = transposition_table[hash_fen]
                if depth_score > depth:
                    print('restored position')
                    boardValue = score
                else:
                    boardValue = -self.negaMax(orig_board,board,-beta, -alpha, depth-1)
                    transposition_table[hash_fen] = boardValue, depth
            else:
                boardValue = -self.negaMax(orig_board,board,-beta, -alpha, depth-1)
                transposition_table[hash_fen]= boardValue, depth
            board = self.undo_move(board,move,before)
            if boardValue > bestValue:
                bestValue = boardValue
                bestMove = move
            if( boardValue > alpha ):
                alpha = boardValue
        return bestMove

    def negaMax(self,orig_board,board, alpha, beta, depthleft, depth=1 ) :
        bestscore = -9999
        if( depthleft == 0 or orig_board.get_time_left()<=self.TIME_THRESHOLD):
            return self.quiesce(board, alpha, beta, depth,2)
        
        moves = board.generate_valid_moves(board.player_turn)
        sorted_moves = self.sort_moves(moves,board)
        for move in sorted_moves:
            board,before = self.do_move(board,move)
            fen = self.build_fen(board).encode('utf-8')
            hash_fen = int(hashlib.md5(fen).hexdigest(), 16)
            if transposition_table.get(hash_fen, None) != None:
                score, depth_score = transposition_table[hash_fen]
                if depth_score > depth:
                    print('restored position')
                    boardValue = score
                else:
                    boardValue = -self.negaMax(orig_board,board,-beta, -alpha, depth-1)
                    transposition_table[hash_fen] = boardValue, depth
            else:
                score = -self.negaMax(orig_board,board, -beta, -alpha, depthleft - 1, depth+1 )
                transposition_table[hash_fen]=score, depth+1
            board = self.undo_move(board,move,before)
            if( score >= beta ):
                print("cut branch")
                return score
            if( score > bestscore ):
                bestscore = score
                if( score > alpha ):
                    alpha = score   
        return bestscore

    def negaMax_move(self,orig_board,board,alpha,beta,depth,depthleft,color):
        bestscore = -9999
        if( depthleft == 0 or orig_board.get_time_left()<=self.TIME_THRESHOLD):
            return self.quiesce(board, alpha, beta, depth,2),None
        
        moves = board.generate_valid_moves(board.player_turn)
        sorted_moves = self.sort_moves(moves,board)
        move = None
        for m in sorted_moves:
            board,before = self.do_move(board,m)
            score = -self.negaMax_move(orig_board,board, -beta, -alpha, depth+1,depthleft - 1 ,color*-1)[0]
            # alpha = max(alpha,score)
            board = self.undo_move(board,m,before)
            if( score >= beta ):
                return score, move
            if( score > bestscore ):
                move = m
                bestscore = score
                if( score > alpha ):
                    alpha = score           
        return bestscore, move
    
    def quiesce(self,board, alpha, beta, depth, depthleft ):
        color = board.player_turn
        if depthleft<=0:
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
                # fen = self.build_fen(board).encode('utf-8')
                # hash_fen = int(hashlib.md5(fen).hexdigest(), 16)
                # if transposition_table.get(hash_fen, None) != None:
                #     score, depth_score = transposition_table[hash_fen]
                #     if depth_score > depth:
                #         print('restored position')
                #         boardValue = score
                #     else:
                #         boardValue = -self.negaMax(orig_board,board,-beta, -alpha, depth-1)
                #         transposition_table[hash_fen] = boardValue, depth
                # else:
                #     score = -self.quiesce(board, -beta, -alpha,depth+1,depthleft-1)
                #     transposition_table[hash_fen]=score,depth+1
                score = -self.quiesce(board, -beta, -alpha,depth+1,depthleft-1)
                board = self.undo_move(board,move,before)
                if( score >= beta ):
                    print("cut branch")
                    return beta
                if( score > alpha ):
                    alpha = score  
        return alpha

    def is_capture_move(self,board,move):
        turn = board.player_turn
        goal = move[1]
        if board[move[1]] != None:
            if board[move[1]].color == board.get_enemy(board.player_turn):
                return True
        return False
    
    def is_threatening_move(self,board,move):
        if board[move[1]] == None:
            return False
        goals = list(board[move[1]].possible_moves(move[1]))
        for g in goals:
            if board[g]!=None:
                if board[g].color == board.get_enemy(board.player_turn):
                    return True

        return False

    def threats(self,board):
        # if enemy piece is attacked by lower value piece add score
        color = board.player_turn
        score = 0
        moves = board.generate_valid_moves(color)
        for move in moves:
            if self.is_threatening_move(board,move):
                from_value = piece_values[board[move[0]].lower()]
                to_value = piece_values[board[move[1]].lower()]
                if from_value < to_value:
                    score += (to_value - from_value)*0.5

        enemy_moves = board.generate_valid_moves(board.get_enemy(board.player_turn))
        for move in enemy_moves:
            if self.is_threatening_move(board,move):
                from_value = piece_values[board[move[0]].abbriviation.lower()]
                to_value = piece_values[board[move[1]].abbriviation.lower()]
                if from_value < to_value:
                    score -= (to_value - from_value)*0.5
        return score




    def undo_move(self,board,m,before):
        # RESET
        player = before[0]
        move_number = before[1]
        _from_fig = before[2]
        _to_fig = before[3]
        board[m[0]] = _from_fig
        board[m[1]] = _to_fig
        board.player_turn = player
        board.fullmove_number = move_number 
        return board

        
    def do_move(self, board, m):
        # COPY

        _from_fig = board[m[0]]
        _to_fig = board[m[1]]
        player, move_number = board.get_current_state()  

        # PERFORM
        board._do_move(m[0],m[1])
        board.switch_players()

        return board, (player,move_number,_from_fig,_to_fig)



    


    


