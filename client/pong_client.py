import pygame
import sys
import client_sock_utils
from shared.messages import PlayerActionMessage

def handle_server_messages(message, game_state):
    if isinstance(message, dict) and message.get('type') == 'GAME_STATE_UPDATE':
        game_state.clear()
        game_state.update(message['game_state'])


def draw_game(screen, game_state):
    screen_width, screen_height = screen.get_size()
    screen.fill((0, 0, 0))

    if game_state:
        # Calculate pixel positions and sizes
        paddle1_x = int(game_state['paddle1_x'] * screen_width)
        paddle1_y = int(game_state['paddle1_y'] * screen_height)
        paddle2_x = int(game_state['paddle2_x'] * screen_width)
        paddle2_y = int(game_state['paddle2_y'] * screen_height)
        paddle_width = int(game_state['paddle_width'] * screen_width)
        paddle_height = int(game_state['paddle_height'] * screen_height)
        ball_x = int(game_state['ball_x'] * screen_width)
        ball_y = int(game_state['ball_y'] * screen_height)
        ball_radius = int(game_state['ball_diameter'] * screen_height / 2)

        # Draw paddles
        pygame.draw.rect(screen, (255, 255, 255), (paddle1_x, paddle1_y, paddle_width, paddle_height))
        pygame.draw.rect(screen, (255, 255, 255), (paddle2_x, paddle2_y, paddle_width, paddle_height))

        # Draw ball
        pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), ball_radius)

    pygame.display.flip()

def handle_user_input(client_socket, session_id, username):
    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        client_sock_utils.send_message(client_socket, PlayerActionMessage(session_id, username, "up"))
    if keys[pygame.K_DOWN]:
        client_sock_utils.send_message(client_socket, PlayerActionMessage(session_id, username, "down"))


def run_pong_game(client_socket, screen, session_id, username):
    game_state = {}
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        while not client_sock_utils.q.empty():
            message = client_sock_utils.q.get()
            handle_server_messages(message, game_state)

        handle_user_input(client_socket, session_id, username)
        draw_game(screen, game_state)
        clock.tick(60)
