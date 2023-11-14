import random
import pygame

width = 900
height = 700
game_width = 320    # block of width 20
game_height = 600   # block of height 20
topleft_x = (width - game_width) // 2
topleft_y = height - game_height - 50
block_size = 20

# Shapes and its rotations in a 4x4 matrix with indexes 0-15
shapes = [
    [[1,5,9,13], [4,5,6,7]],    # I-shape and its rotations
    [[4,5,9,10], [2,5,6,9]],    # Z-shape and its rotations
    [[6,7,9,10], [1,5,6,10]],   # S-shape and its rotations
    [[1,5,9,10], [4,5,6,8], [1,2,6,10], [7,9,10,11]],   # L-shape and its rotations
    [[2,6,9,10], [4,8,9,10], [1,2,5,9], [5,6,7,11]],    # J-shape and its rotations
    [[5,8,9,10], [1,5,6,9], [5,6,7,10], [2,5,6,10]],    # T-shape and its rotations
    [[5,6,9,10]]    # O-shape and its rotations
]

shapecolors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (255, 0, 255), (0, 255, 255)]

class Block():
    x = y = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = self.color = random.randint(0, len(shapes)-1)
        self.rotation = random.randint(0, len(shapes[self.type])-1)
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(shapes[self.type])
    def image(self):
        return shapes[self.type][self.rotation]
    

def create_grid(locked_positions):
    grid = [[(255, 255, 255) for _ in range(16)] for _ in range(30)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid

def draw_grid(screen, grid, rows, columns):
    # Setting up the game environment
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont('comicsansms', 30)
    label = font.render('TETRIS', 1, (0, 255, 255))
    screen.blit(label, (topleft_x + game_width / 3, 10))
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(screen, grid[i][j], (topleft_x + j * 20, topleft_y + i * 20, 20, 20))
    pygame.draw.rect(screen, (255, 0, 0), (topleft_x, topleft_y, game_width, game_height), 2)
    for i in range(rows+1):
        pygame.draw.line(screen, (128, 128, 128), (topleft_x, topleft_y + i * 20), (topleft_x + game_width, topleft_y + i * 20))
    for i in range(columns+1):
        pygame.draw.line(screen, (128, 128, 128), (topleft_x + i * 20, topleft_y), (topleft_x + i * 20, topleft_y + game_height))

def new_block():
    block = Block(6, 0)
    return block

def shape_format(current_piece):
    positions = []
    for i in range(4):
        for j in range(4):
            p = i * 4 + j
            if p in current_piece.image():
                positions.append((current_piece.x + j, current_piece.y + i))
    return positions

def draw_text_middle(screen, text, size, color):
    font = pygame.font.SysFont("comicsansms", size, bold=True)
    label = font.render(text, 1, color)
    screen.blit(label, (width/3, height/3))

def draw_next_block(screen, next_piece):
    font = pygame.font.SysFont('comicsansms', 30)
    label = font.render('Next Block', 1, (0, 255, 255))
    sx = topleft_x + game_width + 90
    sy = topleft_y + game_height/3 + 50
    screen.blit(label, (sx - 40, sy - 50))
    pygame.draw.rect(screen, (0, 0, 0), (sx, sy, 80, 80))
    for i in range(4):
        for j in range(4):
            p = i * 4 + j
            if p in next_piece.image():
                pygame.draw.rect(screen, shapecolors[next_piece.color], (sx + j * 20, sy + i * 20, 20, 20))

def intersects(current_piece):
    intersection = False
    for i in range(4):
        for j in range(4):
            p = i * 4 + j
            if p in current_piece.image():
                if i + current_piece.y < 0 or j + current_piece.x < 0 or j + current_piece.x > 15:
                    intersection = True
    return intersection


def clear_rows(grid, locked_positions):
    inc = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        if (255, 255, 255) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                locked_positions.pop((j, i))
    if inc > 0:
        for key in sorted(list(locked_positions), key = lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                locked_positions[(x, y + inc)] = locked_positions[(x, y)]
                locked_positions.pop((x, y))
    return inc

def freezing(current_piece, locked_positions):
    freeze = False
    for i in range(4):
        for j in range(4):
            p = i * 4 + j
            if p in current_piece.image():
                sx = j + current_piece.x
                sy = i + current_piece.y
                if sy == 29 or ((sx, sy+1) in locked_positions):
                    freeze = True
    return freeze

def check_lost(locked_positions):
    for pos in locked_positions:
        x, y = pos
        if y < 1:
            return True
    return False

def update_score(score, max_score):
    if score > max_score:
        max_score = score
    return score, max_score

def main(screen):
    locked_positions = {}
    grid = create_grid(locked_positions)
    draw_grid(screen, grid,  30, 16)
    
    current_piece = new_block()
    next_piece = new_block()
    score = max_score = 0
    clock = pygame.time.Clock()
    UPDATE = pygame.USEREVENT
    pygame.time.set_timer(UPDATE, 200)
    running = True
    
    while running:

        grid = create_grid(locked_positions)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if intersects(current_piece):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if intersects(current_piece):
                        current_piece.x -= 1

                elif event.key == pygame.K_SPACE:
                    old_rotation = current_piece.rotation
                    current_piece.rotate()
                    if intersects(current_piece):
                        current_piece.rotation = old_rotation
                
                elif event.key == pygame.K_UP:
                    current_piece.y -= 1
                    if intersects(current_piece):
                        current_piece.y += 1
        
            elif event.type == UPDATE:
                current_piece.y += 1
                if intersects(current_piece):
                    current_piece.y -= 1
        
        positions = shape_format(current_piece)
        for i in range(len(positions)):
            x, y = positions[i]
            grid[y][x] = shapecolors[current_piece.color]

        if freezing(current_piece, locked_positions):
            for i in positions:
                locked_positions[i] = shapecolors[current_piece.color]
            current_piece = next_piece
            next_piece = new_block()
            score += clear_rows(grid, locked_positions)
        
        if check_lost(locked_positions):
            score, max_score = update_score(score, max_score)
            draw_text_middle(screen, f"Score : {score}", 55, (0, 0, 0))
            pygame.display.update()
            pygame.time.delay(1500)
            running = False

        draw_grid(screen, grid, 30, 16)
        draw_next_block(screen, next_piece)
        pygame.display.update()
        clock.tick(60)

def main_menu(screen):  
    run = True
    while run:
        screen.fill((0,0,0))
        draw_text_middle(screen, 'Press Any Key To Play', 30, (255,255,255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(screen)

    pygame.quit()

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tetris")

main_menu(screen)