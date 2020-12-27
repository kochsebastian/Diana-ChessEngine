

import time
import random
import math
from copy import deepcopy, copy
import hashlib
from studentagent import *
from pieces import *
from collections import Counter



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



SCORE_WIN    = 1000
        
SCORE_PAWN   = 10
SCORE_ROOK   = 40
SCORE_BISHOP = 30
SCORE_KNIGHT = 28
SCORE_KING  = 99

SCORE_CHECK     = 10

piece_values = {    'p': SCORE_PAWN,
                    'r': SCORE_ROOK,
                    'k': SCORE_KING,
                    'n': SCORE_KNIGHT,
                    'b': SCORE_BISHOP,
                }



pawn_square_table = [   [0,0,0,0,0,0],
                        [50,50,50,50,50,50],
                        [10,20,30,30,20,10],
                        [5,0,20,20,0,5],
                        [5,10,-20,-20,10,5],
                        [0,0,0,0,0,0]]

knight_square_table = [ [-50,-40,-30,-30,-40,-50],
                        [-40,-20,0,0,-20,-40],
                        [-30,5,15,15,5,-30],
                        [-30,10,15,-5,5,-30],
                        [-40,-20,5,5,10,-40],
                        [-50,-40,-30,-30,-40,-50]]

bishop_square_table = [ [-20,-10,-10,-10,-10,-20],
                        [-10,0,0,0,0,-10],
                        [-10,5,10,10,5,-10],
                        [-10,10,5,5,10,-10],
                        [5,0,10,10,0,5],
                        [-50,-40,-30,-30,-40,-50]]

rook_square_table = [   [0,0,0,0,0,0],
                        [5,10,10,10,10,5],
                        [0,0,0,0,0,0],
                        [0,0,0,0,0,0],
                        [-5,0,0,0,0,-5],
                        [0,0,5,5,0,0]]

king_earlygame_table = [[-30,-40,-50,-50,-40,-30],
                        [-30,-40,-50,-50,-40,-30],
                        [-30,-40,-50,-50,-40,-30],
                        [-20,-20,-20,-20,-20,-10],
                        [20,20,0,0,20,20],
                        [20,30,5,5,30,20]]

king_endgame_table = [  [-50,-40,-25,-25-40,-50],
                        [-30,-20,-5,-5,-20,-30],
                        [-30,-10,15,15,-10,-30],
                        [-30,-10,25,25,-10,-30],
                        [-30,-30,0,0,-30,-30],
                        [-50,-30,-30,-30,-30,-50]]

piece_squares = {   'p': [pawn_square_table,pawn_square_table],
                    'r': [rook_square_table,rook_square_table],
                    'k': (king_earlygame_table,king_endgame_table),
                    'n': [knight_square_table,knight_square_table],
                    'b': [bishop_square_table,bishop_square_table],
        }

class SuperAgent:
    def __init__(self,delay=0,threshold=5):
        # print('Student is playing')
        self.delay = delay
        self.TIME_THRESHOLD = threshold
        self.transposition_table = {}
        self.endgame = False
        self.color = None
        

        # time.sleep(20)
    
    def generate_next_move(self,gui):

        board = gui.chessboard
        
        moves = board.generate_valid_moves(board.player_turn)
        if len(moves) > 0:
            a = random.randint(0,len(moves)-1)
            board.update_move(moves[a])
            gui.perform_move()
        board.engine_is_selecting = False

    def set_fen(self,board,fen):
        position, turn = fen.split(' ')
        rows = position.split('/')
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

    def evaluateGame(self,board):
        return self.evaluateGame_normal(board)
        # return self.evaluateGame_multi(board)

    def evaluateGame_normal(self, board):
        ticktick = time.time()
        tick = time.time()
        color = board.player_turn
        score = 0
        w_material = 1
        w_check = 1
        w_checkmate = 1
        w_atacks =1 
        w_position = 1

        score +=w_check*self.check_score(board,color)
        if score != 0:
            score+=w_checkmate*self.checkmate_score(board,color)
        tock = time.time()
        # print(f"Eval checkmate: {tock-tick}s")

        # score +=w_check*self.check_score(board,color)
        tick=time.time()
        # print(f"Eval check: {tick-tock}s")

        score += w_material*self.material_score(board,color)
        tock=time.time()
        # print(f"Eval material: {tock-tick}s")

        # score += w_atacks*self.attack_score(board,color)
        tick=time.time()
        # print(f"Eval attacks: {tick-tock}s")
        # print(f"Eval: {time.time()-ticktick}s")
        return score

   

    

    def evaluateGame_difference(self, board,moves):
        ticktick = time.time()
        # moves = [item for t in moves for item in t] 

        # moves = list(set(moves))

        tick = time.time()
        color = board.player_turn
        score = 0
        w_material = 1
        w_check = 1
        w_checkmate = 1
        w_atacks =1 
        w_position = 1


        score +=w_check*self.check_score(board,color)
        if score != 0:
            score+=w_checkmate*self.checkmate_score(board,color)
        tock = time.time()
        # print(f"Eval checkmate: {tock-tick}s")


        # orig_board=self.board
        tick=time.time()
        # print(f"Eval check: {tick-tock}s")

        score += w_material*self.material_score(board,color)
        tock=time.time()
        # print(f"Eval material: {tock-tick}s")

        # score += w_atacks*self.attack_score(board,color)
        tick=time.time()
        # print(f"Eval attacks: {tick-tock}s")
        # print(f"Eval: {time.time()-ticktick}s")
        # boardScore = self.evaluateGame(board)
        # diffScore =self.score_origBoard + score
        # if boardScore!=diffScore:
        #     print()
        return  score


    def material_score_difference(self,orig_board,board,color,squares):
            
        score = 0
        for coord in squares: 
            if (board[coord] != None):
                figure = board[coord]
                mobility = self.material_mobility_score(figure,coord)
                fig_color = board[coord].color
                piece = figure.abbriviation.lower()
                position_score = self.material_position_score(board,coord,piece,fig_color)
                figurescore = piece_values[piece]
                if fig_color == color:
                    score += figurescore+0.5*mobility+0.5*position_score
                else:
                    score -= figurescore+0.5*mobility+0.5*position_score

        for coord in squares: 
            if (orig_board[coord] != None):
                figure = orig_board[coord]
                mobility = self.material_mobility_score(figure,coord)
                fig_color = orig_board[coord].color
                piece = figure.abbriviation.lower()
                position_score = self.material_position_score(orig_board,coord,piece,fig_color)
                figurescore = piece_values[piece]
                if fig_color == color:
                    score -= figurescore+0.5*mobility+0.5*position_score
                else:
                    score += figurescore+0.5*mobility+0.5*position_score
        return score




