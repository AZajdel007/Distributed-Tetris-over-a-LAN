import pygame as pg
import colors

class Grid:
    def __init__(self):
        self.rows = 20
        self.cols = 10
        self.grid = [[0 for col in range(self.cols)] for row in range(self.rows)]
        self.field_size = 30

    def draw(self, screen):
        for row in range(self.rows):
            for col in range(self.cols):
                field = self.grid[row][col]
                field_rect = pg.Rect(col*self.field_size, row*self.field_size, self.field_size-1, self.field_size-1)
                pg.draw.rect(screen, colors.color[field], field_rect)
