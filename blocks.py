import pygame
import pygame as pg
import colors
from position import Position

GRID_HORIZONTAL_SIZE = 10
GRID_VERTICAL_SIZE = 20
GRID_RIGHT_TOP_CORNER_X = 20
GRID_RIGHT_TOP_CORNER_Y = 20
GRID_FIELD_SIZE = 30

class Block:

    def __init__(self, ):
        self.position = Position(0, 0)
        self.block_color = None
        self.rotations = None
        self.current_rotation = None
        self.tile_size = 30
    def draw(self, screen):
        for tile in self.rotations[self.current_rotation]:
            tile_rect = pygame.Rect((self.position.column+tile[0])*self.tile_size, (self.position.row+tile[1])*self.tile_size, self.tile_size-1, self.tile_size-1)
            pg.draw.rect(screen, colors.color[self.block_color], tile_rect)

    def check_collision_with_wall(self, movement, grid):
        for tile in self.rotations[self.current_rotation]: # zwraca true jeśli jest kolizja
            if (self.position.column + tile[0] + movement) >= 10 or (self.position.column + tile[0] + movement) < 0 or grid.grid[self.position.row+tile[1]][self.position.column+tile[0]+movement] != 0:
                return True
        return False

    def check_rotate_collision(self, grid):
        for tile in self.rotations[(self.current_rotation + 1) % len(self.rotations)]:
            if self.position.column+tile[0] >= 10 or self.position.column+tile[0] < 0 or grid.grid[self.position.row+tile[1]][self.position.column+tile[0]] != 0:
                return True
        return False

    def move_x(self, movement, grid):
        if not self.check_collision_with_wall(movement, grid):
            self.position.column = self.position.column + movement

    def rotate(self, grid):
        if not self.check_rotate_collision(grid):
            self.current_rotation = (self.current_rotation + 1) % len(self.rotations)



# PO I PRZED ROTACJI SPRAWDZIĆ CZY BLOK JUŻ NIE SPADŁ
class IBlock(Block):
    def __init__(self):
        Block.__init__(self)

        self.block_color = 3
        self.position = Position(3, 0)
        self.rotations = {
            0: ((0, 0), (1, 0), (2, 0), (3, 0)),
            1: ((0, 0), (0, 1), (0, 2), (0, 3))
        }
        self.current_rotation = 1


