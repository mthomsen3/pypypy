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
        for player, action in player_actions.items():
            player_index = self.players.index(player)
            if action is None:
                continue
            if action == "up":
                self.state[f'paddle{player_index + 1}_y'] -= 0.02
            elif action == "down":
                self.state[f'paddle{player_index + 1}_y'] += 0.02

        # Clamp paddle positions to the screen
        paddle_height = self.state['paddle_height']
        self.state['paddle1_y'] = max(0, min(1 - paddle_height, self.state['paddle1_y']))
        self.state['paddle2_y'] = max(0, min(1 - paddle_height, self.state['paddle2_y']))
        
        # Update ball position
        self.state['ball_x'] += self.state['ball_velocity'][0]
        self.state['ball_y'] += self.state['ball_velocity'][1]

        # Implement ball-wall collisions
        ball_diameter = self.state['ball_diameter']
        if self.state['ball_y'] <= 0 or self.state['ball_y'] + ball_diameter >= 1:
            self.state['ball_velocity'][1] = -self.state['ball_velocity'][1]

        # Implement ball-paddle collisions
        def calculate_ball_y_velocity(ball_center_y, paddle_y, paddle_height):
            relative_y = (ball_center_y - paddle_y) / paddle_height
            return (relative_y - 0.5) * 0.025  # Tweak this value to adjust the maximum Y velocity change
            
        def rects_intersect(rect1, rect2):
            return (rect1[0] + rect1[2] > rect2[0] and rect1[0] < rect2[0] + rect2[2] and
                    rect1[1] < rect2[1] + rect2[3] and rect1[1] + rect1[3] > rect2[1])
            
        def ball_paddle_collision_response(ball_rect, paddle_rect):
            overlap_left = paddle_rect[0] + paddle_rect[2] - ball_rect[0]
            overlap_right = ball_rect[0] + ball_rect[2] - paddle_rect[0]
            overlap_top = paddle_rect[1] + paddle_rect[3] - ball_rect[1]
            overlap_bottom = ball_rect[1] + ball_rect[3] - paddle_rect[1]

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_left:
                return 'left'
            elif min_overlap == overlap_right:
                return 'right'
            elif min_overlap == overlap_top:
                return 'top'
            else:
                return 'bottom'


        ball_rect = [self.state['ball_x'], self.state['ball_y'], ball_diameter, ball_diameter]
        paddle1_rect = [self.state['paddle1_x'], self.state['paddle1_y'], self.state['paddle_width'], paddle_height]
        paddle2_rect = [self.state['paddle2_x'], self.state['paddle2_y'], self.state['paddle_width'], paddle_height]

        # Detect if ball intersects paddle
        paddle_collision = None
        if rects_intersect(ball_rect, paddle1_rect):
            paddle_collision = 'paddle1'
        elif rects_intersect(ball_rect, paddle2_rect):
            paddle_collision = 'paddle2'
            
        if paddle_collision == 'paddle1':
            collision_side = ball_paddle_collision_response(ball_rect, paddle1_rect)
            if collision_side in ('left', 'right'):
                self.state['ball_velocity'][0] = -self.state['ball_velocity'][0]
                self.state['ball_velocity'][1] += calculate_ball_y_velocity(self.state['ball_y'] + (ball_diameter / 2), self.state['paddle1_y'], paddle_height)
            elif collision_side in ('top', 'bottom'):
                self.state['ball_velocity'][1] = -self.state['ball_velocity'][1]

        elif paddle_collision == 'paddle2':
            collision_side = ball_paddle_collision_response(ball_rect, paddle2_rect)
            if collision_side in ('left', 'right'):
                self.state['ball_velocity'][0] = -self.state['ball_velocity'][0]
                self.state['ball_velocity'][1] += calculate_ball_y_velocity(self.state['ball_y'] + (ball_diameter / 2), self.state['paddle2_y'], paddle_height)
            elif collision_side in ('top', 'bottom'):
                self.state['ball_velocity'][1] = -self.state['ball_velocity'][1]


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
            'ball_x': 640 / 1280,  # 50% of virtual screen width
            'ball_y': 360 / 720,  # 50% of virtual screen height
            'ball_velocity': [-0.005, -0.005],  # 0.5% of screen width/height per update
            'paddle1_x': 64 / 1280,  # 5% of virtual screen width
            'paddle1_y': 324 / 720,  # 45% of virtual screen height
            'paddle2_x': 1152 / 1280,  # 90% of virtual screen width
            'paddle2_y': 324 / 720,  # 45% of virtual screen height
            'paddle_width': 12.8 / 1280,  # 1% of virtual screen width
            'paddle_height': 72 / 720,  # 10% of virtual screen height
            'ball_diameter': 38.4 / 1280,  # 3% of virtual screen width
            'scores': [0, 0],
            'game_over': False,
            'winning_score': 10,
        }
        return state

