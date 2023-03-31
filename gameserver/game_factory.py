from pong import Pong
from tictactoe import TicTacToe

class GameFactory:
    def __init__(self):
        self.game_classes = {
            'pong': Pong,
            'tictactoe': TicTacToe,
        }

    def create_game(self, game_type, game_id, players):
        if game_type in self.game_classes:
            return self.game_classes[game_type](game_id, players)
        else:
            raise ValueError(f"Invalid game type: {game_type}")
