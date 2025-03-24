import pygame
import sys
import os
import time
from math import floor
import queue
import random
from constants import *

pygame.init()

# pygame.mixer.init()
# pygame.mixer.music.load("music.mp3")
# pygame.mixer.music.play(-1,0.0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Unravel")

font = pygame.font.Font('Pacifico-Regular.ttf', 24)

def load_images():
    images = {}
    if not os.path.exists(IMAGES):
        print(f"Error: Image directory '{IMAGES}' not found.")
        sys.exit()

    try:
        images[Direction.UP.value] = pygame.image.load(f'./{IMAGES}/up.jpg').convert()
        images[Direction.RIGHT.value] = pygame.image.load(f'./{IMAGES}/right.jpg').convert()
        images[Direction.DOWN.value] = pygame.image.load(f'./{IMAGES}/down.jpg').convert()
        images[Direction.LEFT.value] = pygame.image.load(f'./{IMAGES}/left.jpg').convert()
        images[' '] = pygame.image.load(f'./{IMAGES}/background.jpg').convert()
        images['*'] = pygame.image.load(f'./{IMAGES}/saw.jpg').convert()
    except pygame.error as e:
        print(f"Error loading images: {e}")
        sys.exit()
    return images

def load_levels(directory):
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' not found.")
        return [], [], []

    levels, steps, difficulty = [], [], []
    for filename in sorted(os.listdir(directory)):
        try:
            with open(os.path.join(directory, filename), 'r') as file:
                lines = file.readlines()
                steps_line = lines[0]
                difficulty_line = lines[1]
                if steps_line.startswith("STEPS:"):
                    steps.append(int(steps_line.split(":")[1]))
                else:
                    print(f"Error in level {filename}: First line must start with 'STEPS:'")
                    continue

                if difficulty_line.startswith("Difficulty:"):
                    difficulty.append(difficulty_line.split(":")[1])
                else:
                    print(f"Error in level {filename}: Second line must start with 'Difficulty:'")
                    continue

                level = [line for line in lines[2:] if line]
                if level:
                    levels.append(level)
                else:
                    print(f"Error in level {filename}: Level grid is empty")
        except Exception as e:
            print(f"Error loading level {filename}: {e}")
    return levels, steps, difficulty

def save_progress(completed_levels):
    try:
        with open(PROGRESS_FILE, "w") as f:
            for level in completed_levels:
                f.write(f"{level}\n")
    except Exception as e:
        print(f"Error saving progress: {e}")

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return set()
    
    try:
        with open(PROGRESS_FILE, "r") as f:
            return set(int(line.strip()) for line in f.readlines())
    except Exception as e:
        print(f"Error loading progress: {e}")
        return set()

def draw_level(level):
    images = load_images()
    screen_width, screen_height = screen.get_size()
    level_width = len(level[0]) * SIZE
    level_height = len(level) * SIZE
    
    offset_x = (screen_width - level_width) // 2
    offset_y = (screen_height - level_height) // 2
    
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if sprite := images.get(tile, None):
                screen.blit(sprite, (x * SIZE + offset_x, y * SIZE + offset_y))

def move_arrow(level, pos_x, pos_y):
    new_level = [list(row) for row in level]
    tile = level[pos_y][pos_x]

    try:
        direction = Direction(tile)
    except ValueError:
        print("You should move an arrow!")
        return new_level, 0

    dx, dy = 0, 0
    if direction == Direction.UP:
        dy = -1
    elif direction == Direction.RIGHT:
        dx = 1
    elif direction == Direction.DOWN:
        dy = 1
    elif direction == Direction.LEFT:
        dx = -1

    arrow_dist = 1
    while level[pos_y + dy * arrow_dist][pos_x + dx * arrow_dist] == ' ':
        arrow_dist += 1

    new_level[pos_y][pos_x] = ' '
    if new_level[pos_y + dy * arrow_dist][pos_x + dx * arrow_dist] != '*':
        new_level[pos_y + dy * (arrow_dist - 1)][pos_x + dx * (arrow_dist - 1)] = direction.value

    return new_level, 1


def check_win(level):
    return not any(direction.value in row for direction in Direction for row in level)

