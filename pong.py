import math
import random
import pygame
from pygame.locals import *

class Pong:

    scores = [0, 0]
    moved = False
    discrete = False
    paddles = [None, None]

    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Pong')
        self.paddles[0] = self.Paddle('left')
        self.paddles[1] = self.Paddle('right')
        self.clock = pygame.time.Clock()
        self.serve()

    def serve(self):
        angle = random.random() - 0.45
        speed = random.choice([9, -9])
        self.ball = self.Ball((angle, speed), pygame.Rect(320, 240, 9, 9))

    def play(self):
        while self.moved or not self.discrete:
            self.moved = False
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_a:
                        self.paddles[0].moveup()
                    elif event.key == K_z:
                        self.paddles[0].movedown()
                    elif event.key == K_UP:
                        self.paddles[1].moveup()
                    elif event.key == K_DOWN:
                        self.paddles[1].movedown()
                elif event.type == KEYUP:
                    if event.key == K_a or event.key == K_z:
                        self.paddles[0].movepos = [0,0]
                        self.paddles[0].state = 'still'
                    elif event.key == K_UP or event.key == K_DOWN:
                        self.paddles[1].movepos = [0,0]
                        self.paddles[1].state = 'still'
            for paddle in self.paddles:
                paddle.update()
            winner = self.ball.update(self.paddles)
            if winner:
                self.scores[winner-1] += 1
                print 'Score: {0}, {1}'.format(*self.scores)
                self.serve()
            self.render()

    def render(self):
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        self.display.fill(BLACK)
        pygame.draw.rect(self.display, WHITE, self.ball.rect)
        for paddle in self.paddles:
            pygame.draw.rect(self.display, WHITE, paddle)
        pygame.display.update()


    class Ball:

        def __init__(self, vector, rect):
            self.vector = vector
            self.hit = 0
            self.rect = rect
            self.area = pygame.display.get_surface().get_rect()

        def update(self, paddles):
            newpos = self.calcnewpos(self.rect, self.vector)
            self.rect = newpos
            (angle, z) = self.vector
            if not self.area.contains(newpos):
                tl = not self.area.collidepoint(newpos.topleft)
                tr = not self.area.collidepoint(newpos.topright)
                bl = not self.area.collidepoint(newpos.bottomleft)
                br = not self.area.collidepoint(newpos.bottomright)
                if (tr and tl) or (br and bl):
                    angle = -angle
                if (tl and bl):
                    return 2
                    angle = math.pi - angle
                elif (tr and br):
                    return 1
                    angle = math.pi - angle
            else:
                for paddle in paddles:
                    paddle.rect.inflate(-3, -3)
                    if self.rect.colliderect(paddle) == 1 and not self.hit:
                        angle = math.pi - angle
                        angle += random.choice([random.random() / 0.9, -random.random() / 0.9])
                        self.hit = not self.hit
                    elif self.hit:
                        self.hit = not self.hit
            self.vector = (angle, z)

        def calcnewpos(self, rect, vector):
            (angle, z) = vector
            (dx, dy) = (z*math.cos(angle), z*math.sin(angle))
            return rect.move(dx, dy)

    class Paddle:

        def __init__(self, side):
            self.area = pygame.display.get_surface().get_rect()
            self.side = side
            self.rect = pygame.Rect(5, 5, 10, 50)
            self.speed = 10
            self.init()

        def init(self):
            self.state = 'still'
            self.movepos = [0,0]
            if self.side == 'left':
                self.rect.midleft = self.area.midleft
            elif self.side == 'right':
                self.rect.midright = self.area.midright

        def update(self):
            newpos = self.rect.move(self.movepos)
            if self.area.contains(newpos):
                self.rect = newpos
            pygame.event.pump()

        def moveup(self):
            self.movepos[1] = self.movepos[1] - self.speed
            self.state = 'moveup'

        def movedown(self):
            self.movepos[1] = self.movepos[1] + self.speed
            self.state = 'movedown'

if __name__ == '__main__':
    p = Pong()
    p.play()
