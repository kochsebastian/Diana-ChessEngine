Notes for Assignment 6 (Chess AI)
--------------------------------------------------------------------------------

o We recommend using an IDE (like Pycharm) for working on this assignment.

o First, you need to install python pillow package by executing the following command in terminal:

  § pip install Pillow

  If you are using Pycharm, you can also add the package from:
  File-> Settings-> Project:dianachess-> Project Interpreter. Click the '+' sign to 
  add new packages. Search Pillow and install the package.

o The game gui can be started by running the script 'dianachess.py' the following way:

  § python dianachess.py -w <white player> -b <black player> -t <turn time>

  - You can take the following options for both white and black players:
    -- Human : If you want to try play chess manually.
    -- MrRandom : If you want to select the random agent.
    -- MrNovice : If you want to select the agent with Min-Max agent with max 
                  depth level 2
    -- MrExpert : (Not inlcuded in the template) An agent which with a higher
                  depth which we keep for competition only
    -- Student: Your agent
  
  - The default turn tume is 30 seconds. If you want to change this for testing,
    just give another time in seconds for turn time.

  For example: § python dianachess.py -w Human -b MrExpert -t 20
  
  - Default: white player: Human
             black player: Human
             turn time: 30 seconds 


o Please note that for the evaluation, the value 30 will be used (pending further
  tests, a higher value may instead be used to account for the server running 
  the games being slightly slower, however your agent should be prepared for being 
  given less time than expected by registering preliminary moves)

o If your agent is still running after the timelimit has passed, your agent will
  lose unless you have registered a preliminary move with update_move. See the 
  template studentagent.py for details.

o You must rename the file studentagent.py to the last name of both team members 
  (e.g. rahimshamsafar.py} for Rahim and Shamsafar). Rename the class MrCustom with a 
  class named with both your last names e.g RahimShamsafar inside that file. Your agent's
  functionality should be similar to the class MrNovice in agents.py. Details are provided
  in the comments of the template class. You are not allowed to modify any other file in the 
  program, so please make sure your agent works with the base version of the
  game as distributed. Please do not split your implementation across multiple files. 

  Important: please include some documentation for your agent (either as
  comments in the py file or as a separate document). Document which algorithm
  you are using, what the idea behind your heuristic/evaluation function is, etc.

o If you find any inefficiency in the code (e.g in board.py, agents.py or pieces.py)
  and you can suggest any improvement, you are allowed to send the tutors an email 
  till 22.12.20. If that suggestion improves the speed significantly, we will 
  modify the template for everyone till 23.12.20. If its not a significant change or 
  its after the due date, we will ignore the changes. You can also report bugs in the
  implementation.
  
o You are allowed to use any basic package in python that helps in your implementation.

o Your agent should be single-threaded. A multi-threaded agent will not get any
  marks for the assignment and will be disqualified from the tournament.

o Two agents are included in this framework to allow you to test your agent:

  - MrRandom: A very primitive agent that selects its moves randomly from the
    list of legal moves. Basically any agent should be able to beat this.

  - MrNovice: A minimax agent with a simple cutoff heuristic. After reaching a
    given depth in the gametree (or finding a leaf node) the current position
    will be evaluated by counting the material value of both players and whether
    a player's king is in check.

--------------------------------------------------------------------------------

Known Bugs:

o  If an agent makes a move there could be a graphical glitch for a short moment