def next_vertex_on_direction(level, pos_x, pos_y):
    tile = level[pos_y][pos_x]
    direction = Direction(tile)
    dx, dy = 0, 0
    if direction == Direction.UP:
        dy = -1
    elif direction == Direction.RIGHT:
        dx = 1
    elif direction == Direction.DOWN:
        dy = 1
    elif direction == Direction.LEFT:
        dx = -1

    arrow_dist = 1
    while level[pos_y + dy * arrow_dist][pos_x + dx * arrow_dist] == ' ':
        arrow_dist += 1
    if level[pos_y + dy * arrow_dist][pos_x + dx * arrow_dist] == '*':
        return '*', arrow_dist

    return level[pos_y + dy * arrow_dist][pos_x + dx * arrow_dist], arrow_dist

def is_solvable_by_steps(copy_level) -> int:
    steps_to_solve = 0
    # try kill by direct saw
    while True:
        deleted = False
        for y, row in enumerate(copy_level):
            for x, tile in enumerate(row):
                if any(direction.value == tile for direction in Direction) and next_vertex_on_direction(copy_level, x, y)[0] == '*':
                    copy_level[y][x] = ' ' 
                    steps_to_solve += 1
                    deleted = True
        if not deleted:
            break
    # check win
    if check_win(copy_level):
        return steps_to_solve
    # queue of movable arrows
    q = queue.Queue()
    for y, row in enumerate(copy_level):
        for x, tile in enumerate(row):
            if tile == 'UP' or tile == 'DOWN' or tile == 'LEFT' or tile == 'RIGHT':
                next_vertex = next_vertex_on_direction(copy_level, x, y)
                next_tile = next_vertex[0]
                if tile == Direction.UP and next_tile == Direction.DOWN:
                    return -1
                if tile == Direction.DOWN and next_tile == Direction.UP:
                    return -1
                if tile == Direction.RIGHT and next_tile == Direction.LEFT:
                    return -1
                if tile == Direction.LEFT and next_tile == Direction.UP:
                    return -1
                if next_vertex[1] > 1:
                    q.put((x, y)) 
    while not q.empty():
        x, y = q.get()
        another_copy, _ = move_arrow(copy_level, x, y)         
        next_steps = is_solvable_by_steps(another_copy)
        if next_steps >= 0:
            return steps_to_solve + next_steps

    return -1

