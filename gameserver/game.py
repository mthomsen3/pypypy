from queue import Queue

class Game:
    def __init__(self, session_id, players):
        self.session_id = session_id
        self.players = players
        self.game_type = None
        self.state = None
        self.action_queue = Queue()

    def start(self):
        raise NotImplementedError
    
    def add_player_action(self, player, action):
        self.action_queue.put((player, action))
        
    def get_next_action(self):
        return self.action_queue.get()

    def update(self):
        raise NotImplementedError

    def end(self):
        raise NotImplementedError

    def get_state(self):
        return self.state
