import argparse
import math, os, sys, traceback
import agent, threading, time
from game import Game
from pprint import pprint

APPLE_OPTIMAL = {
    0 : {'left': 1}  ,
    1 : {'up': 1}    ,
    2 : {'right': 1} ,
    -1: {'down': 1}
}

WALL_OPTIMAL = {
    (-1, -2): {'down':  0.5, 'left' : 0.25, 'right': 0.25},
    (-2, -1): {'right': 0.5, 'up'   : 0.25, 'down' : 0.25},
    (-1, -1): {'down': 0.5 , 'right': 0.5},
    (1, 2):   {'up':    0.5, 'left' : 0.25, 'right': 0.25},
    (2, 1):   {'left':  0.5, 'up'   : 0.25, 'down' : 0.25},
    (1, 1):   {'up': 0.5   , 'left' : 0.5}
}

META_OPTIMAL = {
    1: {'live': 1},
    2: {'seek': 1}
}

def normalize(strategy):
    # d is a dictionary of dictionaries
    d = strategy.copy()
    smallest = 0
    for state in d:
        for val in d[state]:
            if d[state][val] < smallest:
                smallest = d[state][val]
    for state in d:
        d[state] = { k: v + abs(smallest) for k,v in d[state].iteritems() }
    for state in d:
        denominator = sum(d[state].itervalues())
        if denominator == 0:
            denominator = 1
        factor = 1.0/denominator
        d[state] = { k: v*factor for k, v in d[state].iteritems() }
    return d

def calc_score(learner, optimal):
    Q = normalize(learner.Q)
    score = 0.0
    top = 0.0
    for state in optimal:
        actions = optimal.get(state, {}).copy()
        actions.update(Q.get(state,{}))
        for act in actions:
            target = optimal.get(state, {}).get(act, 0)
            found = Q.get(state, {}).get(act, 0)
            add = (1.0 - abs(target - float(found)))
            score += add
            top += 1
    return score * 100 / (max(1, top))

def train(player, learner, config, max_steps=200):
    i = 0
    # make sure each training session is limited in length
    if args.max_training_steps:
        max_steps = args.max_training_steps
    while i < max_steps:
        t_start = time.time()
        time_limit = 5
        i = i + 1
        player.t = threading.Thread(target=player.game.start)
        player.t.daemon = True
        player.t.start()
        seconds_passed = time.time() - t_start
        while player.game.running and seconds_passed < time_limit:
            apple, walls, min_d = player.assess_environment()
            if min_d == 0 and player.game.running:
                time.sleep(0.02)
                player.game.running = False
                continue
            if config == 0:
                learner.set_state(apple)
            elif config == 1:
                learner.set_state(walls)
            player.lowlevelaction(learner.select())
            while player.pos == player.game.get_head():
                time.sleep(0.01)
            # the action succeeded
            player.pos = player.game.get_head()
            reward = player.check_reward()
            if reward and config == 0:
                learner.reward(reward)
            seconds_passed = time.time() - t_start
        if config == 1 and seconds_passed > time_limit:
            learner.reward(-1000)
        time.sleep(0.02)
        player.reset_game()

def evaluate(player, max_runs=5000):
    actions = ['up', 'down', 'left', 'right']
    # game set up
