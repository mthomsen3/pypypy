'''


'''
import pygame
from pygame.locals import *
import client_sock_utils
import create_lobby_menu
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



def run(screen, client_socket, username):
    """
    run: Main loop of the chat application's user interface.
    Parameters: screen (pygame.Surface) - The main display surface; client_socket (socket.socket) - The client communication socket; username (str) - The user's username.
    Returns: None
    Side Effects: Draws UI components, handles user input, sends and receives chat messages, updates user list, and updates message history.
    Dependencies: pygame, messages, client_sock_utils
    """
    clock = pygame.time.Clock()
    pygame.display.set_caption('Main Menu')
    chat_messages = []
    logged_in_users = []
    input_text = ""
    game_lobbies = []
    lobby_rects = []
    x,y = 0, 0

    create_lobby_rect = pygame.Rect(50, 30, 120, 30)  # x = 260
    create_lobby_color = (96, 96, 96)
    create_lobby_hover_color = (128, 128, 128)
    create_lobby_hovered = False

    # Request user list and message history from the server
    request_user_list = messages.RequestUserListMessage()
    client_sock_utils.send_message(client_socket, request_user_list)

    request_message_history = messages.RequestMessageHistoryMessage()
    client_sock_utils.send_message(client_socket, request_message_history)
    
    lobby_list_msg = messages.RequestLobbyListMessage()
    client_sock_utils.send_message(client_socket, lobby_list_msg)
    print("Sent RequestLobbyListMessage to server")

    font = pygame.font.SysFont(None, 24)

    done = False
    while not done:
        x, y = pygame.mouse.get_pos()
        create_lobby_hovered = create_lobby_rect.collidepoint(x, y)
        


        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                clicked_lobby_index = None
                for i, lobby_rect in enumerate(lobby_rects):
                    if lobby_rect.collidepoint(x, y):
                        clicked_lobby_index = i
                        break
                if clicked_lobby_index is not None:
                    join_request_msg = messages.JoinLobbyMessage(lobby_id=game_lobbies[clicked_lobby_index]['lobby_id'], username=username, lobby_password=None)
                    client_sock_utils.send_message(client_socket, join_request_msg)
                    print(f"Joining lobby {game_lobbies[clicked_lobby_index]['lobby_id']}...")
                if create_lobby_rect.collidepoint(x, y):
                    create_lobby_req_msg = messages.CreateLobbyMenuRequestMessage(owner=username)
                    client_sock_utils.send_message(client_socket, create_lobby_req_msg)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    disconnect_message = messages.DisconnectMessage(username)
                    client_sock_utils.send_message(client_socket, disconnect_message)
                    done = True
                elif event.key == K_RETURN:
                    chat_msg = messages.ChatMessage(username=username, message=input_text)
                    client_sock_utils.send_message(client_socket, chat_msg)
                    input_text = ""
                elif event.key == K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
                # Handle other keyboard events here

        bg_color = (64, 64, 64)
        screen.fill(bg_color)

        # Draw user list
        user_list_title = font.render("Logged-in Users", True, (255, 255, 255))
        screen.blit(user_list_title, (20, 100))
        for i, username in enumerate(logged_in_users):
            user_text = font.render(f"{username}", True, (255, 255, 255))
            screen.blit(user_text, (20, 130 + i * 30))

        # Draw game rooms list
        game_room_title = font.render("Game Rooms", True, (255, 255, 255))
        screen.blit(game_room_title, (20, 380))
        #display_games_list(screen, [lobby["name"] for lobby in game_lobbies], font, (255, 255, 255), 20, 410)
        lobby_rects = display_games_list(screen, [lobby['lobby_name'] for lobby in game_lobbies], font, (255, 255, 255), 20, 410)

        # Draw the "Create Lobby" button
        create_lobby_hovered = create_lobby_rect.collidepoint(x, y)
        draw_button(screen, font, "Create Lobby", create_lobby_rect.x, create_lobby_rect.y, create_lobby_rect.width, create_lobby_rect.height, create_lobby_color, create_lobby_hover_color, create_lobby_hovered)

        # Check for incoming messages
        while not client_sock_utils.q.empty():
            message = client_sock_utils.q.get()
            #print(f"Processing message: {message}")  # Add this line
            if isinstance(message, dict) and message.get('type') == 'CHAT_MESSAGE':
                chat_messages.append(f"{message['username']}: {message['message']}")
            elif isinstance(message, dict) and message.get('type') == 'USER_LIST_UPDATE': 
                new_users = message['users']
                print(f"Received user list: {new_users}")
                for new_user in new_users:
                    if new_user not in logged_in_users:
                        logged_in_users.append(new_user)
            elif isinstance(message, dict) and message.get('type') == 'REQUEST_MESSAGE_HISTORY':  
                chat_messages = [f"{msg[0]}: {msg[1]}" for msg in message['messages']]
            elif isinstance(message, dict) and message.get('type') == 'REQUEST_USER_LIST':
                logged_in_users = message['usernames']
            elif isinstance(message, dict) and message.get('type') == 'LOBBY_LIST_UPDATE':
                game_lobbies = message['lobbies']
                print(f"Received lobby list: {game_lobbies}")
            elif isinstance(message, dict) and message.get('type') == 'LOBBY_FAILED':
                print(f"Received lobby failed message: {message['error_message']}")
                #TODO: display error message on screen
            elif isinstance(message, dict) and message.get('type') == 'CREATE_LOBBY_MENU_REQUEST_ACCEPTED':
                print("Received lobby created message")
                if message['owner'] == username:
                    # move the client to the lobby menu
                    print("Moving to lobby menu")
                    #TODO: implement lobby menu
                    create_lobby_menu.run(screen, client_socket, username)

        # Draw chat messages
        display_chat(screen, chat_messages, font, (255, 255, 255), int(screen.get_width() * 0.55), 50, max_messages=25, max_width=int(screen.get_width() * 0.4), max_height=500)

        # Draw input box and current input text
        input_box = pygame.Rect(int(screen.get_width() * 0.55), 550, int(screen.get_width() * 0.4), 40)
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
        input_text_surface = font.render(input_text, True, (255, 255, 255))
        screen.blit(input_text_surface, (input_box.x + 5, input_box.y + 5))

        pygame.display.flip()
        clock.tick(60)
        pygame.display.update()
        
