'''


'''
import pygame
import client_sock_utils
import register_menu
import login_menu
import sys

VERSION = "v0.0.1"
ADDRESS = client_sock_utils.getIp(public=False)
PORT = 9999

# Initialize pygame
pygame.init()
pygame.display.set_caption("Pyew Pyew")

# Define window size
window_size = (800, 600)
screen = pygame.display.set_mode(window_size)

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# Set up the title
title_font = pygame.font.SysFont("Arial", 60, bold=True)
title_text = title_font.render("Pyew Pyew", True, (128, 128, 128))
title_text_rect = title_text.get_rect()
title_text_rect.center = (window_size[0]/2, 100)


# Create buttons
button_font = pygame.font.Font(None, 30)
login_button = pygame.Rect(300, 200, 200, 50)
login_button_text = button_font.render("Login", True, (255, 255, 255))
register_button = pygame.Rect(300, 275, 200, 50)
register_button_text = button_font.render("Register", True, (255, 255, 255))
about_button = pygame.Rect(300, 350, 200, 50)
about_button_text = button_font.render("About", True, (255, 255, 255))
settings_button = pygame.Rect(300, 425, 200, 50)
settings_button_text = button_font.render("Settings", True, (255, 255, 255))
quit_button = pygame.Rect(300, 500, 200, 50)
quit_button_text = button_font.render("Quit", True, (255, 255, 255))


# TODO: not working
def fade_in(screen):
    black_surface = pygame.Surface((800, 600))
    for alpha in range(0, 256, 5):  # Adjust the step (5) for different fading speeds
        screen.fill((70, 70, 70))
        black_surface.set_alpha(255 - alpha)
        screen.blit(black_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(30)  # Adjust the delay for different fading speeds

def fade_out(screen):
    black_surface = pygame.Surface((800, 600))
    for alpha in range(0, 256, 5):  # Adjust the step (5) for different fading speeds
        black_surface.set_alpha(alpha)
        screen.blit(black_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(30)  # Adjust the delay for different fading speeds


# Set initial state to "not connected"
connected = False
connecting = False
disconnecting = False

fade_in(screen)

# Start game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if login_button.collidepoint(mouse_pos):
                print("Login button clicked")
                login_menu.run(screen)
            elif register_button.collidepoint(mouse_pos):
                print("Register button clicked")
                register_menu.run(screen)
            elif about_button.collidepoint(mouse_pos):
                print("About button clicked")
            elif settings_button.collidepoint(mouse_pos):
                print("Settings button clicked")
            elif quit_button.collidepoint(mouse_pos):
                fade_out(screen)
                pygame.quit()
                sys.exit()
                    


    # Fill the background
    screen.fill(WHITE)

    # Draw title, buttons, and text
    screen.fill((70, 70, 70))
    screen.blit(title_text, title_text_rect)
    pygame.draw.rect(screen, GRAY, login_button)
    pygame.draw.rect(screen, GRAY, register_button)
    pygame.draw.rect(screen, GRAY, about_button)
    pygame.draw.rect(screen, GRAY, settings_button)
    pygame.draw.rect(screen, GRAY, quit_button)
    screen.blit(login_button_text, (login_button.centerx - login_button_text.get_width() / 2, login_button.centery - login_button_text.get_height() / 2))
    screen.blit(register_button_text, (register_button.centerx - register_button_text.get_width() / 2, register_button.centery - register_button_text.get_height() / 2))
    screen.blit(about_button_text, (about_button.centerx - about_button_text.get_width() / 2, about_button.centery - about_button_text.get_height() / 2))
    screen.blit(settings_button_text, (settings_button.centerx - settings_button_text.get_width() / 2, settings_button.centery - settings_button_text.get_height() / 2))
    screen.blit(quit_button_text, (quit_button.centerx - quit_button_text.get_width() / 2, quit_button.centery - quit_button_text.get_height() / 2))
    
    # Update display
    pygame.display.update()








    '''    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if connect_button.collidepoint(mouse_pos) and not connected and not connecting:
                # Start connecting to server
                connecting = True
                servaddr = (ADDRESS, PORT)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.connect(servaddr)
                    connected = True
                    connecting = False
                    thread = threading.Thread(target=client_sock_utils.bgThread, args=(sock,))
                    thread.start()

                    hello_msg = messages.HelloMessage(message="PyPyPy")
                    client_sock_utils.send_message(sock, hello_msg)
                    version_msg = messages.VersionMessage(version="v0.0.1")
                    client_sock_utils.send_message(sock, version_msg)

                    msg = client_sock_utils.read()
                    if msg == "errVer":
                        print(msg)

                    elif msg == "errBusy":
                        print(msg)

                    elif msg == "errLock":
                        print(msg)
                        
                    else:
                        print(msg)

                except ConnectionRefusedError:
                    connecting = False
            elif quit_button.collidepoint(mouse_pos) and connected and not disconnecting:
                # Send QUIT message and disconnect from server
                disconnecting = True
                client_sock_utils.send_message(sock, messages.QuitMessage())
                time.sleep(0.1)
                sock.close()
                connected = False
                disconnecting = False
            
    # Draw screen
    screen.fill(WHITE)
    if not connected:
        pygame.draw.rect(screen, GREEN, connect_button)
        screen.blit(connect_button_text, (50, 50))
    else:
        pygame.draw.rect(screen, RED, quit_button)
        screen.blit(quit_button_text, (50, 50))
    pygame.display.update()

'''


'''
# This is a main function that calls all other functions, socket initialisation
# and the screen that appears just after online menu but just before online lobby.
def main():
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servaddr = (ADDRESS, PORT)

    try:
        sock.connect(servaddr)

    except:
        return

    thread = threading.Thread(target=client_sock_utils.bgThread, args=(sock,))
    thread.start()

    #client_sock_utils.write(sock, "HELLO:PyPyPy")
    #client_sock_utils.write(sock, f"VERSION:{VERSION}")\

    hello_msg = messages.HelloMessage(message="PyPyPy")
    client_sock_utils.send_message(sock, hello_msg)

    version_msg = messages.VersionMessage(version="v0.0.1")
    client_sock_utils.send_message(sock, version_msg)
    

    msg = client_sock_utils.read()
    if msg == "errVer":
        print(msg)

    elif msg == "errBusy":
        print(msg)

    elif msg == "errLock":
        print(msg)
        
    else:
        print(msg)


    #client_sock_utils.write(sock, "quit")
    client_sock_utils.send_message(sock, messages.QuitMessage())
    sock.close()
    thread.join()
    client_sock_utils.flush()

main()
'''