import uuid
import random

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
        self.groups = []
        
    def get_id(self):
        return self.lobby_id

    def get_name(self):
        return self.lobby_name
    
    def get_owner(self):
        return self.owner
    
    def get_lobby_password(self):
        return self.lobby_password

    def add_player(self, player):
        if player not in self.players:
            self.players.append(player)
            self.sort_players_into_groups()
        else:
            print(f"Player {player} is already in the lobby.")

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
            self.sort_players_into_groups()
        else:
            print(f"Player {player} is not in the lobby.")

    def is_full(self):
        return len(self.players) >= self.max_players

    def start_game(self):
        pass
    
    def change_game_type(self, game_type):
        self.game_type = game_type
        self.sort_players_into_groups()

    def sort_players_into_groups(self):
        if self.game_type in ["Chess", "Checkers", "Battleship"]:
            self.groups = self.pair_players_and_spectators()
        elif self.game_type == "Pong":
            self.groups = self.create_two_teams()
        elif self.game_type in ["Free-for-all", "Poker"]:
            self.groups = self.create_individual_teams()
        elif self.game_type == "4s":
            self.groups = self.create_teams_of_n(4)
        else:
            raise ValueError(f"Invalid game type{self.game_type}")

    def pair_players_and_spectators(self):
        players = list(self.players)
        random.shuffle(players)

        if len(players) >= 2:
            p1, p2 = players[:2]
            spectators = players[2:]
        else:
            p1 = players[0] if players else None
            p2 = None
            spectators = []

        return [(p1, p2, spectators)]

    def create_two_teams(self):
        players = list(self.players)
        random.shuffle(players)

        mid = len(players) // 2
        team1 = players[:mid]
        team2 = players[mid:]

        return [team1, team2]

    def create_individual_teams(self):
        return [[player] for player in self.players]

    def create_teams_of_n(self, n):
        players = list(self.players)
        random.shuffle(players)
        return [players[i:i + n] for i in range(0, len(players), n)]


    def to_dict(self):
        return {
            'lobby_id': self.lobby_id,
            'owner': self.owner,
            'lobby_name': self.lobby_name,
            'game_type': self.game_type,
            'max_players': self.max_players,
            'lobby_password': self.lobby_password,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            lobby_id=data['lobby_id'],
            owner=data['owner'],
            lobby_name=data['lobby_name'],
            game_type=data['game_type'],
            max_players=data['max_players'],
            lobby_password=data['lobby_password'],
        )