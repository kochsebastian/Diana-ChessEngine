import threading
import sys
from agents import *

# Python program using 
# traces to kill threads   
class thread_with_trace(threading.Thread): 
    
    def __init__(self, *args, **keywords): 
        threading.Thread.__init__(self, *args, **keywords) 
        self.killed = False
  
    def start(self): 
        self.__run_backup = self.run 
        self.run = self.__run       
        threading.Thread.start(self) 
  
    def __run(self): 
        sys.settrace(self.globaltrace) 
        self.__run_backup() 
        self.run = self.__run_backup 
  
    def globaltrace(self, frame, event, arg): 
        if event == 'call': 
            return self.localtrace 
        else: 
            return None
  
    def localtrace(self, frame, event, arg): 
        if self.killed: 
            if event == 'line': 
                raise SystemExit() 
        return self.localtrace 
  
    def kill(self): 
        self.killed = True



def update_clock(board, label,time, turn_time,player,root):
    
    if not board.game_ended:
    
        if not(player == board.player_turn):
                time = turn_time
                board.timer = turn_time
                player = board.player_turn

        label.configure(text=str(max(math.floor(time),0)))
        board.timer = time

        root.after(500, update_clock, board, label,time-0.5, turn_time,player,root)


def startGame(root,board,gui):

    if not board.game_ended:

        if not board.engine_is_selecting:

            color = board.player_turn

            PLAYER_1 = board.PLAYER_1
            PLAYER_2 = board.PLAYER_2

            if PLAYER_1 > 1 and color=="white":
                board.engine_is_selecting = True
                t = None
                #print("Engine starts now:")

                if PLAYER_1 == 2:
                    t = thread_with_trace(target = MrRandom().generate_next_move, args=(gui,))
                elif PLAYER_1 == 3:
                    t = thread_with_trace(target = MrNovice().generate_next_move, args=(gui,))
                elif PLAYER_1 == 4:
                    t = thread_with_trace(target = MrExpert().generate_next_move, args=(gui,))
                elif PLAYER_1 == 5:
                    t = thread_with_trace(target = MrCustom().generate_next_move, args=(gui,))

                gui.current_engine_thread = t
                t.start()
                #print("thread white started:")


            elif PLAYER_2 > 1 and color=="black":
                board.engine_is_selecting = True
                t = None
                #print("Engine starts now:")

                if PLAYER_2 == 2:
                    t = thread_with_trace(target = MrRandom().generate_next_move, args=(gui,))
                elif PLAYER_2 == 3:
                    t = thread_with_trace(target = MrNovice().generate_next_move, args=(gui,))
                elif PLAYER_2 == 4:
                    t = thread_with_trace(target = MrExpert().generate_next_move, args=(gui,))
                elif PLAYER_2 == 5:
                    t = thread_with_trace(target = MrCustom().generate_next_move, args=(gui,))
  
                gui.current_engine_thread = t
                t.start()
                #print("thread black started:")

        root.after(500, startGame, root, board, gui)

def stopClock(root,board,gui):
    if board.timer <= 0:
        thread = gui.current_engine_thread
        #print("timer is out.")
        if thread is not None:
            thread.kill() 
            thread.join()
            gui.current_engine_thread = None
            #print("thread was killed.")

        print(board.player_turn," chose move: ", board.next_move)
        if board.player_turn == "white" and board.PLAYER_1 == 1 or board.player_turn == "black" and board.PLAYER_2 == 1:
            print("Timeout with no valid move: ", board.get_enemy(board.player_turn), " won!")
            gui.label.configure(text="Timeout with no valid move: " + board.get_enemy(board.player_turn) + " won!")
            board.end_game(gui)
        else:
            if (board.next_move is not None):
                gui.perform_move()
            else:
                print("Timeout with no valid move: ", board.get_enemy(board.player_turn), " won!")
                gui.label.configure(text="Timeout with no valid move: " + board.get_enemy(board.player_turn) + " won!")
                board.end_game(gui)

            board.engine_is_selecting = False
    else:
        root.after(200, stopClock, root, board,gui)