#   player.game.suppressed = True
    i = 0
    outfile = 'default.txt'
    if args.outfile:
        outfile = args.outfile
    if os.path.exists(outfile):
        c = raw_input('WARNING: output file {0} already exists, continue?\n'.format(outfile)).lower()
        if not c.startswith('y'):
            sys.exit(0)
    with open(outfile, 'w') as f:
        high_score = 0
        last_scores = []
        # initialize the learners
        apple_seeker = agent.Q_Learn(0, actions)
        wall_avoider = agent.Q_Learn(0, actions)
        meta_learner = agent.Q_Learn(0, ['live', 'seek'])
        if args.meta_learner:
            train(player, apple_seeker, 0)
            train(player, wall_avoider, 1)
            apple_seeker.epsilon = 0     # disable exploration
            wall_avoider.epsilon = 0
        while i < max_runs - 1:
            t_start = time.time()
            time_limit = 60
            seconds_passed = 0
            i = i + 1
            player.t = threading.Thread(target=player.game.start)
            player.t.daemon = True
            player.t.start()
            # learner set up
            while player.game.running and seconds_passed < time_limit:
                apple, walls, min_d = player.assess_environment()
                if min_d == 0 and player.game.running: # don't set the learner state if we lost
                    time.sleep(0.02)
                    player.game.running = False
                    continue
                apple_seeker.set_state(apple)
                wall_avoider.set_state(walls)
                seek = apple_seeker.select()
                live = wall_avoider.select()
                if seek == 0 or live == 0:
                    raise Exception('zero error')
                meta_learner.set_state(min_d) # hope that the meta learner learns that the survivor is better
                if args.meta_learner:
                    choice = meta_learner.select()
                    if choice == 'live':
                        player.lowlevelaction(live)
                    elif choice == 'seek':
                        player.lowlevelaction(seek)
                    else:
                        raise Exception('unknown action in meta learner')
                elif args.apple:
                    player.lowlevelaction(seek)
                elif args.survivor:
                    player.lowlevelaction(live)
                else:
                    raise Exception('unknown learner')
                # block until the action succeeds
                while player.pos == player.game.get_head():
                    time.sleep(0.01)
                # the action succeeded
                player.pos = player.game.get_head()
                reward = player.check_reward()
                if reward and args.apple:
                    apple_seeker.reward(reward)
                if reward and args.meta_learner:
                    if choice == 'seek':
                        apple_seeker.reward(reward)
                    meta_learner.reward(1)
                lost = True
                seconds_passed = time.time() - t_start
            if seconds_passed > time_limit:
                lost = False
            # we lost or it was reset
            score = player.game.score
            high_score = max(score, high_score)
            N = 10
            last_scores.append(score)
            avg_scores = float(sum(last_scores[-N:]))/N
            if args.meta_learner and lost:
                meta_learner.reward(-1000)
                if lost and choice == 'live':
                    wall_avoider.reward(-2500)
                optimal = META_OPTIMAL
                learner = meta_learner
            elif args.survivor:
                if lost:
                    wall_avoider.reward(-2500)
                optimal = WALL_OPTIMAL
                learner = wall_avoider
            elif args.apple:
                if lost:
                    learner.reward(-1) # small negative reward because 'went wrong way'
                optimal = APPLE_OPTIMAL
                learner = apple_seeker
            current = calc_score(learner, optimal)
            if current > 95.0 and args.break_on_optimal:
                print 'policy with score {1} found in {0} iterations'.format(i, current)
                pprint(normalize(learner.Q))
                pprint(optimal)
                break
            time.sleep(0.02)
            player.reset_game()
            if i % 10 == 0:
#               pprint(learner.Q)
                pprint(normalize(learner.Q))
                pprint(optimal)
                print 'Policy has score of {0}. average score: {2}. Iteration {1}, high score {3}'.format(calc_score(learner, optimal), i, avg_scores, high_score)
                f.write(str(current) + ',' + str(avg_scores) + ',' + str(high_score) + '\n')


def main():
    global args
    game = Game()
    game.set_size(6, 6)
    game.set_discrete(True)
    player = agent.Agent(game)
    evaluate(player, max_runs=args.max_evaluations)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='snake q-learner evaluator')
    parser.add_argument('-a', '--apple', action='store_true', help='learn to seek the apple')
    parser.add_argument('-s', '--survivor', action='store_true', help='learn to survive')
    parser.add_argument('-c', '--meta_learner', action='store_true', help='test the meta learner')
    parser.add_argument('-o', '--outfile', help='where to store the results')
    parser.add_argument('-m', '--max_evaluations', type=int, default=5000, help='how many evaluations are the maximum')
    parser.add_argument('-t', '--max_training_steps', type=int, default=200, help='maximum number of training steps')
    parser.add_argument('-v', '--verbose', action='count', help='increase output verbosity')
    parser.add_argument('--break_on_optimal', action='store_true', help='stop the simulation at a good policy')
    args = parser.parse_args()
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except SystemExit:
        sys.exit(0)
    except Exception, e:
        print traceback.print_exc()
        print e
        sys.exit(1)
