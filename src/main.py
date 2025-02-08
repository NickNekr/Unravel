import pygame
import sys
import os
import time
from math import floor
from constants import *

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Unravel")

font = pygame.font.Font(None, 36)

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
        return [], []

    levels, steps = [], []
    for filename in sorted(os.listdir(directory)):
        try:
            with open(os.path.join(directory, filename), 'r') as file:
                lines = file.readlines()
                steps_line = lines[0].upper()
                if steps_line.startswith("STEPS:"):
                    steps.append(int(steps_line.split(":")[1]))
                else:
                    print(f"Error in level {filename}: First line must start with 'STEPS:'")
                    continue

                level = [line for line in lines[1:] if line]
                if level:
                    levels.append(level)
                else:
                    print(f"Error in level {filename}: Level grid is empty")
        except Exception as e:
            print(f"Error loading level {filename}: {e}")
    return levels, steps

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
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if sprite := images.get(tile, None):
                screen.blit(sprite, (x * SIZE, y * SIZE))

def check_win(level):
    return not any(direction.value in row for direction in Direction for row in level)

def draw_status(start_time, steps):
    elapsed_time = time.time() - start_time
    timer_text = f"Time: {int(elapsed_time)}s"
    steps_text = f"Steps: {steps}"
    timer_surface = font.render(timer_text, True, BLACK)
    steps_surface = font.render(steps_text, True, BLACK)
    
    screen.blit(timer_surface, (WIDTH - 200, 20))
    screen.blit(steps_surface, (WIDTH - 200, 60))

def draw_level_menu(selected_level, completed_levels, total_levels):
    screen.fill(WHITE)
    title_surface = font.render("Select a Level", True, BLACK)
    screen.blit(title_surface, ((WIDTH - title_surface.get_width()) // 2, 50))
    
    for i in range(total_levels):
        level_text = f"Level {i + 1} {'(Completed)' if i in completed_levels else ''}"
        color = BLACK if i == selected_level else GREEN
        if i in completed_levels:
            color = BLACK if i == selected_level else GREEN
        else:
            color = BLACK if i == selected_level else SAND
        level_surface = font.render(level_text, True, color)
        screen.blit(level_surface, (WIDTH // 2 - 100, 150 + i * 40))
    
    pygame.display.flip()

def level_selector(levels):
    total_levels = len(levels)
    selected_level = 0
    completed_levels = load_progress()

    while True:
        draw_level_menu(selected_level, completed_levels, total_levels)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_level = (selected_level - 1) % total_levels
                if event.key == pygame.K_DOWN:
                    selected_level = (selected_level + 1) % total_levels
                if event.key == pygame.K_RETURN:
                    return selected_level, completed_levels

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

def main():
    levels, max_steps = load_levels(LEVELS_DIR)
    if not levels:
        print("No levels to load. Please check the 'levels' directory.")
        return

    while True:
        current_level_index, completed_levels = level_selector(levels)
        original_level = levels[current_level_index]
        level = [row[:] for row in original_level]
        steps = max_steps[current_level_index]

        clock = pygame.time.Clock()
        start_time = time.time()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    tile_pos_x, tile_pos_y = floor(x / SIZE), floor(y / SIZE)
                    if floor(y / SIZE) >= len(level) or floor(x / SIZE) >= len(level[0]):
                        print("You should move arrow!")
                        continue
                    level, is_moved = move_arrow(level, tile_pos_x, tile_pos_y)
                    if is_moved:
                        steps -= 1
                    print(f'Mouse clicked at {tile_pos_x}, {tile_pos_y}')

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
                    break
                if steps == 0:
                    print("Уровень провален!")
                    level = [row[:] for row in original_level]
                    steps = max_steps[current_level_index]
                    start_time = time.time()

                screen.fill(WHITE)
                draw_level(level)
                draw_status(start_time, steps)
                pygame.display.flip()
                clock.tick(60)
                continue

            break

if __name__ == "__main__":
    main()