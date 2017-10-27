import random
import copy

# CONSTANTS
CELLS_X = 3
CELLS_Y = 3
EMPTY = ' '
PLAYER_X = 'X'
PLAYER_O = 'O'
CENTER = [1, 1]

# DIFFICULTY -> MOVE FORECAST
diff_dict = {
    1: 2,
    2: 3,
    3: 6,
    4: 9
}


# Board Object, to attribute all methods such as check and move to the board itself.
class Board:
    def __init__(self):
        board = []
        rows = []
        for x in range(CELLS_X):
            for y in range(CELLS_Y):
                rows.append([x, y, EMPTY])
            board.append(rows)
            rows = []
        self.layout = board
        self.player_X_moves = []
        self.player_O_moves = []
        self.AIChoice = ""
        self.current_player = random.choice((PLAYER_X, PLAYER_O))

    # Outputs the board every game move by printing rows individually.
    def output(self):
        for x in self.layout:
            strlist = [str(y[2]) for y in x]
            print("  " + " | ".join(strlist))
            if self.layout[2] != x:
                print("----+---+----")
        print("\n" * 2)

    # Performs the move of a player taking row and column coordinates.
    # Adds the move to a list of moves for each player.
    def move(self, destination):
        x = destination[0]
        y = destination[1]
        if self.current_player == PLAYER_X:
            self.layout[x][y][2] = PLAYER_X
            self.player_X_moves.append([x, y])
        else:
            self.layout[x][y][2] = PLAYER_O
            self.player_O_moves.append([x, y])
        return True

    # checks columns, rows and diagonal triplets to check if the player parameter has one.
    # noinspection PyTypeChecker
    def check(self, player):
        b = self.layout
        win_conditions = [
            # columns
            [b[0][0][2], b[0][1][2], b[0][2][2]],
            [b[1][0][2], b[1][1][2], b[1][2][2]],
            [b[2][0][2], b[2][1][2], b[2][2][2]],

            # rows
            [b[0][0][2], b[1][0][2], b[2][0][2]],
            [b[0][1][2], b[1][1][2], b[2][1][2]],
            [b[0][2][2], b[1][2][2], b[2][2][2]],

            # diagonal
            [b[0][0][2], b[1][1][2], b[2][2][2]],
            [b[2][0][2], b[1][1][2], b[0][2][2]]]

        if list(player * 3) in win_conditions:
            return player
        return False

    # Allows entry of row and column with data validation.
    def show_options(self, move):
        print("It is", str(move) + "'s move.")
        row, column = "TEMP", "TEMP"
        valid = False
        while not valid:
            while row.isalpha() or (row not in ['1', '2', '3']):
                row = input("Choose row 1, 2 or 3: ")
            while column.isalpha() or (column not in ['1', '2', '3']):
                column = input("Choose column 1, 2 or 3: ")
            if self.layout[int(row) - 1][int(column) - 1][2] == ' ':
                print("\n" * 2)
                return int(row), int(column)
            else:
                print("Invalid move. Not an empty space.")
                row, column = "a", "7"
        print("\n" * 2)

    # Static Method that calculates a triplets heuristic value.
    # +10 for two cells and one empty for AI
    # +1 for one cell and two empty for AI
    # -10 for two cells and one empty for Human
    # -1 for one cell and two empty for Human

    @staticmethod
    def evaluate(triplet):
        heuristic = 0
        position = copy.deepcopy(triplet)
        if position.count(PLAYER_O) == 1:
            if position.count(EMPTY) == 2:
                heuristic += 1
        elif position.count(EMPTY) == 1:
            if position.count(PLAYER_O) == 2:
                heuristic += 10
        if position.count(PLAYER_X) == 1:
            if position.count(EMPTY) == 2:
                heuristic -= 1
        elif position.count(EMPTY) == 1:
            if position.count(PLAYER_X) == 2:
                heuristic -= 10
        return heuristic

    # Returns the heuristic value of the game board by calling the function
    # above for each row, column and diagonal to develop a complete heuristic
    # value for the board.

    def heuristic(self):
        heuristic = 0
        for x in range(3):
            current_row = [j[2] for j in self.layout[x]]
            current_column = [i[x][2] for i in self.layout]
            heuristic += self.evaluate(current_row)
            heuristic += self.evaluate(current_column)
        diagonal1 = [self.layout[0][0][2], self.layout[1][1][2], self.layout[2][2][2]]
        diagonal2 = [self.layout[2][0][2], self.layout[1][1][2], self.layout[0][2][2]]
        heuristic += self.evaluate(diagonal1)
        heuristic += self.evaluate(diagonal2)
        return heuristic

    # Creates a list of all empty cells in the game state.
    def generate_new_moves(self):
        move_list = []
        for x in self.layout:
            for y in x:
                if y[2] == " ":
                    move_list.append([y[0], y[1]])
        return move_list


