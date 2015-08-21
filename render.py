import pygame
#rom pygame.locals import *

# setup code, constants
WIN_WIDTH = 640
WIN_HEIGHT = 480
CELL_SIZE = 20
assert WIN_WIDTH  % CELL_SIZE == 0, "Window width must be a multiple of cell size."
assert WIN_HEIGHT % CELL_SIZE == 0, "Window height must be a multiple of cell size."
CELL_WIDTH  = int(WIN_WIDTH  / CELL_SIZE)
CELL_HEIGHT = int(WIN_HEIGHT / CELL_SIZE)
# color constants
# COLOR       R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK


# TODO: pass things into renderer and renderer figures it out for us
class Renderer:
    display = None
    basic_font = None
    _cc = None
    _ww = 320
    _wh = 240
    
    def __init__(self, ww, wh, cc):
        pygame.init()
        self.display = pygame.display.set_mode((ww, wh))
        self.basic_font = pygame.font.Font('freesansbold.ttf', 18)
        pygame.display.set_caption('Snake Game Clone')
        self._cc = cc
        self._ww = ww
        self._wh = wh

    def render(self, items):
        self.display.fill(BGCOLOR)
        self.draw_grid()
        self.draw_apple(items['apple']) # draw the apple first so
        self.draw_snake(items['snake']) # snake can overwrite it
        self.draw_score(len(items['snake']) - 3) # draw the score
        pygame.display.update()

    def draw_apple(self, apple):
        c = self._cc
        x = apple['x'] * c
        y = apple['y'] * c
        apple_rect = pygame.Rect(x, y, c, c)
        pygame.draw.rect(self.display, RED, apple_rect)

    def draw_snake(self, coords):
        c = self._cc
        for coord in coords:
            x = coord['x'] * c
            y = coord['y'] * c
            worm_segment_rect = pygame.Rect(x, y, c, c)
            worm_segment_fill = pygame.Rect(x + 4, y + 4, c - 8, c - 8)

            pygame.draw.rect(self.display, DARKGREEN, worm_segment_rect)
            pygame.draw.rect(self.display,     GREEN, worm_segment_rect)

    def draw_score(self, score):
        surf = self.basic_font.render('Score: %s' % (score), True, WHITE)
        rect = surf.get_rect()
        rect.topleft = (self._ww - 120, 10)
        self.display.blit(surf, rect)

    def draw_grid(self):
        cell_size = self._cc
        for x in range(0, self._ww, cell_size): # draw vertical lines
            pygame.draw.line(self.display, DARKGRAY, (x, 0), (x, self._wh))
        for y in range(0, self._ww, cell_size): # draw vertical lines
            pygame.draw.line(self.display, DARKGRAY, (0, y), (self._ww, y))