def draw_status(level, start_time, steps, difficulty, current_level_index):
    elapsed_time = time.time() - start_time
    timer_text = f"Time: {int(elapsed_time)}s"
    steps_text = f"Steps: {steps}"
    copy_level = [list(row) for row in level]
    still_solvable = f"Solvable: " + str(is_solvable_by_steps(copy_level) > 0)
    difficulty_of_lvl = f"Difficulty: {difficulty}"
    lvl_index = f"Level: #{current_level_index + 1}"

    timer_surface = font.render(timer_text, True, BLACK)
    steps_surface = font.render(steps_text, True, BLACK)
    still_solvable = font.render(still_solvable, True, BLACK)
    difficulty_of_lvl = font.render(difficulty_of_lvl, True, BLACK)
    lvl_index = font.render(lvl_index, True, BLACK)
    
    screen.blit(lvl_index, (WIDTH // 2 - 230, 20))
    screen.blit(timer_surface, (WIDTH // 2 - 230, 60))
    screen.blit(steps_surface, (WIDTH // 2 - 90, 20))
    screen.blit(still_solvable, (WIDTH // 2 - 90, 60))
    screen.blit(difficulty_of_lvl, (WIDTH // 2 + 55, 20))

def draw_menu(lvl_index, difficulty):
    screen.fill(SAND)
    welcome_surface = font.render("Welcome to Unravel!", True, TERRACOTA)
    title_surface = font.render("Select a Level", True, BLACK)
    play_surface = font.render("Play!", True, TERRACOTA)

    lvl_surface = font.render(f"Level: #{lvl_index}", True, TERRACOTA)
    difficulty_surface = font.render(f"Difficulty: {difficulty}", True, TERRACOTA)

    screen.blit(title_surface, ((WIDTH - title_surface.get_width()) // 2, 75))
    screen.blit(welcome_surface, ((WIDTH - welcome_surface.get_width()) // 2, 25))
    screen.blit(play_surface, ((WIDTH - play_surface.get_width()) // 2, HEIGHT // 2))
    screen.blit(lvl_surface, ((WIDTH - play_surface.get_width()) // 2 - 20, HEIGHT // 2 + 40))
    screen.blit(difficulty_surface, ((WIDTH - play_surface.get_width()) // 2 - 60, HEIGHT // 2 + 80))

    triangle_points = [
        (0, 0),  # Левая точка
        (0, 100),  # Нижняя точка
        (-100, 50)   # Правая точка (острие)
    ]
    
    border_points = [
        ((WIDTH - triangle_points[0][0]) // 2 - 25, (HEIGHT - triangle_points[0][1]) // 2 + 7),
        ((WIDTH - triangle_points[1][0]) // 2 - 25, (HEIGHT - triangle_points[1][1]) // 2 - 7),
        ((WIDTH - triangle_points[2][0]) // 2 - 13, (HEIGHT - triangle_points[2][1]) // 2)
    ]
    pygame.draw.polygon(screen, (50, 50, 50), border_points)  # Обводка

    inner_points = [
        ((WIDTH - triangle_points[0][0]) // 2 - 20, (HEIGHT - triangle_points[0][1]) // 2),
        ((WIDTH - triangle_points[1][0]) // 2 - 20, (HEIGHT - triangle_points[1][1]) // 2),
        ((WIDTH - triangle_points[2][0]) // 2 - 20, (HEIGHT - triangle_points[2][1]) // 2)
    ]
    pygame.draw.polygon(screen, TERRACOTA, inner_points)  # Внутренняя часть



    pygame.display.flip()


def level_selector(go_next_level, next_level, difficulty):
    if go_next_level:
        return
    while True:
        draw_menu(next_level, difficulty)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

def main():
    levels, max_steps, all_difficulties = load_levels(LEVELS_DIR)
    go_next_level = False
    if not levels:
        print("No levels to load. Please check the 'levels' directory.")
        return

    while True:
        completed_levels = load_progress()
        current_level_index = 0
        if completed_levels:
            current_level_index = max(completed_levels) + 1
        if current_level_index >= len(levels):
            print("You completed the game!")
            return

        original_level = levels[current_level_index]
        level = [row[:] for row in original_level]
        steps = max_steps[current_level_index]
        difficulty = all_difficulties[current_level_index]

        level_selector(go_next_level, current_level_index, difficulty)

        clock = pygame.time.Clock()
        start_time = time.time()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    screen_width, screen_height = screen.get_size()
                    level_width = len(level[0]) * SIZE
                    level_height = len(level) * SIZE
                    offset_x = (screen_width - level_width) // 2
                    offset_y = (screen_height - level_height) // 2
                    tile_pos_x, tile_pos_y = floor((x - offset_x) / SIZE), floor((y - offset_y) / SIZE)
                    print(tile_pos_x, tile_pos_y)
                    if tile_pos_y >= len(level) or tile_pos_x >= len(level[0]) or\
                        tile_pos_y < 0 or tile_pos_x < 0:
                        print("You should move arrow!")
                        continue
                    level, is_moved = move_arrow(level, tile_pos_x, tile_pos_y)
                    if is_moved:
                        steps -= 1
                    

                if event.type == pygame.KEYDOWN:        
                    if event.key == pygame.K_r:
                        level = [row[:] for row in original_level]
                        steps = max_steps[current_level_index]
                        start_time = time.time()

                    if event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                        break

            else:
                if check_win(level):
                    print("Уровень пройден!")
                    completed_levels.add(current_level_index)
                    save_progress(completed_levels)
                    go_next_level = True
                    break
                if steps == 0:
                    print("Уровень провален!")
                    level = [row[:] for row in original_level]
                    steps = max_steps[current_level_index]
                    start_time = time.time()

                screen.fill(WHITE)
                pygame.draw.rect(screen, SAND, (0, 0, STRIPE_WIDTH, HEIGHT))
                pygame.draw.rect(screen, SAND, (WIDTH - STRIPE_WIDTH, 0, STRIPE_WIDTH, HEIGHT))
                draw_level(level)
                draw_status(level, start_time, steps, difficulty, current_level_index)
                pygame.display.flip()
                clock.tick(60)
                continue

            break

if __name__ == "__main__":
    main()