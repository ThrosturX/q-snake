import pygame
import render
import random

# Constants
FPS = 15
# action constants
UP    = 'up'
DOWN  = 'down'
LEFT  = 'left'
RIGHT = 'right'

_startx = _starty = 12

class Game:
    _fps_clock = None
    _cc = 20
    _cw = 32
    _ch = 24
    running = True
    moved = False
    discrete = False
    direction = RIGHT
    head  =     {'x': _startx,      'y': _starty}
    coords =   [{'x': _startx,      'y': _starty},
                {'x': _startx - 1,  'y': _starty},
                {'x': _startx - 2,  'y': _starty}]

    apple = {'x': 0, 'y': 0}
    score = 0

    # default cell size
    def __init__(self):
        self.apple = self.getRandomLocation()
        self.fps_clock = pygame.time.Clock()

    def set_discrete(self, discrete):
        self.discrete = discrete

    # custom cell size
    def set_size(self, cw, ch):
        self._cw = cw
        self._ch = ch
        self.apple = self.getRandomLocation()

    def post(self, action): 
        if action == UP:
            key = pygame.K_UP
        elif action == DOWN:
            key = pygame.K_DOWN
        elif action == LEFT:
            key = pygame.K_LEFT
        elif action == RIGHT:
            key = pygame.K_RIGHT
        else:
            print 'unknown action... gonna fail'
            
        evt = pygame.event.Event(pygame.KEYDOWN, {'key': key})
        pygame.event.post(evt)

    def get_items(self):
        d = {}
        d['snake'] = self.coords
        d['apple'] = self.apple
        return d

    def start(self):
        r = render.Renderer(self._cw * self._cc, self._ch * self._cc, self._cc)
        while self.running:
            # process all events
            self.process_events()
            # move snake
            self.move_snake()
            self.update_score()
            r.render(self.get_items())
            if self.discrete:
                while not self.moved:
                    self.process_events()
                self.moved = False
            else:
                self.fps_clock.tick(FPS)
        print 'Game over. Score: {0}'.format(self.score)
        pygame.quit()

    def update_score(self):
        if self.coords[0]['x'] == self.apple['x'] and self.coords[0]['y'] == self.apple['y']:
            self.apple = self.getRandomLocation() # place a new apple
            self.score += 1
        else:
            del self.coords[-1] # remove the tail
        if self.coords[0]['x'] <= -1               \
        or self.coords[0]['x'] >= self._cw         \
        or self.coords[0]['y'] <= -1               \
        or self.coords[0]['y'] >= self._ch:
            self.running = False
        for body in self.coords[1:]:
            if body['x'] == self.coords[0]['x'] and body['y'] == self.coords[0]['y']:
                self.running = False

    def move_snake(self):
        direction = self.direction
        if direction == UP:
            dest = {'x': self.coords[0]['x'], 'y': self.coords[0]['y'] - 1}
        elif direction == DOWN:
            dest = {'x': self.coords[0]['x'], 'y': self.coords[0]['y'] + 1}
        elif direction == LEFT:
            dest = {'x': self.coords[0]['x'] - 1, 'y': self.coords[0]['y']}
        elif direction == RIGHT:
            dest = {'x': self.coords[0]['x'] + 1, 'y': self.coords[0]['y']}
        self.coords.insert(0, dest)
             
    def process_events(self):
        for event in pygame.event.get():
            self.process_event(event)

    def process_event(self, event):
        d = None
        if event.type == pygame.QUIT: self.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and self.direction != RIGHT:
                d = LEFT
            elif event.key == pygame.K_RIGHT and self.direction != LEFT:
                d = RIGHT
            elif event.key == pygame.K_UP and self.direction != DOWN:
                d = UP
            elif event.key == pygame.K_DOWN and self.direction != UP:
                d = DOWN
            elif event.key == pygame.K_ESCAPE: self.quit()

            if d:
                self.direction = d
                self.moved = True

    def getRandomLocation(self):
        return {'x': random.randint(0, self._cw - 1), 'y': random.randint(0, self._ch - 1)}

    def quit(self):
        self.running = False

