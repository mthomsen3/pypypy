import pygame
import client_sock_utils
import lobby_menu
from pygame.locals import *
import sys
sys.path.append('../')
import shared.messages as messages
from shared.lobby import Lobby

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
BG_COLOR = (200, 200, 200)
FONT_COLOR = (0, 0, 0)
MENU_COLOR = (240, 240, 240)
SELECTED_MENU_COLOR = (180, 180, 180)
HOVERED_MENU_COLOR = (220, 220, 220)

games = ["Pong", "Chess", "Poker", "Checkers"]


def draw_button(screen, font, text, x, y, width, height, color, hover_color, is_hovered):
    if is_hovered:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))

    text_surface = font.render(text, True, FONT_COLOR)
    text_width, text_height = text_surface.get_size()
    screen.blit(text_surface, (x + (width - text_width) // 2, y + (height - text_height) // 2))


def draw_menu(screen, font, is_open, selected_game, hovered_game):
    current_selection = games[selected_game]

    if is_open:
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 100, 200, 30 * len(games))
        pygame.draw.rect(screen, MENU_COLOR, menu_rect)

        for index, game in enumerate(games):
            text_surface = font.render(game, True, FONT_COLOR)
            text_height = text_surface.get_height()
            vertical_offset = (30 - text_height) // 2
            
            if index == hovered_game:
                pygame.draw.rect(screen, HOVERED_MENU_COLOR, pygame.Rect(menu_rect.x, menu_rect.y + 30 * index, menu_rect.width, 30))
            if index == selected_game:
                pygame.draw.rect(screen, SELECTED_MENU_COLOR, pygame.Rect(menu_rect.x, menu_rect.y + 30 * index, menu_rect.width, 30))
            screen.blit(text_surface, (menu_rect.x + 10, menu_rect.y + 30 * index + vertical_offset))

    default_text = f"Choose a Game: {current_selection}"
    text_surface = font.render(default_text, True, FONT_COLOR)
    text_height = text_surface.get_height()
    vertical_offset = (30 - text_height) // 2
    screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, 70 + vertical_offset))

def draw_text_input(screen, font, text, x, y, width, height, label, color):
    input_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, input_rect, 2)
    label_surface = font.render(label, True, FONT_COLOR)
    screen.blit(label_surface, (x - (width - label_surface.get_width()) // 2, y - 25))
    text_surface = font.render(text, True, FONT_COLOR)
    screen.blit(text_surface, (x + 5, y + 5))

def run(screen, client_socket, username):
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 24)

    game_name = ""
    password = ""
    max_players = "4"
    selected_game = 0

    menu_open = False
    active_input = None

    done = False
    while not done:
        hovered_game = -1
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if create_lobby_rect.collidepoint(x, y):
                    create_lobby_msg = messages.CreateLobbyRequestMessage(owner=username, game_type=games[selected_game], lobby_name=game_name, lobby_password=password, max_players=int(max_players))
                    client_sock_utils.send_message(client_socket, create_lobby_msg)
                elif not menu_open and SCREEN_WIDTH // 2 - 100 <= x <= SCREEN_WIDTH // 2 + 100 and 70 <= y <= 100:
                    menu_open = True
                elif menu_open and SCREEN_WIDTH // 2 - 100 <= x <= SCREEN_WIDTH // 2 + 100 and 100 <= y <= 100 + 30 * len(games):
                    selected_game = (y - 100) // 30
                    menu_open = False
                elif menu_open:
                    menu_open = False
                if 220 <= x <= 420 and 150 <= y <= 180:
                    active_input = "game_name"
                elif 220 <= x <= 420 and 250 <= y <= 280:
                    active_input = "password"
                elif 220 <= x <= 420 and 350 <= y <= 380:
                    active_input = "max_players"
                else:
                    active_input = None

            elif event.type == KEYDOWN:
                if active_input is not None:
                    if event.key == K_BACKSPACE:
                        if active_input == "game_name":
                            game_name = game_name[:-1]
                        elif active_input == "password":
                            password = password[:-1]
                        elif active_input == "max_players":
                            max_players = max_players[:-1]
                    else:
                        if active_input == "game_name":
                            game_name += event.unicode
                        elif active_input == "password":
                            password += event.unicode
                        elif active_input == "max_players":
                            if event.unicode.isdigit():
                                max_players += event.unicode


        screen.fill(BG_COLOR)

        draw_text_input(screen, font, game_name, SCREEN_WIDTH // 2 - 100, 150, 200, 30, "Lobby Name:", BG_COLOR)
        draw_text_input(screen, font, password, SCREEN_WIDTH // 2 - 100, 250, 200, 30, "Password (optional):", BG_COLOR)
        draw_text_input(screen, font, max_players, SCREEN_WIDTH // 2 - 100, 350, 200, 30, "Max Players:", BG_COLOR)

        x, y = pygame.mouse.get_pos()
        if menu_open and SCREEN_WIDTH // 2 - 100 <= x <= SCREEN_WIDTH // 2 + 100 and 100 <= y <= 100 + 30 * len(games):
            hovered_game = (y - 100) // 30
        else:
            hovered_game = -1


        create_lobby_rect = pygame.Rect(SCREEN_WIDTH // 2 - 60, 400, 120, 30)
        create_lobby_color = (96, 96, 96)
        create_lobby_hover_color = (128, 128, 128)
        create_lobby_hovered = create_lobby_rect.collidepoint(x, y)
        draw_button(screen, font, "Create Lobby", create_lobby_rect.x, create_lobby_rect.y, create_lobby_rect.width, create_lobby_rect.height, create_lobby_color, create_lobby_hover_color, create_lobby_hovered)
        
        # Draw input field borders
        pygame.draw.rect(screen, FONT_COLOR, (SCREEN_WIDTH // 2 - 100, 150, 200, 30), 2)
        pygame.draw.rect(screen, FONT_COLOR, (SCREEN_WIDTH // 2 - 100, 250, 200, 30), 2)
        pygame.draw.rect(screen, FONT_COLOR, (SCREEN_WIDTH // 2 - 100, 350, 200, 30), 2)

        draw_menu(screen, font, menu_open, selected_game, hovered_game)

        # Check for incoming messages
        while not client_sock_utils.q.empty():
            message = client_sock_utils.q.get()
            if isinstance(message, dict) and message.get('type') == 'LOBBY_FAILED':
                print(f"Received lobby failed message: {message['error_message']}")
                #TODO: display error message on screen
            elif isinstance(message, dict) and message.get('type') == 'LOBBY_CREATED':
                print("Received lobby created message")
                if message['owner'] == username:
                    screen.blit(font.render("Lobby created!", True, FONT_COLOR), (10, 10))
                    # create a lobby menu object
                    # the server also has its own Lobby object, updates are transmitted to the client... may need to change this
                    new_lobby = Lobby(lobby_id = message['lobby_id'], owner = message['owner'], lobby_name = message['lobby_name'], game_type = message['game_type'], max_players = message['max_players'], lobby_password = message['lobby_password'])
                    for player in message['players']:
                        new_lobby.add_player(player)
                    print("Moving to lobby menu")
                    #TODO: implement lobby menu
                    # move the client to the lobby menu, passing in the lobby object
                    lobby_menu.run(screen, client_socket, username, new_lobby)

        pygame.display.flip()
        clock.tick(60)
        pygame.display.update()

