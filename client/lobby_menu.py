
import pygame
import client_sock_utils
from pong_client import run_pong_game
from tictactoe_client import run_tictactoe_game
from pygame.locals import *
import sys
sys.path.append('../')
import shared.messages as messages

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
BG_COLOR = (200, 200, 200)
FONT_COLOR = (0, 0, 0)
MENU_COLOR = (240, 240, 240)
SELECTED_MENU_COLOR = (180, 180, 180)
HOVERED_MENU_COLOR = (220, 220, 220)
ACTIVE_INPUT_COLOR = (180, 180, 255)

# move to utils
games = ["Pong", "Chess", "Poker", "Checkers", "Tic-tac-toe"]

def draw_button(screen, font, text, x, y, width, height, color, hover_color, is_hovered):
    if is_hovered:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))

    text_surface = font.render(text, True, FONT_COLOR)
    text_width, text_height = text_surface.get_size()
    screen.blit(text_surface, (x + (width - text_width) // 2, y + (height - text_height) // 2))


def display_lobby_info(screen, font, lobby):
    info_text = f"Lobby Name: {lobby.lobby_name}\nGame Type: {lobby.game_type}\nOwner: {lobby.owner}\nPlayers: {len(lobby.players)}/{lobby.max_players}\nGroups: {lobby.groups}"
    info_lines = info_text.split('\n')
    y_offset = 100
    for line in info_lines:
        text_surface = font.render(line, True, FONT_COLOR)
        screen.blit(text_surface, (500, y_offset))
        y_offset += text_surface.get_height() + 5
        
        
def draw_confirmation_popup(screen, font, yes_rect, no_rect, yes_hovered, no_hovered):
    pygame.draw.rect(screen, MENU_COLOR, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, 300, 200))
    text_surface = font.render("Are you sure?", True, FONT_COLOR)
    screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 80))

    draw_button(screen, font, "Yes", yes_rect.x, yes_rect.y, yes_rect.width, yes_rect.height, MENU_COLOR, HOVERED_MENU_COLOR, yes_hovered)
    draw_button(screen, font, "No", no_rect.x, no_rect.y, no_rect.width, no_rect.height, MENU_COLOR, HOVERED_MENU_COLOR, no_hovered)

# move to utils
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

# move to utils
def draw_text_input(screen, font, text, x, y, width, height, label, color):
    input_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, input_rect, 2)
    label_surface = font.render(label, True, FONT_COLOR)
    screen.blit(label_surface, (x, y - 25))
    #screen.blit(label_surface, (x - (width - label_surface.get_width()) // 2, y - 25))
    text_surface = font.render(text, True, FONT_COLOR)
    screen.blit(text_surface, (x + 5, y + 5))
    

