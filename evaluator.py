import argparse
import math, os, sys, traceback
import agent, threading, time
from game import Game
from pprint import pprint

APPLE_OPTIMAL = {
    0 : {'left': 1},
    1 : {'up': 1}   ,
    2 : {'right': 1} ,
    -1: {'down': 1}
}

def normalize(strategy):
    # d is a dictionary of dictionaries
    d = strategy.copy()
    for state in d:
        factor = 1.0/sum(d[state].itervalues())
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

def evaluate(player, max_runs=5000):
    actions = ['up', 'down', 'left', 'right']
    # game set up
    player.game.suppressed = True
    i = 0
    outfile = 'default.txt'
    if args.outfile:
        outfile = args.outfile
    if os.path.exists(outfile):
        c = raw_input('WARNING: output file {0} already exists, continue?\n'.format(outfile)).lower()
        if not c.startswith('y'):
            sys.exit(0)
    with open(outfile, 'w') as f:
        while i < max_runs:
            i = i + 1
            player.t = threading.Thread(target=player.game.start)
            player.t.daemon = True
            player.t.start()
            # learner set up
            apple_seeker = agent.Q_Learn(0, actions)
            while player.game.running:
                apple, walls, min_d = player.assess_environment()
                apple_seeker.set_state(apple)
                seek = apple_seeker.select()
                player.lowlevelaction(seek)
                # block until the action succeeds
                while player.pos == player.game.get_head():
                    time.sleep(0.01)
                # the action succeeded
                player.pos = player.game.get_head()
                reward = player.check_reward()
                if reward:
                    apple_seeker.reward(reward)
            current = calc_score(apple_seeker, APPLE_OPTIMAL)
            if current > 95.0:
                print 'policy with score {1} found in {0} iterations'.format(i, current)
                pprint(normalize(apple_seeker.Q))
                pprint(APPLE_OPTIMAL)
                break
            time.sleep(0.02)
            player.reset_game()
            if i % 10 == 0:
                pprint(normalize(apple_seeker.Q))
                pprint(APPLE_OPTIMAL)
                print 'Policy has score of {0}/{1}'.format(calc_score(apple_seeker, APPLE_OPTIMAL), 100)
                f.write(str(current) + '\n')


def main():
    global args
    game = Game()
    game.set_size(6, 6)
    game.set_discrete(True)
    player = agent.Agent(game)
    evaluate(player)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='snake q-learner evaluator')
    parser.add_argument('-a', '--apple', action='store_true', help='learn to seek the apple')
    parser.add_argument('-o', '--outfile', help='where to store the results')
    parser.add_argument('-v', '--verbose', action='count', help='increase output verbosity')
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
