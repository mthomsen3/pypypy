import uuid
from game_session import GameSession

class Lobby:
    def __init__(self, owner, lobby_name, game_type, max_players, lobby_password=None):
        self.lobby_id = str(uuid.uuid4())
        self.owner = owner
        self.lobby_name = lobby_name
        self.game_type = game_type
        self.max_players = max_players
        self.lobby_password = lobby_password
        self.players = []
        self.game_session = None

    def get_name(self):
        return self.lobby_name
    
    def get_owner(self):
        return self.owner

    def add_player(self, player):
        if player not in self.players:
            self.players.append(player)
        else:
            print(f"Player {player} is already in the lobby.")

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
        else:
            print(f"Player {player} is not in the lobby.")

    def is_full(self):
        return len(self.players) >= self.max_players

    def start_game(self):
        if self.game_session is None:
            # Create a game instance of the specified game type
            game_instance = self.game_type(self.players)

            # Create a GameSession instance with the game instance
            self.game_session = GameSession(self.players, game_instance)
            self.game_session.start()
        else:
            print("Game is already in progress.")
