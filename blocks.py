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
        self.is_placed = False

    """Rysowanie aktualnego spadającego bloku na ekranie"""
    def draw(self, screen):
        for tile in self.rotations[self.current_rotation]:
            if self.position.column + tile[0] >= 0 and self.position.row + tile[1] >= 0:
                tile_rect = pygame.Rect((self.position.column+tile[0])*self.tile_size, (self.position.row+tile[1])*self.tile_size, self.tile_size-1, self.tile_size-1)
                pg.draw.rect(screen, colors.color[self.block_color], tile_rect)

    #def draw(self, screen):
    #    for tile in self.rotations[self.current_rotation]:
    #        tile_rect = pygame.Rect((self.position.column+tile[0])*self.tile_size, (self.position.row+tile[1])*self.tile_size, self.tile_size-1, self.tile_size-1)
    #        pg.draw.rect(screen, colors.color[self.block_color], tile_rect)

    """Sprawdzenie czy przy próbie przesunięcia bloku w prawo / lewo występuje kolizja ze ścianą"""
    def check_collision_with_wall(self, movement, grid):
        for tile in self.rotations[self.current_rotation]: # zwraca true jeśli jest kolizja
            if (self.position.column + tile[0] + movement) >= 10 or (self.position.column + tile[0] + movement) < 0 or grid.grid[self.position.row+tile[1]][self.position.column+tile[0]+movement] != 0:
                return True
        return False

    """Sprawdzenie czy przy próbie obrotu klocka kolizja ze ścianą lub innym postawionym już klockiem"""
    def check_rotate_collision(self, grid):
        for tile in self.rotations[(self.current_rotation + 1) % len(self.rotations)]:
            if self.position.row+tile[1] < 0:
                continue
            if self.position.row+tile[1] >= 20 or self.position.column+tile[0] >= 10 or self.position.column+tile[0] < 0 or grid.grid[self.position.row+tile[1]][self.position.column+tile[0]] != 0:
                return True
        return False

    # WERSJA DZIAŁAJĄCA ALE BEZ MOŻLIWOŚCI ROTACJI BLOKÓW NA SAMEJ GÓRZE
    #def check_rotate_collision(self, grid):
    #    for tile in self.rotations[(self.current_rotation + 1) % len(self.rotations)]:
    #        if self.position.row+tile[1] >= 20 or self.position.row+tile[1] < 0 or self.position.column+tile[0] >= 10 or self.position.column+tile[0] < 0 or grid.grid[self.position.row+tile[1]][self.position.column+tile[0]] != 0:
    #            return True
    #    return False

    """Sprawdzenie czy pod spadającym klockiem są już inne postawione wcześniej klocki"""
    def check_collision_under(self, grid):
        for tile in self.rotations[self.current_rotation]:
            if self.position.row+tile[1]+1 >= 20 or grid.grid[self.position.row + tile[1]+1][self.position.column + tile[0]] != 0:
                return True
        return False

    # WERSJA DZIAŁAJĄCA ALE BEZ MOŻLIWOŚCI ROTACJI BLOKÓW NA SAMEJ GÓRZE
    #def check_collision_under(self, grid):
    #    for tile in self.rotations[self.current_rotation]:
    #        if self.position.row+tile[1]+1 >= 20 or self.position.row+tile[1]+1 < 0 or grid.grid[self.position.row + tile[1]+1][self.position.column + tile[0]] != 0:
    #            return True
    #    return False

    """Przesunięcie spadającego klocka w lewo/prawo (ze sprawdzeniem przed czy nie ma żadnej kolizji)"""
    def move_x(self, movement, grid):
        if not self.check_collision_with_wall(movement, grid):
            self.position.column = self.position.column + movement

    """Rotacja spadającego klocka (ze sprawdzeniem przed czy nie ma żadnej kolizji ze ścianą / innym postawionym już klockiem)"""
    def rotate(self, grid):
        if not self.check_rotate_collision(grid):
            self.current_rotation = (self.current_rotation + 1) % len(self.rotations)

    """Przesunięcie spadającego klocka w dół (ze sprawdzeniem przed czy nie ma żadnej kolizji)"""
    def move_down(self, grid):
        if not self.check_collision_under(grid):
            self.position.row = self.position.row + 1

    """Zrzucenie spadającego klocka na maxa w dół (ze sprawdzeniem kolizji)"""
    def drop(self, grid):
        while not self.check_collision_under(grid):
            self.move_down(grid)

    """Położenie spadającego klocka na planszy na stałe"""
    def put_on_grid(self, grid):
        for tile in self.rotations[self.current_rotation]:
            grid.grid[self.position.row+tile[1]][self.position.column + tile[0]] = self.block_color
            self.is_placed = True



