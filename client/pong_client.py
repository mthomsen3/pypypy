import pygame
import sys
import client_sock_utils
from shared.messages import PlayerActionMessage


def handle_server_messages(message, game_state):
    if isinstance(message, dict) and message.get('type') == 'GAME_STATE_UPDATE':
        game_state.update(message['game_state'])

def draw_game(screen, game_state, paddle_width, paddle_height, ball_radius):
    screen.fill((0, 0, 0))

    if game_state:
        # Draw paddles
        pygame.draw.rect(screen, (255, 255, 255), (
            game_state['paddle1_x'], game_state['paddle1_y'], paddle_width, paddle_height))
        pygame.draw.rect(screen, (255, 255, 255), (
            game_state['paddle2_x'], game_state['paddle2_y'], paddle_width, paddle_height))

        # Draw ball
        pygame.draw.circle(screen, (255, 255, 255), (
            int(game_state['ball_x']), int(game_state['ball_y'])), ball_radius)

    pygame.display.flip()

def handle_user_input(client_socket, username):
    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        client_socket.send_message(PlayerActionMessage(username, "MOVE_UP"))
    if keys[pygame.K_DOWN]:
        client_socket.send_message(PlayerActionMessage(username, "MOVE_DOWN"))

def run_pong_game(client_socket, screen, username):
    game_state = {}
    paddle_width = 20
    paddle_height = 100
    ball_radius = 8
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        while not client_sock_utils.q.empty():
            message = client_sock_utils.q.get()
            handle_server_messages(message, game_state)

        handle_user_input(client_socket, username)
        draw_game(screen, game_state, paddle_width, paddle_height, ball_radius)
        clock.tick(60)