def run(screen, client_socket, username, current_lobby):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    increase_button_rect = pygame.Rect(SCREEN_WIDTH // 2 + 110, 350, 30, 30)
    decrease_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, 350, 30, 30)

    lobby_name_input = pygame.Rect(SCREEN_WIDTH // 2 - 100, 150, 200, 30)
    password_input = pygame.Rect(SCREEN_WIDTH // 2 - 100, 250, 200, 30)
    max_players_input = pygame.Rect(SCREEN_WIDTH // 2 - 100, 350, 200, 30)

    lobby_name = current_lobby.lobby_name
    password = current_lobby.lobby_password
    max_players = str(current_lobby.max_players)
    game_type = current_lobby.game_type
    selected_game = games.index(game_type)

    menu_open = False
    active_input = None

    edit_fields = (username == current_lobby.owner)

    done = False
    show_confirmation_popup = False

    while not done:
        hovered_game = -1
        # Get mouse position
        x, y = pygame.mouse.get_pos()
        
        display_lobby_info(screen, font, current_lobby)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                show_confirmation_popup = True
            if event.type == MOUSEBUTTONDOWN and edit_fields:
                if start_game_rect.collidepoint(x, y):
                    start_game_msg = messages.StartGameMessage(lobby_id=current_lobby.lobby_id)
                    client_sock_utils.send_message(client_socket, start_game_msg)
                    print("Starting game... (sending message to server)")
                elif not menu_open and SCREEN_WIDTH // 2 - 100 <= x <= SCREEN_WIDTH // 2 + 100 and 70 <= y <= 100:
                    menu_open = True
                elif menu_open and SCREEN_WIDTH // 2 - 100 <= x <= SCREEN_WIDTH // 2 + 100 and 100 <= y <= 100 + 30 * len(games):
                    selected_game = (y - 100) // 30
                    game_type = games[selected_game]
                    update_msg = messages.LobbyUpdateMessage(lobby_id=current_lobby.lobby_id, lobby_name=lobby_name, game_type=game_type, max_players=int(max_players), owner=current_lobby.owner, players=current_lobby.players, groups=current_lobby.groups, lobby_password=password)
                    client_sock_utils.send_message(client_socket, update_msg)
                    menu_open = False
                elif menu_open:
                    menu_open = False  
                if lobby_name_input.collidepoint(event.pos):
                    active_input = 'lobby_name'
                elif password_input.collidepoint(event.pos):
                    active_input = 'password'
                elif max_players_input.collidepoint(event.pos):
                    active_input = 'max_players'
                else:
                    active_input = None
                if increase_button_rect.collidepoint(x, y):
                    max_players = str(min(int(max_players) + 1, 20))
                    update_msg = messages.LobbyUpdateMessage(lobby_id=current_lobby.lobby_id, lobby_name=lobby_name, game_type=game_type, max_players=int(max_players), owner=current_lobby.owner, players=current_lobby.players, groups=current_lobby.groups, lobby_password=password)
                    client_sock_utils.send_message(client_socket, update_msg)
                elif decrease_button_rect.collidepoint(x, y):
                    max_players = str(max(1, int(max_players) - 1))
                    update_msg = messages.LobbyUpdateMessage(lobby_id=current_lobby.lobby_id, lobby_name=lobby_name, game_type=game_type, max_players=int(max_players), owner=current_lobby.owner, players=current_lobby.players, groups=current_lobby.groups, lobby_password=password)
                    client_sock_utils.send_message(client_socket, update_msg)
            elif event.type == KEYDOWN and active_input is not None:
                if event.key == K_RETURN:
                    update_msg = messages.LobbyUpdateMessage(lobby_id=current_lobby.lobby_id, lobby_name=lobby_name, game_type=game_type, max_players=int(max_players), owner=current_lobby.owner, players=current_lobby.players, groups=current_lobby.groups, lobby_password=password)
                    client_sock_utils.send_message(client_socket, update_msg)
                    active_input = None
                elif event.key == K_BACKSPACE:
                    if active_input == 'lobby_name':
                        lobby_name = lobby_name[:-1]
                    elif active_input == 'password':
                        password = password[:-1]
                    elif active_input == 'max_players':
                        max_players = max_players[:-1]
                else:
                    if active_input == 'lobby_name':
                        lobby_name += event.unicode
                    elif active_input == 'password':
                        password += event.unicode
                    elif active_input == 'max_players':
                        if event.unicode.isdigit():
                            max_players += event.unicode    
    
        screen.fill(BG_COLOR)
        

        # Draw input fields
        draw_text_input(screen, font, lobby_name, lobby_name_input.x, lobby_name_input.y, lobby_name_input.width, lobby_name_input.height, "Lobby Name:", BG_COLOR)
        draw_text_input(screen, font, password, password_input.x, password_input.y, password_input.width, password_input.height, "Lobby Password:", BG_COLOR)
        draw_text_input(screen, font, max_players, max_players_input.x, max_players_input.y, max_players_input.width, max_players_input.height, "Max Players:", BG_COLOR)
        
        #draw_text_input(screen, font, game_name, SCREEN_WIDTH // 2 - 100, 150, 200, 30, "Lobby Name:", BG_COLOR)
        #draw_text_input(screen, font, password, SCREEN_WIDTH // 2 - 100, 250, 200, 30, "Password (optional):", BG_COLOR)
        #draw_text_input(screen, font, max_players, SCREEN_WIDTH // 2 - 100, 350, 200, 30, "Max Players:", BG_COLOR)
        
        if menu_open and SCREEN_WIDTH // 2 - 100 <= x <= SCREEN_WIDTH // 2 + 100 and 100 <= y <= 100 + 30 * len(games):
            hovered_game = (y - 100) // 30
        else:
            hovered_game = -1
            
        start_game_rect = pygame.Rect(SCREEN_WIDTH // 2 - 60, 400, 120, 30)
        start_game_color = (96, 96, 96)
        start_game_hover_color = (128, 128, 128)
        start_game_hovered = start_game_rect.collidepoint(x, y)
        draw_button(screen, font, "Start Game", start_game_rect.x, start_game_rect.y, start_game_rect.width, start_game_rect.height, start_game_color, start_game_hover_color, start_game_hovered)
        
        draw_button(screen, font, "+", increase_button_rect.x, increase_button_rect.y, increase_button_rect.width, increase_button_rect.height, (96, 96, 96), (128, 128, 128), increase_button_rect.collidepoint(x, y))
        draw_button(screen, font, "-", decrease_button_rect.x, decrease_button_rect.y, decrease_button_rect.width, decrease_button_rect.height, (96, 96, 96), (128, 128, 128), decrease_button_rect.collidepoint(x, y))

        # Draw input field borders
        pygame.draw.rect(screen, FONT_COLOR, (SCREEN_WIDTH // 2 - 100, 150, 200, 30), 2)
        pygame.draw.rect(screen, FONT_COLOR, (SCREEN_WIDTH // 2 - 100, 250, 200, 30), 2)
        #pygame.draw.rect(screen, FONT_COLOR, (SCREEN_WIDTH // 2 - 100, 350, 200, 30), 2)
        
        # Draw dropdown menu
        draw_menu(screen, font, menu_open, selected_game, hovered_game)
        
        
        
        #new_lobby = Lobby(lobby_id = message['lobby_id'], owner = message['owner'], lobby_name = message['lobby_name'], game_type = message['game_type'], max_players = message['max_players'], lobby_password = message['lobby_password'])
        # Check for incoming messages
        while not client_sock_utils.q.empty():
            message = client_sock_utils.q.get()
            if isinstance(message, dict) and message.get('type') == 'LOBBY_UPDATE' and message.get('lobby_id') == current_lobby.lobby_id:
                current_lobby.players = message.get('players')
                current_lobby.groups = message.get('groups')
                current_lobby.lobby_name = message.get('lobby_name')
                current_lobby.game_type = message.get('game_type')
                current_lobby.max_players = message.get('max_players')
                current_lobby.lobby_password = message.get('lobby_password')
            elif isinstance(message, dict) and message.get('type') == 'GAME_STARTED' and message.get('session_id') == current_lobby.lobby_id:
                game_type = message.get('game_type')
                session_id = message.get('session_id')
                if game_type == 'Pong':
                    run_pong_game(client_socket, screen, session_id, username)
                if game_type == 'Tic-tac-toe':
                    run_tictactoe_game(client_socket, screen, session_id, username)
            else:
                continue

        pygame.display.flip()
        clock.tick(60)
        pygame.display.update()
        
        if show_confirmation_popup:
            yes_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2, 80, 30)
            no_rect = pygame.Rect(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT // 2, 80, 30)
            yes_hovered = yes_rect.collidepoint(x, y)
            no_hovered = no_rect.collidepoint(x, y)

            draw_confirmation_popup(screen, font, yes_rect, no_rect, yes_hovered, no_hovered)

            # Separate event loop for handling confirmation pop-up events
            popup_done = False
            while not popup_done:
                for popup_event in pygame.event.get():
                    if popup_event.type == MOUSEBUTTONDOWN:
                        if yes_rect.collidepoint(popup_event.pos):
                            if username == current_lobby.owner:
                                # Send message to close the lobby
                                close_msg = messages.LobbyClosedMessage(owner=username, lobby_id=current_lobby.lobby_id)
                                client_sock_utils.send_message(client_socket, close_msg)
                            else:
                                # Send message to remove the player from the lobby
                                leave_msg = messages.LeaveLobbyMessage(lobby_id=current_lobby.lobby_id, username=username)
                                client_sock_utils.send_message(client_socket, leave_msg)

                            done = True
                            popup_done = True
                        elif no_rect.collidepoint(popup_event.pos):
                            show_confirmation_popup = False
                            popup_done = True
                    elif popup_event.type == QUIT:
                        done = True
                        popup_done = True
                pygame.display.flip()
                clock.tick(60)
                pygame.display.update()