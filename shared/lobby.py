import uuid

class Lobby:
    def __init__(self, lobby_id, owner, lobby_name, game_type, max_players, lobby_password=None):
        if lobby_id is not None:
            self.lobby_id = lobby_id
        else:
            self.lobby_id = str(uuid.uuid4())
        self.owner = owner
        self.lobby_name = lobby_name
        self.game_type = game_type
        self.max_players = max_players
        self.lobby_password = lobby_password
        self.players = []

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
        pass
