'''


'''
import re
import pygame
import socket
import ssl
import bcrypt
import threading
import client_sock_utils
from pygame.locals import *
import sys
sys.path.append('../')
import shared.messages as messages


def run(screen):
    """
    run: Handles the user registration process in the Pygame window.
    Parameters: screen (pygame.Surface) - The main display surface.
    Returns: None
    Side Effects: Displays user registration form, validates input, and attempts to register the user.
    Dependencies: pygame, re (for email validation)
    """
    clock = pygame.time.Clock()
    pygame.display.set_caption('User Registration Menu')
    # create input fields for user registration
    name_input = pygame.Rect(350, 200, 200, 40)
    email_input = pygame.Rect(350, 260, 200, 40)
    password_input = pygame.Rect(350, 320, 200, 40)
    submit_button = pygame.Rect(350, 380, 200, 40)

    # 
    name_input_active = True
    email_input_active = False
    password_input_active = False

    # create Pygame text objects for input labels
    font = pygame.font.SysFont(None, 24)
    name_label = font.render('Name:', True, (255, 255, 255))
    email_label = font.render('Email:', True, (255, 255, 255))
    password_label = font.render('Password:', True, (255, 255, 255))
    submit_label = font.render('Submit', True, (255, 255, 255))


    # create Pygame text objects for error messages
    error_font = pygame.font.SysFont(None, 18)
    name_error = ''
    email_error = ''
    password_error = ''
    submit_error = ''


    # get user input from Pygame event queue
    name_input_text = ''
    email_input_text = ''
    password_input_text = ''
    # loop to handle user input and registration
    done = False


    while not done:
        # get mouse position and button state
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    done = True
                elif name_input_active:
                    if event.key == pygame.K_RETURN:
                        name_input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name_input_text = name_input_text[:-1]
                    else:
                        if len(name_input_text) < 100:
                            name_input_text += event.unicode
                elif email_input_active:
                    if event.key == pygame.K_RETURN:
                        email_input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        email_input_text = email_input_text[:-1]
                    else:
                        if len(email_input_text) < 100:
                            email_input_text += event.unicode
                elif password_input_active:
                    if event.key == pygame.K_RETURN:
                        password_input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        password_input_text = password_input_text[:-1]
                    else:
                        if len(password_input_text) < 100:
                            password_input_text += event.unicode
            elif event.type == MOUSEBUTTONDOWN:
                if name_input.collidepoint(mouse_pos):
                    name_input_active = True
                    email_input_active = False
                    password_input_active = False
                elif email_input.collidepoint(mouse_pos):
                    name_input_active = False
                    email_input_active = True
                    password_input_active = False
                elif password_input.collidepoint(mouse_pos):
                    name_input_active = False
                    email_input_active = False
                    password_input_active = True
                else:
                    name_input_active = False
                    email_input_active = False
                    password_input_active = False
                if submit_button.collidepoint(event.pos):
                    # validate user input
                    name = name_input_text.strip()
                    email = email_input_text.strip()
                    password = password_input_text.strip()
                    if not name:
                        name_error = 'Name is required.'
                    else:
                        name_error = ''
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
                    if not name_error and not email_error and not password_error:

                        # Attempt to register the user (password is hashed in register_user())
                        if register_user(name, email, password):
                            done = True
                        else:
                            submit_error = 'Registration failed. Please check your connection and try again.'
                        


        # draw Pygame input fields and labels
        bg_color = (64, 64, 64)
        screen.fill(bg_color)
        pygame.draw.rect(screen, (200, 200, 200), name_input)
        pygame.draw.rect(screen, (200, 200, 200), email_input)
        pygame.draw.rect(screen, (200, 200, 200), password_input)
        pygame.draw.rect(screen, (0, 255, 0), submit_button)
        screen.blit(name_label, (250, 210))
        screen.blit(email_label, (250, 270))
        screen.blit(password_label, (250, 330))
        screen.blit(submit_label, (400, 395))

        # draw Pygame error messages
        name_error_text = error_font.render(name_error, True, (255, 0, 0))
        email_error_text = error_font.render(email_error, True, (255, 0, 0))
        password_error_text = error_font.render(password_error, True, (255, 0, 0))
        submit_error_text = error_font.render(submit_error, True, (255, 0, 0))
        screen.blit(name_error_text, (575, 215))
        screen.blit(email_error_text, (575, 275))
        screen.blit(password_error_text, (575, 335))
        screen.blit(submit_error_text, (575, 395))


        # Draw Pygame user input fields
        max_visible_chars = (name_input.width - 10) // font.size(" ")[0]
        visible_name_input_text = name_input_text[-max_visible_chars:]
        visible_email_input_text = email_input_text[-max_visible_chars:]
        visible_password_input_text = password_input_text[-max_visible_chars:]

        name_input_text_surface = font.render(visible_name_input_text, True, (0, 0, 0))
        email_input_text_surface = font.render(visible_email_input_text, True, (0, 0, 0))
        password_input_text_surface = font.render(visible_password_input_text, True, (0, 0, 0))

        # Calculate the vertical position for the text surfaces
        name_input_text_y = name_input.y + (name_input.height // 2) - (name_input_text_surface.get_height() // 2)
        email_input_text_y = email_input.y + (email_input.height // 2) - (email_input_text_surface.get_height() // 2)
        password_input_text_y = password_input.y + (password_input.height // 2) - (password_input_text_surface.get_height() // 2)

        # Calculate horizontal position for the text surfaces
        name_input_text_x = name_input.x + 5 - max(0, font.size(name_input_text)[0] - name_input.width + 10)
        email_input_text_x = email_input.x + 5 - max(0, font.size(email_input_text)[0] - email_input.width + 10)
        password_input_text_x = password_input.x + 5 - max(0, font.size(password_input_text)[0] - password_input.width + 10)

        # Draw Pygame user input fields
        screen.set_clip(name_input)  # Set clipping area to the name_input rect
        screen.blit(name_input_text_surface, (name_input_text_x, name_input_text_y))
        screen.set_clip(email_input)  # Set clipping area to the email_input rect
        screen.blit(email_input_text_surface, (email_input_text_x, email_input_text_y))
        screen.set_clip(password_input)  # Set clipping area to the password_input rect
        screen.blit(password_input_text_surface, (password_input_text_x, password_input_text_y))

        screen.set_clip(None)  # Reset the clipping area


        # update Pygame display
        pygame.display.flip()
        clock.tick(60)
        pygame.display.update()



def register_user(username, email, password):
    """
    register_user: Registers a new user with the provided information.
    Parameters:
    username (str) - The chosen username of the new user;
    email (str) - The email address of the new user;
    password (str) - The password for the new user's account.
    Returns: success (bool) - True if the registration is successful, False otherwise.
    Side Effects: Connects to the server, sends user registration information, and closes the connection.
    Dependencies: socket, ssl, threading, client_sock_utils, messages, bcrypt
    """
    # TODO: add to central config file to avoid changing in multiple places
    ADDRESS = 'localhost'
    PORT = 9999

    # create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # wrap the socket object in an SSL context
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.load_verify_locations('server.crt')
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

        # Encode the password as bytes
        password_bytes = password.encode('utf-8')

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        register_msg = messages.RegisterMessage(username=username, email=email, password=hashed_password.decode('utf-8'))
        client_sock_utils.send_message(client_socket, register_msg)

        # Return success message 
        return True
        
    except:
        print('Error connecting to server.')

        return False