# PO I PRZED ROTACJI SPRAWDZIĆ CZY BLOK JUŻ NIE SPADŁ

"""RODZAJE KLOCKÓW:
        self.block_color - KOLOR KLOCKA 
        self.position = POZYCJA STARTOWA KLOCKA
        self.rotations = ROTACJE KLOCKA
        self.current_rotation = ROTACJA STARTOWA KLOCKA"""

class IBlock(Block):
    def __init__(self):
        Block.__init__(self)

        self.block_color = 1
        self.position = Position(0, 3)
        self.rotations = {
            0: ((-1, 0), (0, 0), (1, 0), (2, 0)),
            1: ((0, -1), (0, 0), (0, 1), (0, 2))
        }
        self.current_rotation = 0

class OBlock(Block):
    def __init__(self):
        Block.__init__(self)

        self.block_color = 2
        self.position = Position(0, 5)
        self.rotations = {
            0: ((0, 0), (1, 0), (0, 1), (1, 1))
        }
        self.current_rotation = 0

class TBlock(Block):
    def __init__(self):
        Block.__init__(self)

        self.block_color = 3
        self.position = Position(1, 4)
        self.rotations = {
            0: ((-1, 0), (0, 0), (1, 0), (0, -1)),
            1: ((0, -1), (0, 0), (0, 1), (-1, 0)),
            2: ((-1, 0), (0, 0), (1, 0), (0, 1)),
            3: ((0, -1), (0, 0), (0, 1), (1, 0)),
        }
        self.current_rotation = 0

class JBlock(Block):
    def __init__(self):
        Block.__init__(self)

        self.block_color = 4
        self.position = Position(0, 4)
        self.rotations = {
            0: ((-1, 0), (0, 0), (1, 0), (1, 1)),
            1: ((0, -1), (0, 0), (0, 1), (-1, 1)),
            2: ((-1, 0), (0, 0), (1, 0), (-1, -1)),
            3: ((0, -1), (0, 0), (0, 1), (1, -1)),
        }
        self.current_rotation = 0

class LBlock(Block):
    def __init__(self):
        Block.__init__(self)

        self.block_color = 5
        self.position = Position(0, 4)
        self.rotations = {
            0: ((-1, 0), (0, 0), (1, 0), (-1, 1)),
            1: ((0, -1), (0, 0), (0, 1), (-1, -1)),
            2: ((-1, 0), (0, 0), (1, 0), (1, -1)),
            3: ((0, -1), (0, 0), (0, 1), (1, 1)),
        }
        self.current_rotation = 0


class SBlock(Block):
    def __init__(self):
        Block.__init__(self)

        self.block_color = 6
        self.position = Position(0, 5)
        self.rotations = {
            0: ((-1, 1), (0, 0), (0, 1), (1, 0)),
            1: ((-1, -1), (0, 0), (-1, 0), (0, 1))
        }
        self.current_rotation = 0

class ZBlock(Block):
    def __init__(self):
        Block.__init__(self)

        self.block_color = 7
        self.position = Position(0, 5)
        self.rotations = {
            0: ((-1, 0), (0, 0), (0, 1), (1, 1)),
            1: ((-1, 1), (0, 0), (-1, 0), (0, -1))
        }
        self.current_rotation = 0

