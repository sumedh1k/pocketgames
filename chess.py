import pygame
import os
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
tile_selected_pink = load_image("Assets/Chess/Board/tile_selected_pink.png")
tile_selected_blue = load_image("Assets/Chess/Board/tile_selected_blue.png")

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

# Smaller versions of the pieces for the capture boxes
CAPTURE_SIZE = 60
capture_piece_images = {
    piece: pygame.transform.scale(img, (CAPTURE_SIZE, CAPTURE_SIZE))
    for piece, img in piece_images.items()
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

# Game state
selected_square = None
turn = "pink"  # pink pieces are uppercase
captured_pink = []
captured_blue = []
scroll_pink = 0
scroll_blue = 0

# drag state for picking up pieces
dragging_piece = None
drag_start = None
drag_pos = (0, 0)

# Draw the board
def draw_board():
    for row in range(8):
        for col in range(8):
            tile = tile_light if (row + col) % 2 == 0 else tile_dark
            x = BOARD_ORIGIN[0] + col * TILE_SIZE
            y = BOARD_ORIGIN[1] + row * TILE_SIZE
            screen.blit(tile, (x, y))
            if selected_square == (row, col):
                piece = board[row][col]
                if piece:
                    highlight = tile_selected_pink if piece.isupper() else tile_selected_blue
                    screen.blit(highlight, (x, y))
    screen.blit(border, BOARD_ORIGIN)
    screen.blit(numbers, (521, 140))
    screen.blit(letters, (560, 948))

# Draw the pieces
def draw_pieces():
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                if dragging_piece and drag_start == (row, col):
                    continue
                img = piece_images[piece]
                x = BOARD_ORIGIN[0] + col * TILE_SIZE
                y = BOARD_ORIGIN[1] + row * TILE_SIZE
                screen.blit(img, (x, y))
    if dragging_piece:
        img = piece_images[dragging_piece]
        x = drag_pos[0] - TILE_SIZE // 2
        y = drag_pos[1] - TILE_SIZE // 2
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

    # Draw captured pieces for pink (top box) and blue (bottom box)
    for i, piece in enumerate(captured_pink[scroll_pink:scroll_pink + 6]):
        img = capture_piece_images[piece]
        x = 10 + i * CAPTURE_SIZE
        y = 140 + (capture_box.get_height() - CAPTURE_SIZE) // 2
        screen.blit(img, (x, y))

    for i, piece in enumerate(captured_blue[scroll_blue:scroll_blue + 6]):
        img = capture_piece_images[piece]
        x = 10 + i * CAPTURE_SIZE
        y = 785 + (capture_box.get_height() - CAPTURE_SIZE) // 2
        screen.blit(img, (x, y))


# Functions for Calculations
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Convert a pixel coordinate to board square indices
def pixel_to_square(pos):
    x, y = pos
    col = (x - BOARD_ORIGIN[0]) // TILE_SIZE
    row = (y - BOARD_ORIGIN[1]) // TILE_SIZE
    if 0 <= row < 8 and 0 <= col < 8:
        return int(row), int(col)
    return None

# Determine if a move is legal according to basic chess rules
def is_legal_move(start, end, piece):
    sr, sc = start
    er, ec = end
    if sr == er and sc == ec:
        return False

    target = board[er][ec]
    if target and (target.isupper() == piece.isupper()):
        return False

    dr = er - sr
    dc = ec - sc

    direction = -1 if piece.isupper() else 1

    if piece.upper() == 'P':
        start_row = 6 if piece.isupper() else 1
        if dc == 0:
            if dr == direction and target == "":
                return True
            if sr == start_row and dr == 2 * direction and target == "" and board[sr + direction][sc] == "":
                return True
        if abs(dc) == 1 and dr == direction and target != "":
            return True
        return False

    if piece.upper() == 'N':
        return (abs(dr), abs(dc)) in ((2, 1), (1, 2))

    if piece.upper() == 'B':
        if abs(dr) != abs(dc):
            return False
        step_r = 1 if dr > 0 else -1
        step_c = 1 if dc > 0 else -1
        for i in range(1, abs(dr)):
            if board[sr + i * step_r][sc + i * step_c] != "":
                return False
        return True

    if piece.upper() == 'R':
        if dr != 0 and dc != 0:
            return False
        if dr == 0:
            step_c = 1 if dc > 0 else -1
            for i in range(1, abs(dc)):
                if board[sr][sc + i * step_c] != "":
                    return False
        else:
            step_r = 1 if dr > 0 else -1
            for i in range(1, abs(dr)):
                if board[sr + i * step_r][sc] != "":
                    return False
        return True

    if piece.upper() == 'Q':
        if abs(dr) == abs(dc):
            return is_legal_move(start, end, 'B')
        if dr == 0 or dc == 0:
            return is_legal_move(start, end, 'R')
        return False

    if piece.upper() == 'K':
        return max(abs(dr), abs(dc)) == 1

    return False

# Main loop
def main():
    global scroll_pink, scroll_blue, turn, selected_square
    global dragging_piece, drag_start, drag_pos

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

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if event.button in (4, 5):
                    if 0 <= pos[0] < capture_box.get_width() and 140 <= pos[1] < 140 + capture_box.get_height():
                        if event.button == 4:
                            scroll_pink = max(0, scroll_pink - 1)
                        elif scroll_pink + 6 < len(captured_pink):
                            scroll_pink += 1
                        continue
                    if 0 <= pos[0] < capture_box.get_width() and 785 <= pos[1] < 785 + capture_box.get_height():
                        if event.button == 4:
                            scroll_blue = max(0, scroll_blue - 1)
                        elif scroll_blue + 6 < len(captured_blue):
                            scroll_blue += 1
                        continue

                if event.button == 1 and not dragging_piece:
                    square = pixel_to_square(pos)
                    if square:
                        row, col = square
                        piece = board[row][col]
                        if piece and ((turn == 'pink' and piece.isupper()) or (turn == 'blue' and piece.islower())):
                            dragging_piece = piece
                            drag_start = (row, col)
                            drag_pos = pos
                            selected_square = (row, col)

            elif event.type == pygame.MOUSEMOTION:
                if dragging_piece:
                    drag_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                pos = event.pos
                if event.button == 1 and dragging_piece:
                    square = pixel_to_square(pos)
                    sr, sc = drag_start
                    if square and is_legal_move(drag_start, square, dragging_piece):
                        er, ec = square
                        target = board[er][ec]
                        if target:
                            if dragging_piece.isupper():
                                captured_pink.append(target)
                            else:
                                captured_blue.append(target)
                        board[er][ec] = dragging_piece
                        board[sr][sc] = ""
                        turn = "blue" if turn == "pink" else "pink"
                    dragging_piece = None
                    drag_start = None
                    selected_square = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