# Outputs win if win parameter is true. Outputs Draw if sum of the lengths of
# player's move lists = 9. Else returns False to continue the game.
def win_check(win, board):
    if win:
        board.output()
        print(win, "is the winner...")
        return win
    elif (len(board.player_X_moves) + len(board.player_O_moves)) == 9:
        board.output()
        print("Draw. Game Over")
        win = "DRAW"
        return win
    return False


# Performs the minimax algorithm for a specific game_state to a specific depth.
# Basics of minimax:
#
# 1. Generates a list of possible moves for the current player (Starting with the computer's move).
# 2. Loops through the list, creating a temporary game_state for each move, and performing that
#    move on each temporary board.
# 3. For each temporary board with its respective move performed upon it, it calls itself (minimax)
#    again (recursively). The current player is switched to the other player.
# 4. A new list of moves is created for each temporary game_state and the cycle continues until a
#    leaf node is reached.
# 5. When the function reaches a maximum depth i.e. 6 moves, or the current game state on the stack
#    is a winning/ending game state, the function calculates the heuristic value of the board; it
#    gives the board a score depending on its advantages and disadvantages for the AI. A board in
#    a winning position yields a higher score for the AI and a board in a losing position has a lower
#    score.
# 6. The heuristic is returned by the function thereby ending the recursion for that stack. The final
#    depth of recursion, for example, may have 5 possible game states. The score for each of these game
#    states is appended to a list. If the current player at that level of recursion is the AI, then the
#    maximum of these scores is calculated and returned, as the goal for the AI is to maximise its own
#    score. If the current player is the Human, then the minimum is returned, as the Human wishes to
#    minimise the score.
# 7. The max/min score is passed up the tree, till it reaches the bottom of the stack (the initial function
#    call.) The final list of scores for each possible initial AI move is maxed, as it is obviously the AI's
#    turn. Now that each move has been evaluated to a certain depth, (AI has seen *depth* moves into the
#    future.), the AI can play the move that yields the max score.
# 8. The function is called again next time it's the AI's turn.
#
# Difficulty:
# Easy - Performs minimax for a depth of 2.
# Medium - Performs minimax for a depth of 3.
# Hard - Performs minimax for a start depth of 6. Next turn it is decreased to 3. Next, its decreased to 1.
# Impossible - Performs minimax for a depth of 9 (All possible game states evaluated).
#

def minimax(game_state, depth, real_depth):
    result_a = game_state.check(PLAYER_X)
    result_b = game_state.check(PLAYER_O)
    if result_a == PLAYER_X:
        return 100 - real_depth
    elif result_b == PLAYER_O:
        return real_depth - 100
    else:
        if (len(game_state.player_X_moves) + len(game_state.player_O_moves)) == 9 or depth == 0:
            heuristic = game_state.heuristic()
            return heuristic

    scores = []
    moves = []
    real_depth += 1
    move_list = game_state.generate_new_moves()
    for move in move_list:
        possible_game_obj = copy.deepcopy(game_state)
        if possible_game_obj.current_player == PLAYER_X:
            possible_game_obj.current_player = PLAYER_O
        else:
            possible_game_obj.current_player = PLAYER_X
        possible_game_obj.move(move)
        scores.append(minimax(possible_game_obj, depth - 1, real_depth))
        moves.append(move)
    if game_state.current_player == PLAYER_O:
        max_score_index = scores.index(max(scores))
        game_state.AIChoice = moves[max_score_index]
        return scores[max_score_index]
    else:
        min_score_index = scores.index(min(scores))
        game_state.AIChoice = moves[min_score_index]
        return scores[min_score_index]


