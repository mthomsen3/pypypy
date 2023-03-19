

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


def run(screen, client_socket, username, new_lobby):
    
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 24)
    
    
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
                
        screen.fill(BG_COLOR)

        # Get mouse position
        x, y = pygame.mouse.get_pos()

        start_game_rect = pygame.Rect(SCREEN_WIDTH // 2 - 60, 400, 120, 30)
        start_game_color = (96, 96, 96)
        start_game_hover_color = (128, 128, 128)
        start_game_hovered = start_game_rect.collidepoint(x, y)
        draw_button(screen, font, "Start Game", start_game_rect.x, start_game_rect.y, start_game_rect.width, start_game_rect.height, start_game_color, start_game_hover_color, start_game_hovered)
        

        # Check for incoming messages
        while not client_sock_utils.q.empty():
            message = client_sock_utils.q.get()
            print(message)

        pygame.display.flip()
        clock.tick(60)
        pygame.display.update()