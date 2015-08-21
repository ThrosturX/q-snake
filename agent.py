import threading
from game import Game

class Agent:
    game = None
    t = None

    def __init__(self, game):
        self.game = game
        self.t = threading.Thread(target=game.start)

    def play(self):
        # start the game
        self.t.start()
        # play the game
        self.game.post('up')

def main():
    g = Game()
    g.set_size(32, 24)
    a = Agent(g)
    a.play()
    print 'done'

if __name__ == '__main__':
    main()

