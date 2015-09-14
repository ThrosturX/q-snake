#!/usr/bin/python2
import argparse
import operator
from bokeh.plotting import figure, output_file, save
from bokeh.models import LinearAxis, Range1d

def get_y(fn):
    data = []
    with open(fn, 'r') as f:
        pols = []
        avgs = []
        high = []
        for line in f.readlines():
            elements = line.strip().split(',')
            pols.append(elements[0])
            avgs.append(elements[1])
            high.append(elements[2])
            
        data.append(pols)
        data.append(avgs)
        data.append(high)
    return data

def main():
    fname = args.name
    name = args.name.strip('.txt')
    yname = args.yname
    y = get_y(fname)
    x = range(len(y[0]))
    x = [(1+r) * 10 for r in x]
    output_file(name+'.html', title=name)
    p = figure(title=name, x_axis_label='games played', y_axis_label='score') 
    p.extra_y_ranges = {'score': Range1d(start=0, end=100), 'avg': Range1d(start=0, end=max(map(float,y[2]))) }
    p.line(x, map(float, y[0]), legend="policy", line_width=2, y_range_name='score', line_color='red')
    p.line(x, map(float, y[1]), legend="average", line_width=2, y_range_name='avg', line_color='orange')
    p.line(x, map(float, y[2]), legend="high", line_width=2, y_range_name='avg')
    p.add_layout(LinearAxis(y_range_name='avg'), 'right')
    save(p)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='snake q-learner evaluator')
    parser.add_argument('name', help='input file name')
    parser.add_argument('-a', '--yname', default='y-axis', help='y-axis name')
    args = parser.parse_args()
    try:
        main()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except Exception as e:
        print 'error', e
        raise

