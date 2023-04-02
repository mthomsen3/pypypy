from game import Game

class TicTacToe(Game):

    def __init__(self, session_id, players):
        super().__init__(session_id, players)
        self.state = self.initialize_game_state()
        self.type = "tictactoe"

    def start(self):
        pass  # Implement Tic-tac-toe game start logic

    def update(self, player_actions):
        for player, action in player_actions.items():
            if action is None:
                continue

            row, col = action
            player_index = self.players.index(player)

            # Check if the cell is empty and the game is not over
            if self.state['board'][row][col] is None and not self.state['game_over']:
                self.state['board'][row][col] = player_index

                # Check if the current player won
                if self.check_win(player_index):
                    self.state['game_over'] = True
                    self.state['winner'] = player

                # Swap the current player
                self.state['current_player'] = self.players[1 - player_index]

    def end(self):
        return self.state['winner']

    def initialize_game_state(self):
        state = {
            'board': [[None, None, None] for _ in range(3)],
            'players': self.players,
            'current_player': self.players[0],
            'game_over': False,
            'winner': None,
        }
        return state

    def check_win(self, player_index):
        board = self.state['board']
        # Check rows, columns and diagonals
        return any([
            all(board[row][col] == player_index for col in range(3)) or
            all(board[row][col] == player_index for row in range(3))
            for row, col in ((row, row) for row in range(3))
        ]) or all(board[i][i] == player_index for i in range(3)) or all(board[i][2 - i] == player_index for i in range(3))
