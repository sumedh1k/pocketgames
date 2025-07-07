import pygame
import subprocess
import os
import time
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
dimensions = pygame.display.Info()
# width, height = dimensions.current_w, dimensions.current_h #use for adjusting resolution
width, height = 1920, 1080
center_x, center_y = width // 2, height // 2
BG_COLOR = (0, 0, 0)  # Black background
TILE_SIZE = 100
BOARD_ORIGIN = ((width-800) // 2, (height-800) // 2)  # Offset based on 800x800 px board and 1920x1080 resolution
NEON_BLUE = (0,255,246)

#fonts
font = pygame.font.Font("Assets/Fonts/Orbitron-Medium.ttf", 35)

# Create the screen
screen = pygame.display.set_mode((width, height), pygame.NOFRAME) # noframe gets rid of screen resizing problem
pygame.display.set_caption('Chess')
# os.environ['SDL_VIDEO_CENTERED'] = '1'  # centers window | delete for ubuntu

# Load assets
def load_image(path, size=None):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size) if size else img

# Load board elements
tile_light = load_image("Assets/Chess/Board/tile_light.png")
tile_dark = load_image("Assets/Chess/Board/tile_dark.png")
border = load_image("Assets/Chess/Board/border.png")
letters = load_image("Assets/Chess/Board/letters.png")
numbers = load_image("Assets/Chess/Board/numbers.png")

# Load pieces
piece_images = {
    "P": load_image("Assets/Chess/Pieces/pawn_pink.png"),
    "p": load_image("Assets/Chess/Pieces/pawn_blue.png"),
    "R": load_image("Assets/Chess/Pieces/rook_pink.png"),
    "r": load_image("Assets/Chess/Pieces/rook_blue.png"),
    "N": load_image("Assets/Chess/Pieces/knight_pink.png"),
    "n": load_image("Assets/Chess/Pieces/knight_blue.png"),
    "B": load_image("Assets/Chess/Pieces/bishop_pink.png"),
    "b": load_image("Assets/Chess/Pieces/bishop_blue.png"),
    "Q": load_image("Assets/Chess/Pieces/queen_pink.png"),
    "q": load_image("Assets/Chess/Pieces/queen_blue.png"),
    "K": load_image("Assets/Chess/Pieces/king_pink.png"),
    "k": load_image("Assets/Chess/Pieces/king_blue.png"),
}

# Load UI (username, move history, captures, home button)
username_box = load_image("Assets/Chess/UI/username_box.png")
player1_name = font.render("Sumedh", True, NEON_BLUE)
player1_rect = player1_name.get_rect(center=(center_x+15,65))
player2_name = font.render("Erica", True, NEON_BLUE)
player2_rect = player2_name.get_rect(center=(center_x+15,1025))
move_history_box = load_image("Assets/Chess/UI/move_history.png")
capture_box = load_image("Assets/Chess/UI/capture_box.png")
home_button = load_image("Assets/Chess/UI/home_button.png")

# Initial board state
board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p"] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    ["P"] * 8,
    ["R", "N", "B", "Q", "K", "B", "N", "R"]
]

# Draw the board
def draw_board():
    for row in range(8):
        for col in range(8):
            tile = tile_light if (row + col) % 2 == 0 else tile_dark
            x = BOARD_ORIGIN[0] + col * TILE_SIZE
            y = BOARD_ORIGIN[1] + row * TILE_SIZE
            screen.blit(tile, (x, y))
    screen.blit(border, BOARD_ORIGIN)
    screen.blit(numbers, (521, 140))
    screen.blit(letters, (560, 948))

# Draw the pieces
def draw_pieces():
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                img = piece_images[piece]
                x = BOARD_ORIGIN[0] + col * TILE_SIZE
                y = BOARD_ORIGIN[1] + row * TILE_SIZE
                screen.blit(img, (x, y))
def draw_ui():
    screen.blit(username_box, (600, 25))
    screen.blit(player1_name, player1_rect)
    screen.blit(username_box, (600, 985))
    screen.blit(player2_name, player2_rect)
    screen.blit(home_button, (525, 25))
    screen.blit(move_history_box, (1425, 141))
    screen.blit(move_history_box, (1425, 141))
    screen.blit(capture_box, (0, 785))
    screen.blit(capture_box, (0, 140))


# Functions for Calculations
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Main loop
def main():
    running = True
    while running:
        
        screen.fill(BG_COLOR)
        draw_board()
        draw_pieces()
        draw_ui()
        pygame.display.flip()

        # track controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.pos #placeholder
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()