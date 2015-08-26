#!/usr/bin/python2
import math, random
import threading, time
from game import Game

class Q_Learn:
    current_state = None
    last_action = None
    epsilon = 0.1
    Q = {} # Q is a dictionary of dictionaries, each subdict represents a state and the rewards for each action
    acts = []
    
    def __init__(self, goal, actions):
        self.acts = actions

    def select(self):
        found = self.Q.get(self.current_state, {}) # try and get the 'action -> reward' dictionary, otherwise empty dictionary
        self.last_action = self.get_action(found)
        return self.last_action

    def get_action(self, d):
        # d is a dictionary containing all available actions and the respective rewards for each state
        if random.random() < self.epsilon: # encourage exploration
            return random.choice(self.acts)
        max_reward = -2
        best_actions = []
        # look at Q to find the preferred actions
        for act in self.acts:
            reward = d.get(act, 0)
            if reward > max_reward:
                max_reward = reward
                best_actions = [act]
            elif reward == max_reward:
                best_actions.append(act)
        # select the best one, use random in case there are many
        return random.choice(best_actions)

    def reward(self, value):
        row = self.Q.get(self.current_state, {})
        current_reward = row.get(self.last_action, 0)
        row[self.last_action] = calculate_reward(current_reward, value)

    def calculate_reward(self, old, reward):
        # TODO: do this
        return 0

class Agent:
    game = None
    t = None
    score = 0
    Q = []
    prev_state = None
    prev_action = None

    def __init__(self, game):
        game.set_discrete(True)
        self.game = game
        self.t = threading.Thread(target=game.start)

    def assess_environment(self):
        items = self.game.get_items()
        snake = items['snake']
        apple = items['apple']['x'], items['apple']['y']
        head = snake[0]['x'], snake[0]['y']
        dx = head[0] - apple[0]
        dy = head[1] - apple[1]
        angle = math.atan2(dy, dx) * 4 / math.pi
        print 'dx: {0}, dy: {1}; angle: {2}'.format(dx, dy, angle)
        # TODO

    def check_reward(self): # can (AND SHOULD) be improved if game is changed
        if game.score > self.score:
            self.score = game.score
            return 100
        return 0
        
    def action(self, act):
        current_direction = self.game.direction
        dirs = ['up', 'right', 'down', 'left']
        # action is in {forward, left, rigtht}
        if act == 'forward':
            self.game.post(current_direction)
        elif act == 'left':
            index = (dirs.index(current_direction) + 3) % 4
            self.game.post(dirs[index])
        elif act == 'right':
            index = (dirs.index(current_direction) + 1) % 4
            self.game.post(dirs[index])

    def play(self):
        # start the game
        self.t.start()
        learner = Q_Learn(0, ['forward', 'left', 'right'])
        while self.game.running:
            self.assess_environment() # use this to calculate the state... # TODO
            act = learner.select()  # select the 'optimal' action
            self.action(act)        # play the selected action
            reward = self.check_reward() # check if there's a reward
            if reward:
                learner.reward(reward)
            time.sleep(0.1)

def main():
    g = Game()
    g.set_size(32, 24)
    a = Agent(g)
    a.play()
    print 'done'
    exit()


if __name__ == '__main__':
    import sys
    try:
        main()
    except Exception, e:
        print e
        sys.exit(1)
    except KeyboardInterrupt:
        sys._exit(0)

