'''


'''
import re
import pygame
import socket
import ssl
import main_menu
import threading
import client_sock_utils
import traceback
from queue import Empty
from pygame.locals import *
import sys
sys.path.append('../')
import shared.messages as messages


def run(screen):
    """
    run: Main function for the login screen using Pygame. Displays input fields for email and password, handles user input and validation, and submits the login request.
    Parameters:
    screen (pygame.Surface) - The Pygame window to render the login screen on.
    Returns: None
    Side Effects: Renders input fields, handles user input, and displays error messages. Calls the login_user function and the main_lobby.run function if the login is successful.
    Dependencies: pygame, re, login_user, main_lobby
    """
    clock = pygame.time.Clock()
    pygame.display.set_caption('User Login Menu')
    # create input fields for user login
    email_input = pygame.Rect(350, 200, 200, 40)
    password_input = pygame.Rect(350, 260, 200, 40)
    submit_button = pygame.Rect(350, 320, 200, 40)

    # 
    email_input_active = True
    password_input_active = False

    # create Pygame text objects for input labels
    font = pygame.font.SysFont(None, 24)
    email_label = font.render('Email:', True, (255, 255, 255))
    password_label = font.render('Password:', True, (255, 255, 255))
    submit_label = font.render('Submit', True, (255, 255, 255))


    # create Pygame text objects for error messages
    error_font = pygame.font.SysFont(None, 18)
    email_error = ''
    password_error = ''
    submit_error = ''


    # get user input from Pygame event queue
    email_input_text = ''
    password_input_text = ''
    # loop to handle user input and login
    done = False


    while not done:
        # get mouse position and button state
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    done = True
                elif email_input_active:
                    if event.key == pygame.K_RETURN:
                        email_input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        email_input_text = email_input_text[:-1]
                    elif event.key == pygame.K_TAB:
                        email_input_active = False
                        password_input_active = True
                    else:
                        if len(email_input_text) < 100:
                            email_input_text += event.unicode
                elif password_input_active:
                    if event.key == pygame.K_RETURN:
                        password_input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        password_input_text = password_input_text[:-1]
                    elif event.key == pygame.K_TAB:
                        password_input_active = False
                        email_input_active = True
                    else:
                        if len(password_input_text) < 100:
                            password_input_text += event.unicode
            elif event.type == MOUSEBUTTONDOWN:
                if email_input.collidepoint(mouse_pos):
                    email_input_active = True
                    password_input_active = False
                elif password_input.collidepoint(mouse_pos):
                    email_input_active = False
                    password_input_active = True
                else:
                    email_input_active = False
                    password_input_active = False
                if submit_button.collidepoint(event.pos):
                    # validate user input
                    email = email_input_text.strip()
                    password = password_input_text.strip()
                    if not email:
                        email_error = 'Email is required.'
                    elif not re.match(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email):
                        email_error = 'Email is invalid.'
                    else:
                        email_error = ''
                    if not password:
                        password_error = 'Password is required.'
                    else:
                        password_error = ''
                    if not email_error and not password_error:

                        # Attempt to log the user in
                        success, message, client_socket, username = login_user(email, password)
                        if success:
                            main_menu.run(screen, client_socket, username)
                            done = True
                        else:
                            submit_error = message

        # draw Pygame input fields and labels
        bg_color = (64, 64, 64)
        screen.fill(bg_color)
        pygame.draw.rect(screen, (200, 200, 200), email_input)
        pygame.draw.rect(screen, (200, 200, 200), password_input)
        pygame.draw.rect(screen, (0, 255, 0), submit_button)
        screen.blit(email_label, (250, 210))
        screen.blit(password_label, (250, 270))
        screen.blit(submit_label, (400, 335))

        # draw Pygame error messages
        email_error_text = error_font.render(email_error, True, (255, 0, 0))
        password_error_text = error_font.render(password_error, True, (255, 0, 0))
        submit_error_text = error_font.render(submit_error, True, (255, 0, 0))
        screen.blit(email_error_text, (575, 215))
        screen.blit(password_error_text, (575, 275))
        screen.blit(submit_error_text, (575, 335))

        # Draw Pygame user input fields
        max_visible_chars = (email_input.width - 10) // font.size(" ")[0]
        visible_email_input_text = email_input_text[-max_visible_chars:]
        visible_password_input_text = password_input_text[-max_visible_chars:]

        email_input_text_surface = font.render(visible_email_input_text, True, (0, 0, 0))
        password_input_text_surface = font.render(visible_password_input_text, True, (0, 0, 0))

        # Calculate the vertical position for the text surfaces
        email_input_text_y = email_input.y + (email_input.height // 2) - (email_input_text_surface.get_height() // 2)
        password_input_text_y = password_input.y + (password_input.height // 2) - (password_input_text_surface.get_height() // 2)

        # Calculate horizontal position for the text surfaces
        email_input_text_x = email_input.x + 5 - max(0, font.size(email_input_text)[0] - email_input.width + 10)
        password_input_text_x = password_input.x + 5 - max(0, font.size(password_input_text)[0] - password_input.width + 10)

        # Draw Pygame user input fields
        screen.set_clip(email_input)  # Set clipping area to the email_input rect
        screen.blit(email_input_text_surface, (email_input_text_x, email_input_text_y))
        screen.set_clip(password_input)  # Set clipping area to the password_input rect
        screen.blit(password_input_text_surface, (password_input_text_x, password_input_text_y))

        screen.set_clip(None)  # Reset the clipping area

        # update Pygame display
        pygame.display.flip()
        clock.tick(60)
        pygame.display.update()


def login_user(email, password):
    """
    login_user: Log in a user given their email and password.
    Parameters: email (str) - The user's email address; password (str) - The user's password.
    Returns: (tuple) - (success (bool) - Login success status, message (str) - Informational message, 
                        client_socket (socket.socket) - Socket object if successful, 
                        username (str) - Username if successful).
    """
    # TODO: add to central config file to avoid changing in multiple places
    ADDRESS = 'localhost'
    PORT = 9999

    # create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # wrap the socket object in an SSL context
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.load_verify_locations('server.crt')
    # TODO: REMOVE IN PRODUCTION, switch to CERT_REQUIRED and use a CA
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    client_socket = ssl_context.wrap_socket(client_socket, server_hostname=ADDRESS)

    # connect the socket object to the server address and port
    try:
        client_socket.connect((ADDRESS, PORT))

        thread = threading.Thread(target=client_sock_utils.bgThread, args=(client_socket,))
        thread.start()

        hello_msg = messages.HelloMessage(message="PyPyPy")
        client_sock_utils.send_message(client_socket, hello_msg)
        version_msg = messages.VersionMessage(version="v0.0.1")
        client_sock_utils.send_message(client_socket, version_msg)
        login_msg = messages.LoginMessage(email=email, password=password)
        client_sock_utils.send_message(client_socket, login_msg)


        # Wait for a response from the server

        while True:
            try:
                response = client_sock_utils.q.get(timeout=5)
                if response.get('type') == 'LOGIN_RESPONSE':
                    if response.get('status') == 'success':
                        return (True, "Login successful!", client_socket, response.get('username'))
                    else:
                        return (False, response.get('message', 'Unknown error'), None, None)
                else:
                    # Ignore non-login related messages
                    continue
            except Empty:
                return (False, "No response from server.", None, None)

    except Exception as e:
        print(f"Error in login_user: {e}")
        traceback.print_exc()
        return (False, 'Error connecting to server.', None, None)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    run(screen)
    pygame.quit()


