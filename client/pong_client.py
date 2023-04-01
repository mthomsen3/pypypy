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
    virtual_width, virtual_height = 1280, 720
    screen.fill((0, 0, 0))

    # Calculate scale factors
    scale_x = screen_width / virtual_width
    scale_y = screen_height / virtual_height

    if game_state:
        # Calculate pixel positions and sizes using virtual resolution
        paddle1_x = int(game_state['paddle1_x'] * virtual_width)
        paddle1_y = int(game_state['paddle1_y'] * virtual_height)
        paddle2_x = int(game_state['paddle2_x'] * virtual_width)
        paddle2_y = int(game_state['paddle2_y'] * virtual_height)
        paddle_width = int(game_state['paddle_width'] * virtual_width)
        paddle_height = int(game_state['paddle_height'] * virtual_height)
        ball_x = int(game_state['ball_x'] * virtual_width)
        ball_y = int(game_state['ball_y'] * virtual_height)
        ball_diameter = int(game_state['ball_diameter'] * virtual_width)

        # Scale and draw paddles
        pygame.draw.rect(screen, (255, 255, 255), (paddle1_x * scale_x, paddle1_y * scale_y, paddle_width * scale_x, paddle_height * scale_y))
        pygame.draw.rect(screen, (255, 255, 255), (paddle2_x * scale_x, paddle2_y * scale_y, paddle_width * scale_x, paddle_height * scale_y))

        # Scale and draw ball
        ball_center_x = int((ball_x + ball_diameter // 2) * scale_x)
        ball_center_y = int((ball_y + ball_diameter // 2) * scale_y)
        pygame.draw.circle(screen, (255, 255, 255), (ball_center_x, ball_center_y), int(ball_diameter // 2 * scale_x))

        # Draw scores
        draw_scores(screen, game_state)

    pygame.display.flip()


    
def draw_scores(screen, game_state):
    # Set the font and size
    font_size = 36
    font = pygame.font.Font("PressStart2P-Regular.ttf", font_size)

    # Render the scores
    score1 = font.render(str(game_state['scores'][0]), True, (255, 255, 255))
    score2 = font.render(str(game_state['scores'][1]), True, (255, 255, 255))

    # Calculate positions
    screen_width, screen_height = screen.get_size()
    score1_x = screen_width // 2 - font_size*2
    score2_x = screen_width // 2 + font_size*2 // 2
    score_y = font_size

    # Draw the scores on the screen
    screen.blit(score1, (score1_x, score_y))
    screen.blit(score2, (score2_x, score_y))

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
