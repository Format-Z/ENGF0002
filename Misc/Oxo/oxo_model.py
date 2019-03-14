#Simple Noughts and Crosses Game, Mark Handley, 2018
from copy import deepcopy
from enum import IntEnum

WIN = 0
DRAW = 1
LOSE = 2
def result_str(result):
    strs = ("WIN", "DRAW", "LOSE")
    return strs[result]

def other_player(player):
    if player == "X":
        return "O"
    else:
        return "X"

    
# Note, computer plays O, human plays X

class Model():
    def __init__(self, controller):
        self.controller = controller
        self.init_game()

    def init_game(self):
        # We'll hold the board as a list of lists of strings, one for each square.
        # A '.' indicates no-one played this square.  Otherwise a
        # square should be "X" or"O"
        self.rows = [[".", ".", "."], [".", ".", "."], [".", ".", "."]]
        self.players_move = True
        self.game_over = False

    def display_board(self):
        s = ""
        for row in self.rows:
            for square in row:
                s += square
            s += "\n"
        print(s)

    def clear_board(self):
        self.init_game()
        self.controller.clear_board()

    def clone(self):
        model = Model(self.controller)
        model.rows = deepcopy(self.rows)
        return model

    # Human plays X, Computer plays O
    def x_plays(self, x, y):
        if self.game_over:
            self.clear_board()
            return

        if self.players_move == False:
            # computer is still thinking, so don't let human play...
            return

        if self.rows[y][x] != ".":
            # square has already been played
            return
        
        self.rows[y][x] = "X"
        self.controller.display_move("X", x, y)
        self.players_move = False

        # did the human win?
        winning_squares = self.test_for_win("X")
        if winning_squares is not None:
            self.game_over = True
            self.controller.win(winning_squares)
            return

        #are there any more squares left to play
        if self.all_played():
            self.game_over = True
            return

        # OK, choose my best move
        self.choose_move()

        # Did I win?
        winning_squares = self.test_for_win("O")
        if winning_squares is not None:
            self.game_over = True
            self.controller.win(winning_squares)
            return

        # Let the human play again
        self.players_move = True
        

    # test_for_win is called when the player indicated by the "player"
    # parameter has just played their move.  It checks if the move was
    # a winning move.  It returns None if the move was not a winning
    # move, and returns a list of (x,y) coordinates of the winning
    # squares if the move was a winning move.
    def test_for_win(self, player):
        # First, test the rows and columns for a win.  We just need to
        # count the number of positions played by the player in each
        # row and in each column. If that total is three, it's a
        # winning move.
        colcounts = [0, 0, 0]  # count for each column - we'll check all these at once.
        for y in range(3):
            rowcount = 0  # count for the current row.
            for x in range(3):
                if self.rows[y][x] == player:
                    rowcount += 1;
                    colcounts[x] += 1
                    if colcounts[x] == 3:
                        # this is a winning column.
                        return [(x,0), (x,1), (x,2)]
            if rowcount == 3:
                # this is a winning row.
                return [(0,y), (1,y), (2,y)]

        #Ok, didn't win horizontally or vertically
        #Now, check diagonals
        d1_count = 0
        d2_count = 0
        for i in range(3):
            if self.rows[i][i] == player:
                d1_count += 1
            if self.rows[2-i][i] == player:
                d2_count += 1
        if d1_count == 3:
            # the top left to bottom right diagonal is a win
            return [(0,0), (1,1), (2,2)]
        if d2_count == 3:
            # the bottom left to top right diagonal is a win
            return [(0,2), (1,1), (2,0)]

        #No, player didn't win
        return None

    # all_played returns True if all the squares have been played
    def all_played(self):
        for row in self.rows:
            for square in row:
                if square == ".":
                    return False
        return True


    # test_move checks whether "player", playing at position (x,y)
    # will result in a win, lose or draw, if both computer and human
    # play their best move.  "trace" keeps track of moves played so far,
    # but is only for debugging.
    def test_move(self, player, x, y, trace):
        #uncomment the next line to print out all the moves explored
        #print(trace, player)

        # play the move
        moves_tested = 1
        self.rows[y][x] = player

        # First, has someone won?
        winning_squares = self.test_for_win(player)
        if winning_squares is not None:
            # someone won.
            if player == "X":
                # human won, we lose
                return LOSE, moves_tested
            else:
                # we won
                return WIN, moves_tested

        # If no-one has won, have all the positions been played?
        if self.all_played():
            return DRAW, moves_tested

        # OK, not a win or a draw.  Carry on testing moves.
        scores = [0, 0, 0] #number of positions that WIN, LOSE, or
                           #DRAW respectively from this starting
                           #position
        
        # try out playing in all squares that don't alredy have a piece
        for y in range(3):
            for x in range(3):
                if self.rows[y][x] == ".": # this square is empty, so try it
                    
                    # we clone the model state, so we can test
                    # possible moves without messing up the current
                    # version of the model.  We'll use this cloned
                    # version to try moves.
                    model = self.clone()

                    # keep track of how we got here for debugging
                    newtrace = trace + " (" + str(x) + "," + str(y) + ")"

                    # see how this move does.
                    result, count = model.test_move(other_player(player), x, y, newtrace)

                    # record the outcome
                    scores[result] += 1
                    moves_tested += count

        # If it's our (i.e., the computer's) turn, and any of the next
        # moves result in a lose, then playing this position is a
        # LOSE.  If not, but any next move results in a draw, then the
        # human can still force a draw, so playing this move is rated
        # a DRAW.  Otherwise it's rate a WIN.
        if player == "O":
            if scores[LOSE] > 0:
                return LOSE, moves_tested
            elif scores[DRAW] > 0:
                return DRAW, moves_tested
            else:
                assert(scores[WIN] > 0)
                return WIN, moves_tested

        # If it's our opponents move, but any of the next moves result
        # in us winning, then this is a WIN for us.
        assert(player == "X")
        if scores[WIN] > 0:
            return WIN, moves_tested
        if scores[DRAW] > 0:
            return DRAW, moves_tested
        else:
            assert(scores[LOSE] > 0)
            return LOSE, moves_tested
        
        

    def choose_move(self):
        best = None
        moves_tested = 0
        for y in range(3):
            for x in range(3):
                if self.rows[y][x] == ".":
                    model = self.clone()
                    trace = "(" + str(x) + "," + str(y) + ")"
                    result, count = model.test_move("O", x, y, trace)
                    moves_tested += count
                    print("Position ", x, y, " predict: ", result, ", moves tested:", moves_tested)
                    msg1 = result_str(result)
                    msg2 = "Tested " + str(moves_tested)
                    self.controller.thinking(msg1, msg2, x, y)
                    if result == WIN:
                        # no need to search further, we can win!
                        self.rows[y][x] = "O"
                        print("Computer plays ", x, y)
                        self.display_board()
                        self.controller.display_move("O", x, y)
                        return
                    elif result == DRAW:
                        # our best result looks like a draw
                        best = x,y
        if best != None:
            x, y = best
            self.rows[y][x] = "O"
            print("Computer plays ", x, y, " predicts draw, moves tested:", moves_tested)
            self.display_board()
            self.controller.display_move("O", x, y)
