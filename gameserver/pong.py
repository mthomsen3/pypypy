from game import Game
import random

class Pong(Game):
    
    def __init__(self, session_id, players):
        super().__init__(session_id, players)
        self.state = self.initialize_game_state()
        self.type = "pong"

    def start(self):
        pass  # Implement Pong game start logic

    def update(self, player_actions):
        # Update paddle positions based on player actions
        for player_index, (player, action) in enumerate(player_actions.items()):
            if action == "up":
                print("UP!")
                self.state[f'paddle{player_index + 1}_y'] -= 0.02
            elif action == "down":
                self.state[f'paddle{player_index + 1}_y'] += 0.02
                print("DOWN!")

        # Clamp paddle positions to the screen
        paddle_height = self.state['paddle_height']
        self.state['paddle1_y'] = max(0, min(1 - paddle_height, self.state['paddle1_y']))
        self.state['paddle2_y'] = max(0, min(1 - paddle_height, self.state['paddle2_y']))

        # Update ball position and check for collisions
        self.state['ball_x'] += self.state['ball_velocity'][0]
        self.state['ball_y'] += self.state['ball_velocity'][1]

        # Implement ball-wall collisions
        ball_diameter = self.state['ball_diameter']
        if self.state['ball_y'] <= 0 or self.state['ball_y'] + ball_diameter >= 1:
            self.state['ball_velocity'][1] = -self.state['ball_velocity'][1]

        # Implement ball-paddle collisions
        paddle1_x = self.state['paddle1_x']
        paddle2_x = self.state['paddle2_x']
        paddle_width = self.state['paddle_width']
        if (self.state['ball_x'] <= paddle1_x + paddle_width and
                self.state['paddle1_y'] <= self.state['ball_y'] <= self.state['paddle1_y'] + paddle_height) or \
                (self.state['ball_x'] + ball_diameter >= paddle2_x and
                self.state['paddle2_y'] <= self.state['ball_y'] <= self.state['paddle2_y'] + paddle_height):
            self.state['ball_velocity'][0] = -self.state['ball_velocity'][0]

        # Implement scoring logic
        winning_score = self.state['winning_score']
        ball_reset_position = [0.5, 0.5]
        ball_reset_velocity = [0.005, 0.005]
        if self.state['ball_x'] <= 0:
            self.state['scores'][1] += 1
            self.state['ball_x'], self.state['ball_y'] = ball_reset_position
            self.state['ball_velocity'] = [random.choice([-1, 1]) * ball_reset_velocity[0], random.choice([-1, 1]) * ball_reset_velocity[1]]
        elif self.state['ball_x'] + ball_diameter >= 1:
            self.state['scores'][0] += 1
            self.state['ball_x'], self.state['ball_y'] = ball_reset_position
            self.state['ball_velocity'] = [random.choice([-1, 1]) * ball_reset_velocity[0], random.choice([-1, 1]) * ball_reset_velocity[1]]

        # Implement game end conditions
        if self.state['scores'][0] >= winning_score or self.state['scores'][1] >= winning_score:
            self.state['game_over'] = True

    def end(self):
        winner = None
        if self.state['scores'][0] > self.state['scores'][1]:
            winner = self.players[0]
        elif self.state['scores'][0] < self.state['scores'][1]:
            winner = self.players[1]

        return winner

    def initialize_game_state(self):
        state = {
            'ball_x': 0.5,  # 50% of screen width
            'ball_y': 0.5,  # 50% of screen height
            'ball_velocity': [-0.005, -0.005],  # 0.5% of screen width/height per update
            'paddle1_x': 0.05,  # 5% of screen width
            'paddle1_y': 0.45,  # 45% of screen height
            'paddle2_x': 0.90,  # 90% of screen width
            'paddle2_y': 0.45,  # 45% of screen height
            'paddle_width': 0.02,  # 2% of screen width
            'paddle_height': 0.1,  # 10% of screen height
            'ball_diameter': 0.015,  # 1.5% of screen height
            'scores': [0, 0],
            'game_over': False,
            'winning_score': 10,
        }
        return state
