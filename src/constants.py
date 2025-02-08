from enum import Enum, auto

class Direction(Enum):
    UP = 'U'
    RIGHT = 'R'
    DOWN = 'D'
    LEFT = 'L'

WIDTH, HEIGHT = 1000, 600
SIZE = 36
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
SAND = (220, 212, 171)

LEVELS_DIR = "levels"
PROGRESS_FILE = "progress.dat"
IMAGES = "images"

class Direction(Enum):
    UP = 'U'
    RIGHT = 'R'
    DOWN = 'D'
    LEFT = 'L'