# Alternates the current_player, checking a win for the current player at the end of each iteration
def two_player_game():
    board = Board()
    win = False

    while win is False:
        board.output()
        row_choice, column_choice = board.show_options(board.current_player)
        board.move((row_choice - 1, column_choice - 1))
        if (len(board.player_X_moves) > 2) or len(board.player_O_moves) > 2:
            win = board.check(board.current_player)

        if win_check(win, board):
            break

        if board.current_player is PLAYER_X:
            board.current_player = PLAYER_O
        else:
            board.current_player = PLAYER_X


# Alternates current_player, and calls minimax for each AI turn, at a user-defined difficulty.
def comp_game(difficulty, first):
    board = Board()
    board.current_player = PLAYER_X
    move_forecast = diff_dict[difficulty]

    if first == "N":
        board.current_player = PLAYER_O
        board.AIChoice = random.choice([[0, 0], [0, 2], [2, 0], [2, 2]])
        board.move(board.AIChoice)

    win = False
    while win is False:
        board.current_player = PLAYER_X
        board.output()
        row_choice, column_choice = board.show_options(board.current_player)
        board.move((row_choice - 1, column_choice - 1))
        win = board.check(PLAYER_X)
        win = win_check(win, board)
        if win:
            break
        minimax(board, move_forecast, 0)
        board.current_player = PLAYER_O
        board.move(board.AIChoice)
        win = board.check(PLAYER_O)
        win = win_check(win, board)
        if difficulty not in ['hard', 'OP']:
            if move_forecast > 3:
                move_forecast -= 3


# Calls the two player/comp function based on user choices. Passes user-defined arguments to
# comp game function.
def play_game():
    print("Choose Game Mode. Enter 1 or 2." + ("\n" * 2))
    print("1. Play against friend.")
    print("2. Play against computer.")
    print('')
    choice = "a"
    while choice.isalpha() or (choice not in ['1', '2']):
        choice = input("Game mode: ")
    if int(choice) == 1:
        two_player_game()
    elif int(choice) == 2:
        print("\n" * 2)
        print("Choose Difficulty. Enter 1, 2, 3 or 4." + ("\n" * 2))
        print("1. Easy - AI might even try to lose.")
        print("2. Medium - AI will block your three in a row, but it is easy to fork it.")
        print("3. Hard - Play corner first move for best chances. ")
        print("4. Impossible - You can't beat it - game always ends in either draw or loss for Human.")
        print('')
        difficulty = "a"
        while difficulty.isalpha() or (difficulty not in ['1', '2', '3', '4']):
            difficulty = input("Difficulty: ")
        difficulty = int(difficulty)
        print('')
        first = "a"
        while first not in ['Y', 'N']:
            first = input("Do you wish to go first? Enter Y/N: ").upper()
            print('')
        comp_game(difficulty, first)

    print("\n" * 2)
    print("Do you wish to play again? Enter Y/N...")
    continue_bool = 2
    while continue_bool not in ['Y', 'N']:
        continue_bool = input("Play again: ").upper()
    if continue_bool == 'Y':
        play_game()
    else:
        print("Thanks for playing!")
        print("\n")
        print("-" * 15)
        print("By Rohit Prasad")


play_game()

'''
trace = open("trace_tables.csv", "a")
trace.write("\n Iteration, Row Choice, Column Choice, Current Player, Player X Moves, Player O Moves, Win \n")
count = 0

counts = str(count)
rowchoice = str(rowchoice)
columnchoice = str(columnchoice)
winS = str(win)
playerX = "\"" + str(board.player_X_moves) + "\""
playerO = "\"" + str(board.player_O_moves) + "\""
current = board.current_player

trace.write("%s,%s,%s,%s,%s,%s,%s \n" % (counts, rowchoice, columnchoice, current, playerX, playerO, winS))
'''
