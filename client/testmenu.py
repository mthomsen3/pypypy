import pygame
import sys

pygame.init()

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
BG_COLOR = (200, 200, 200)
FONT_COLOR = (0, 0, 0)
MENU_COLOR = (240, 240, 240)
SELECTED_MENU_COLOR = (180, 180, 180)

games = ["Pong", "Chess", "Poker", "Checkers"]

# Create the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Select a Game')

# Load font
font = pygame.font.Font(None, 24)

def draw_menu(is_open, selected_game):
    if is_open:
        menu_rect = pygame.Rect(10, 40, 200, 30 * len(games))
        pygame.draw.rect(screen, MENU_COLOR, menu_rect)

        for index, game in enumerate(games):
            text_surface = font.render(game, True, FONT_COLOR)
            if index == selected_game:
                pygame.draw.rect(screen, SELECTED_MENU_COLOR, pygame.Rect(menu_rect.x, menu_rect.y + 30 * index, menu_rect.width, 30))
            screen.blit(text_surface, (menu_rect.x + 10, menu_rect.y + 30 * index))

    default_text = f"Choose a Game: {games[selected_game]}" if is_open else "Choose a Game"
    text_surface = font.render(default_text, True, FONT_COLOR)
    screen.blit(text_surface, (10, 10))


def main():
    menu_open = False
    selected_game = 0

    while True:
        screen.fill(BG_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if not menu_open:
                    menu_open = True
                elif 10 <= x <= 210 and 40 <= y <= 40 + 30 * len(games):
                    selected_game = (y - 40) // 30
                else:
                    menu_open = False

        draw_menu(menu_open, selected_game)
        pygame.display.flip()

if __name__ == '__main__':
    main()
