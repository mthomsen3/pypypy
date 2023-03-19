import json
import uuid

class GameSession:
    def __init__(self, players, game_instance):
        self.session_id = str(uuid.uuid4())
        self.players = players
        self.game_instance = game_instance
        self.game_state = self.game_instance.initialize_game_state()

    def update_game_state(self, player, action):
        if self.game_instance.is_valid_action(player, action):
            self.game_instance.update_game_state(player, action)
            
    async def broadcast_game_state(self):
        # Convert the game state to a JSON string
        game_state_str = json.dumps(self.game_state)

        # Send the game state to all connected players
        for player in self.players:
            websocket = player.websocket  # Assuming player objects have a reference to their websocket
            await websocket.send(game_state_str)

    def start(self):
        # Start the game session and initialize the game state
        pass
