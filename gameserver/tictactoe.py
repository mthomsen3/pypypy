from game import Game

class TicTacToe(Game):
    def __init__(self, session_id, players):
        super().__init__(session_id, players)
        self.state = self.initialize_game_state()
        self.type = "tictactoe"

    def start(self):
        pass  # Implement Tic Tac Toe game start logic

    def update(self, player_actions):
        # Process the action for the current player
        player = self.state['current_player']
        action = player_actions[player]

        if self.state['board'][action[0]][action[1]] == '':
            self.state['board'][action[0]][action[1]] = 'X' if player == 0 else 'O'

            # Check for a win or a draw
            # Update self.state['game_over'] and self.state['winner'] accordingly

            # Switch to the other player
            self.state['current_player'] = 1 - player

    def end(self):
        return self.state['winner']

    def initialize_game_state(self):
        state = {
            'board': [['' for _ in range(3)] for _ in range(3)],
            'current_player': 0,
            'game_over': False,
            'winner': None,
        }
        return state