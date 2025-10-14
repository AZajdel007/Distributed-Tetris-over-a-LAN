import pygame as pg



def is_cursor_over(rect):
    return rect.collidepoint(pg.mouse.get_pos())

class Button:
    def __init__(self, x, y, width, height, text, color, cursor_over_color, text_color, action):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.cursor_over_color = cursor_over_color
        self.text_color = text_color
        self.action = action
        self.font = pg.font.Font(None, 36)

    def draw(self, screen):
        cursor_over = is_cursor_over(self.rect)
        clicked = pg.mouse.get_pressed()[0]

        if cursor_over:
            pg.draw.rect(screen, self.cursor_over_color, self.rect)
            if clicked:
                self.action()
        else:
            pg.draw.rect(screen, self.color, self.rect)

        text_surf = self.font.render(self.text, True, self.text_color)
        screen.blit(text_surf, (self.rect.x + 15, self.rect.y + 15))