def display_games_list(screen, games_list, font, color, x, y, max_games=10):
    lobby_rects = []
    
    for i, game in enumerate(games_list[-max_games:]):
        text = font.render(game, True, color)
        screen.blit(text, (x, y + i * 20))
        lobby_rect = text.get_rect(topleft=(x, y + i * 20))
        lobby_rects.append(lobby_rect)

    return lobby_rects

def display_chat(screen, chat_messages, font, color, x, y, max_messages=25, max_width=None, max_height=None):
    line_count = 0
    message_count = 0

    for message in reversed(chat_messages[-max_messages:]):
        if max_width is not None:
            wrapped_text = wrap_text(message, font, max_width)
            wrapped_text_lines = len(wrapped_text)
        else:
            wrapped_text = [message]
            wrapped_text_lines = 1

        if max_height is not None and (line_count + wrapped_text_lines) * 20 > max_height:
            break

        for idx, line in enumerate(reversed(wrapped_text)):
            text_line = font.render(line, True, color)
            screen.blit(text_line, (x, y + max_height - (line_count + idx + 1) * 20))

        line_count += wrapped_text_lines
        message_count += 1






def wrap_text(text, font, max_width):
    words = text.split(' ')
    wrapped_lines = []
    line = ''

    for word in words:
        test_line = f"{line} {word}".strip()
        text_width, _ = font.size(test_line)

        if text_width <= max_width:
            line = test_line
        else:
            wrapped_lines.append(line)
            line = word

    if line:
        wrapped_lines.append(line)

    return wrapped_lines