################
    def material_score(self,board,color):
        mobility=0
        position_score=0
        score = 0
        for coord in board.keys(): 
            if (board[coord] != None):
                figure = board[coord]
                mobility = self.material_mobility_score(figure,coord)
                fig_color = board[coord].color
                piece = figure.abbriviation.lower()
                position_score = self.material_position_score(board,coord,piece,fig_color)
                figurescore = piece_values[piece]
                if fig_color == color:
                    score += figurescore+0.5*mobility+0.5*position_score
                else:
                    score -= figurescore+0.5*mobility+0.5*position_score
        return score

   
    def material_position_score(self,board,coord,piece,color):
        index=0
        if self.endgame:
            index=1
        piece_sqare_table = piece_squares[piece][index]
        if color == "white":
            piece_sqare_table = piece_sqare_table[::-1]
        position = board.number_notation(coord)
        return piece_sqare_table[position[0]][position[1]]
        
    def material_mobility_score(self,piece,position):
        num_moves = len(list(piece.possible_moves(position)))
        return num_moves
    
    def attack_score(self,board,color):
        return self.threats(board,color)

    def checkmate_score(self,board,color):
        # player_wins = board.check_winning_condition(color)
        # enemy_wins = board.check_winning_condition(board.get_enemy(color))
        # game_ends = player_wins or enemy_wins
        if board.is_in_checkmate(color):
            return -SCORE_WIN
        # elif enemy_wins:
        #     return -SCORE_WIN
        else:
            return 0


    
    def check_score(self,board,color):
        # color = board.player_turn
        score = 0
        if board.is_in_check(color):
            score -= SCORE_CHECK
        
        # if board.is_in_check(board.get_enemy(color)):
        #     score += SCORE_CHECK
        return score

    

    def sort_moves(self,moves,board):
        #encorage taking with lower valued pieces
        # in the endgame active pieces stay active while inactive pieces stay in active
        tick = time.time()
        color = board.player_turn

        sorted_moves = []
        check_moves = []
        threat_moves = []
        threatened_pieces = []
        capture_moves = []
        last_moves =[]
        for m in moves:
            capture = False
            if self.is_capture_move(board,m):
                capture = True
                capture_moves.append(m)
            

            board,before = self.do_move(board,m)
            if board.is_in_check(board.player_turn):
                check_moves.append(m)
                if capture == True:
                    capture_moves.pop()
                if board.is_in_checkmate(board.player_turn):
                    sorted_moves.insert(0,m)
                    check_moves.pop()
            elif self.is_threatening_move(board,m):
                threat = True
                threat_moves.append(m)
            
            else:
                last_moves.insert(0,m) # don't search these moves with high depth
            board = self.undo_move(board,m,before)
        return (sorted_moves+check_moves+threat_moves+capture_moves+last_moves)

    def sort_moves_nonquiet(self,moves,board):
        #encorage taking with lower valued pieces
        # in the endgame active pieces stay active while inactive pieces stay in active
        tick = time.time()
        color = board.player_turn

        sorted_moves = []
        check_moves = []
        threat_moves = []
        threatened_pieces = []
        capture_moves = []
        last_moves =[]
        for m in moves:
            if self.is_capture_move(board,m):
                capture_moves.append(m)
            elif self.is_threatening_move(board,m):
                threat_moves.append(m)

            board,before = self.do_move(board,m)
            if board.is_in_check(board.get_enemy(color)):
                check_moves.append(m)
                if board.check_winning_condition(color):
                    sorted_moves.insert(0,m)
                    check_moves.pop()
                
            
                
            
                
            board = self.undo_move(board,m,before)
        return (sorted_moves+check_moves+capture_moves+threat_moves)

   




  

    def is_capture_move(self,board,move):
        turn = board.player_turn
        goal = move[1]
        if board[move[1]] != None:
            if board[move[1]].color == board.get_enemy(board.player_turn):
                return True
        return False
    
    def is_threatening_move(self,board,move):
        # if board[move[1]] == None:
        #     return False
        goals = list(board[move[1]].possible_moves(move[1]))
        for g in goals:
            if board[g]!=None:
                if board[g].color != board[move[1]].color:
                    return True

        return False

    def threats(self,board,color):
        # if enemy piece is attacked by lower value piece add score
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



    


    


