
import pygame
import client_sock_utils
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
    y_offset = 20
    for line in info_lines:
        text_surface = font.render(line, True, FONT_COLOR)
        screen.blit(text_surface, (20, y_offset))
        y_offset += text_surface.get_height() + 5
        
        
def draw_confirmation_popup(screen, font, yes_rect, no_rect, yes_hovered, no_hovered):
    pygame.draw.rect(screen, MENU_COLOR, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, 300, 200))
    text_surface = font.render("Are you sure?", True, FONT_COLOR)
    screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 80))

    draw_button(screen, font, "Yes", yes_rect.x, yes_rect.y, yes_rect.width, yes_rect.height, MENU_COLOR, HOVERED_MENU_COLOR, yes_hovered)
    draw_button(screen, font, "No", no_rect.x, no_rect.y, no_rect.width, no_rect.height, MENU_COLOR, HOVERED_MENU_COLOR, no_hovered)



def run(screen, client_socket, username, new_lobby):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    input_font = pygame.font.SysFont(None, 20)

    lobby_name_input = pygame.Rect(140, 20, 200, 30)
    game_type_input = pygame.Rect(140, 60, 200, 30)
    max_players_input = pygame.Rect(140, 100, 200, 30)

    lobby_name = new_lobby.lobby_name
    game_type = new_lobby.game_type
    max_players = str(new_lobby.max_players)

    edit_fields = (username == new_lobby.owner)

    done = False
    active_input = None
    show_confirmation_popup = False

    while not done:
        # Get mouse position
        x, y = pygame.mouse.get_pos()
        
        display_lobby_info(screen, font, new_lobby)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                show_confirmation_popup = True
            if event.type == MOUSEBUTTONDOWN and edit_fields:
                if lobby_name_input.collidepoint(event.pos):
                    active_input = 'lobby_name'
                elif game_type_input.collidepoint(event.pos):
                    active_input = 'game_type'
                elif max_players_input.collidepoint(event.pos):
                    active_input = 'max_players'
                else:
                    active_input = None
            if event.type == KEYDOWN and active_input is not None:
                if event.key == K_RETURN:
                    update_msg = messages.LobbyUpdateMessage(lobby_id=new_lobby.lobby_id, lobby_name=lobby_name, game_type=game_type, max_players=int(max_players))
                    client_sock_utils.send_message(client_socket, update_msg)
                    active_input = None
                elif event.key == K_BACKSPACE:
                    if active_input == 'lobby_name':
                        lobby_name = lobby_name[:-1]
                    elif active_input == 'game_type':
                        game_type = game_type[:-1]
                    elif active_input == 'max_players':
                        max_players = max_players[:-1]
                else:
                    if active_input == 'lobby_name':
                        lobby_name += event.unicode
                    elif active_input == 'game_type':
                        game_type += event.unicode
                    elif active_input == 'max_players':
                        max_players += event.unicode                  
    
        screen.fill(BG_COLOR)

        # Draw editable fields
        if edit_fields:
            pygame.draw.rect(screen, SELECTED_MENU_COLOR, lobby_name_input, 1)
            pygame.draw.rect(screen, SELECTED_MENU_COLOR, game_type_input, 1)
            pygame.draw.rect(screen, SELECTED_MENU_COLOR, max_players_input, 1)

            lobby_name_surface = input_font.render(lobby_name, True, FONT_COLOR)
            game_type_surface = input_font.render(game_type, True, FONT_COLOR)
            max_players_surface = input_font.render(max_players, True, FONT_COLOR)

            screen.blit(lobby_name_surface, (lobby_name_input.x + 5, lobby_name_input.y + 5))
            screen.blit(game_type_surface, (game_type_input.x + 5, game_type_input.y + 5))
            screen.blit(max_players_surface, (max_players_input.x + 5, max_players_input.y + 5))

        start_game_rect = pygame.Rect(SCREEN_WIDTH // 2 - 60, 400, 120, 30)
        start_game_color = (96, 96, 96)
        start_game_hover_color = (128, 128, 128)
        start_game_hovered = start_game_rect.collidepoint(x, y)
        draw_button(screen, font, "Start Game", start_game_rect.x, start_game_rect.y, start_game_rect.width, start_game_rect.height, start_game_color, start_game_hover_color, start_game_hovered)
        
        #new_lobby = Lobby(lobby_id = message['lobby_id'], owner = message['owner'], lobby_name = message['lobby_name'], game_type = message['game_type'], max_players = message['max_players'], lobby_password = message['lobby_password'])
        # Check for incoming messages
        while not client_sock_utils.q.empty():
            message = client_sock_utils.q.get()
            if isinstance(message, dict) and message.get('type') == 'LOBBY_UPDATE' and message.get('lobby_id') == new_lobby.lobby_id:
                new_lobby.owner = message.get('owner')
                new_lobby.players = message.get('players')
                new_lobby.groups = message.get('groups')
                new_lobby.lobby_name = message.get('lobby_name')
                new_lobby.game_type = message.get('game_type')
                new_lobby.max_players = message.get('max_players')
                new_lobby.lobby_password = message.get('lobby_password')
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
                            if username == new_lobby.owner:
                                # Send message to close the lobby
                                close_msg = messages.LobbyClosedMessage(owner=username, lobby_id=new_lobby.lobby_id)
                                client_sock_utils.send_message(client_socket, close_msg)
                            else:
                                # Send message to remove the player from the lobby
                                leave_msg = messages.LeaveLobbyMessage(lobby_id=new_lobby.lobby_id, username=username)
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