# Settings for Simple Pong Game.  

from enum import Enum

CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 700
SPACING = 100
DISTANCE_BAR_BOUND = 40
GRID_SIZE = 40

# A total of two players must be specified across the following categories.
local_human_players = 0
local_bot_players = 1
remote_players = 1

winning_score = 5

class Direction(Enum):
    DOWN = 0
    UP = 1
    LEFT = 2
    RIGHT = 3


