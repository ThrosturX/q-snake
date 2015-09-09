#!/usr/bin/python2
import argparse
import math, random
import threading, time, traceback
from game import Game

global verbose
verbose = 0

class Q_Learn:
    current_state = None
    last_action = None
    epsilon = 0.1
    Q = {} # Q is a dictionary of dictionaries, each subdict represents a state and the rewards for each action
    acts = []

    def __init__(self, goal, actions):
        self.acts = actions

    def get_default_dict(self):
        d = {}
        for a in self.acts:
            d[a] = 0
        return d

    def select(self):
        found = self.Q.get(self.current_state, self.get_default_dict()) # try and get the 'action -> reward' dictionary, otherwise empty dictionary
        self.last_action = self.get_action(found)
        return self.last_action

    def set_state(self, state):
        self.current_state = state

    def get_action(self, d):
        # d is a dictionary containing all available actions and the respective rewards for each state
        if random.random() < self.epsilon: # encourage exploration
            best = [i for i in range(len(self.acts)) if d.get(self.acts[i], 0) == max([d.get(act, 0) for act in self.acts])]
#           if args.verbose >= 2:
#               print 'exploring {0}'.format([self.acts[x] for x in best])
            return random.choice(self.acts)
        return self.simple_selection(d)

    def simple_selection(self, d):
        max_reward = min([d.get(act, 0) for act in self.acts]) 
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
        selection = random.choice(best_actions)
        if verbose >= 2:
            print 'selected {0} from values {1}'.format(selection, [d.get(act, 0) for act in self.acts])
        return selection

    def reward_of(self, act):
        d = self.Q.get(self.current_state, {})
        return d.get(act, 0)

    def reward(self, value):
        row = self.Q.get(self.current_state, self.get_default_dict())
        current_reward = row.get(self.last_action, 0)
        row[self.last_action] = self.calculate_reward(current_reward, value, row)
        self.Q[self.current_state] = row
        if value > 5 or value < 0:
            if verbose:
                print '{0} received a reward of {1} after action {2}'.format(self, value, self.last_action)
#               raw_input('continue?')
            if verbose >= 3:
                pprint(self.Q)

    def calculate_reward(self, old, reward, d):
        optimal_estimate = self.reward_of(self.simple_selection(d))
        learned_value = reward + self.epsilon * optimal_estimate
        learning_rate = 1 - self.epsilon
        reward = old + learning_rate * (learned_value - old)
        return reward

class Agent:
    game = None
    t = None
    score = 0
    learners = []
    prev_state = None
    prev_action = None
    pos = (0, 0)

    def __init__(self, game):
        self.game = game

    def add_learner(self, learner):
        self.learners.append(learner)

    def assess_environment(self):
        bounds = self.game.get_size()
        items = self.game.get_items()
        snake = items['snake']
        apple = items['apple']['x'], items['apple']['y']
        head = snake[0]['x'], snake[0]['y']
        dx = head[0] - apple[0]
        dy = head[1] - apple[1]
        angle = math.atan2(dy, dx) * 1 / math.pi
        eat = int(angle * 2) # return an approximation of the direction to the apple (for now)
#       print eat
        du = head[1]                # distance to top
        dd = bounds[1] - head[1]    # distance to bottom
        dl = head[0]                # distance to left
        dr = bounds[0] - head[0]    # distance to right
        walls = (min(2,du), min(2,dd), min(2,dl), min(2,dr))
#       print 'E,W: ({0}, {1})'.format(eat, walls)
        mindist = min(walls)
        return eat, walls, mindist

    def check_reward(self): # can (AND SHOULD) be improved if game is changed
        if self.game.score > self.score:
            self.score = self.game.score
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

    def lowlevelaction(self, act):
        current_direction = self.game.direction
        dirs = ['up', 'right', 'down', 'left']
        index = (dirs.index(current_direction) + 2) % 4
#       print '{0}, currently going {1}'.format(act, current_direction)
        if act == dirs[index]:
            act = random.choice(['left', 'right'])
#           print 'turning', act
            self.action(act)
        else:
#           print 'sending', act
            self.game.post(act)

    def train(self, learner, index):
        self.t = threading.Thread(target=self.game.start)
        self.t.daemon = True
        self.t.start()
        while self.game.running:
            foo = self.assess_environment()
            knowledge = foo[index]
            learner.set_state(knowledge)
            act = learner.select()
            self.lowlevelaction(act)
            reward = self.check_reward()
            if reward:
                learner.reward(reward)
            while self.pos == self.game.get_head():
                time.sleep(0.001)
            self.pos = self.game.get_head()
        learner.reward(-250) # for losing
        self.reset_game()

    def play(self):
        # start the game
        learner = Q_Learn(0, ['up', 'down', 'left', 'right'])
        survivor = Q_Learn(0, ['up', 'down', 'left', 'right'])
#       decider = Q_Learn(0, ['forward', 'left', 'right'])
        decider = Q_Learn(0, ['eat', 'survive'])    # TODO: logic
        i = 1
        self.game.suppressed = True
        for x in xrange(100):
            print 'training session', x
            self.train(learner, 0)
        for x in xrange(100):
            print 'training session', 100 + x
            self.train(survivor, 1)

        self.game.suppressed = False
        while True:
            print 'Run number', i
            i = i + 1
            self.t = threading.Thread(target=self.game.start)
            self.t.daemon = True
            self.t.start()
            while self.game.running:
                apple, obstacles, distance = self.assess_environment()   # use this to calculate the state... # TODO
#               print apple, obstacles, distance
                learner.set_state(apple)            # set the current state 
                survivor.set_state(obstacles) 
                eat = learner.select()              # select the 'optimal' action
#               self.lowlevelaction(eat)
                live = survivor.select()
                decider.set_state((apple, distance))
                act = decider.select()
#               self.lowlevelaction(live)
                if act == 'eat':
                    self.lowlevelaction(eat)
                elif act == 'survive':
                    self.lowlevelaction(live)
                else:
                    raise Exception("Invalid action: {0}".format(act))
                reward = self.check_reward()        # check if there's a reward
                if reward:
#                   survivor.reward(reward)
                    if act == 'eat':
                        learner.reward(reward)
                    decider.reward(reward)
                elif act == 'survive':
                    survivor.reward(distance)
                while self.pos == self.game.get_head():
                    time.sleep(0.01)
                self.pos = self.game.get_head()
            learner.reward(-50) # we lost!
            survivor.reward(-150)
            decider.reward(-50)
            if verbose:
                print 'got score', self.score
            time.sleep(0.1)
            self.reset_game()
    
    def reset_game(self):
        self.score = 0
        self.game.reset()

def main():
    global args
    game = Game()
    game.set_size(6, 6)
    game.set_discrete(True)
#   game.suppressed = True
    a = Agent(game)
    a.play()
    print 'done'
    exit()


if __name__ == '__main__':
    import sys
    parser = argparse.ArgumentParser(description='snake-playing Q-learning agent')
    parser.add_argument('-v', '--verbose', action='count', help='increase output verbosity')
    args = parser.parse_args()
    verbose = args.verbose
    if args.verbose >= 3:
        from pprint import pprint
    try:
        main()
    except Exception, e:
        print traceback.print_exc()
        print e
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)

