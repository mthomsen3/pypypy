import pygame
import pygame.gfxdraw
import sys
import math
import client_sock_utils
from shared.messages import PlayerActionMessage

def handle_server_messages(message, game_state):
    if isinstance(message, dict) and message.get('type') == 'GAME_STATE_UPDATE':
        game_state.clear()
        game_state.update(message['game_state'])

def draw_game(screen, game_state, username):
    screen.fill((30, 30, 30))

    if game_state:
        draw_title(screen)
        draw_legend(screen, game_state)
        draw_board(screen, game_state)
        draw_marks(screen, game_state)
        if game_state.get('current_player') == username:  # Only show hover effect when it's the player's turn
            draw_hover_square(screen, game_state)  # Add this line


    pygame.display.flip()

def draw_title(screen):
    font_size = 48
    font = pygame.font.Font(None, font_size)
    title = font.render("Tic Tac Toe", True, (255, 255, 255))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 20))
    
def draw_hover_square(screen, game_state):
    board_padding = 100
    additional_padding = 200
    board_size = min(screen.get_width() - 2 * board_padding - additional_padding, screen.get_height() - 2 * board_padding)
    board_top_left = (board_padding + additional_padding, screen.get_height() // 2 - board_size // 2)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    cell_size = board_size // 3
    row, col = (mouse_y - board_top_left[1]) // cell_size, (mouse_x - board_top_left[0]) // cell_size

    if 0 <= row < 3 and 0 <= col < 3:
        cell_top_left = (board_top_left[0] + col * cell_size, board_top_left[1] + row * cell_size)
        filled = game_state['board'][row][col] is not None
        color = (128, 128, 128, 100) if filled else (255, 255, 255, 100)  # Gray if filled, white otherwise
        hover_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)  # Create a surface with alpha channel
        pygame.draw.rect(hover_surface, color, (0, 0, cell_size, cell_size), border_radius=5, width=0)
        screen.blit(hover_surface, cell_top_left)

def draw_legend(screen, game_state):
    font_size = 32
    font = pygame.font.Font(None, font_size)
    player1_text = f"PLAYER 1: {game_state['players'][0]}"
    player2_text = f"PLAYER 2: {game_state['players'][1]}"
    player1_label = font.render(player1_text, True, (255, 0, 0))
    player2_label = font.render(player2_text, True, (0, 0, 255))

    legend_x, legend_y = 20, 100
    screen.blit(player1_label, (legend_x, legend_y))
    screen.blit(player2_label, (legend_x, legend_y + font_size * 2))

    if game_state['winner'] is not None:
        winner_index = game_state['players'].index(game_state['winner'])
        winner_y = legend_y + font_size * (2 * winner_index + 1)

        # Draw a gold star next to the winner's name
        star_radius = font_size // 2
        points = 5
        inner_radius = star_radius // 2
        angle_diff = 2 * math.pi / points
        star_points = []

        for i in range(2 * points):
            angle = i * angle_diff
            r = star_radius if i % 2 == 0 else inner_radius
            x = player1_label.get_width() + 1.5 * font_size + r * math.cos(angle)
            y = winner_y - font_size // 2 + r * math.sin(angle)
            star_points.append((int(x), int(y)))

        pygame.draw.polygon(screen, (255, 215, 0), star_points)
        
    if game_state['current_player'] == game_state['players'][0] and game_state['winner'] is None:
        pygame.draw.circle(screen, (255, 0, 0), (player1_label.get_width() + 50, legend_y + font_size // 2), 10)
    elif game_state['current_player'] == game_state['players'][1] and game_state['winner'] is None:
        pygame.draw.circle(screen, (0, 0, 255), (player2_label.get_width() + 50, legend_y + 2 * font_size + font_size // 2), 10)

def draw_board(screen, game_state):
    board_padding = 100
    additional_padding = 200 
    board_size = min(screen.get_width() - 2 * board_padding - additional_padding, screen.get_height() - 2 * board_padding)
    board_top_left = (board_padding + additional_padding, screen.get_height() // 2 - board_size // 2) 

    # Draw the grid lines
    for i in range(1, 3):
        pygame.draw.line(screen, (255, 255, 255), (board_top_left[0] + i * board_size // 3, board_top_left[1]), (board_top_left[0] + i * board_size // 3, board_top_left[1] + board_size), 5)
        pygame.draw.line(screen, (255, 255, 255), (board_top_left[0], board_top_left[1] + i * board_size // 3), (board_top_left[0] + board_size, board_top_left[1] + i * board_size // 3), 5)

def draw_marks(screen, game_state):
    for row in range(3):
        for col in range(3):
            if game_state['board'][row][col] is not None:
                draw_mark(screen, game_state['board'][row][col], row, col)

def draw_mark(screen, player_index, row, col):
    board_padding = 100
    additional_padding = 200
    board_size = min(screen.get_width() - 2 * board_padding - additional_padding, screen.get_height() - 2 * board_padding)
    board_top_left = (board_padding + additional_padding, screen.get_height() // 2 - board_size // 2) 
    cell_size = board_size // 3
    x, y = (col + 0.5) * cell_size + board_top_left[0], (row + 0.5) * cell_size + board_top_left[1]
    radius = cell_size // 3

    if player_index == 0:  # Draw 'X'
        pygame.draw.line(screen, (255, 0, 0), (x - radius, y - radius), (x + radius, y + radius), 5)
        pygame.draw.line(screen, (255, 0, 0), (x - radius, y + radius), (x + radius, y - radius), 5)
    else:  # Draw 'O'
        pygame.draw.circle(screen, (0, 0, 255), (int(x), int(y)), radius, 5)

def run_tictactoe_game(client_socket, screen, session_id, username):
    game_state = {}
    clock = pygame.time.Clock()
    additional_padding = 200  # Add this line
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP and game_state.get('current_player') == username:
                board_padding = 100
                board_size = min(screen.get_width() - 2 * board_padding - additional_padding, screen.get_height() - 2 * board_padding)
                board_top_left = (board_padding + additional_padding, screen.get_height() // 2 - board_size // 2)  # Update this line

                cell_size = board_size // 3
                row, col = (event.pos[1] - board_top_left[1]) // cell_size, (event.pos[0] - board_top_left[0]) // cell_size

                if 0 <= row < 3 and 0 <= col < 3:
                    client_sock_utils.send_message(client_socket, PlayerActionMessage(session_id, username, action=(row, col)))

        while not client_sock_utils.q.empty():
            message = client_sock_utils.q.get()
            handle_server_messages(message, game_state)

        draw_game(screen, game_state, username)
        clock.tick(60)

