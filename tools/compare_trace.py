#!/usr/bin/env python
# compare_trace.py

'''
Compare two output traces and see if they match. Returns true if matches.

first: Jan 23 2017
last : Jan 23 2017

@author Taejoon Byun <taejoon@umn.edu>
'''

import sys, os, glob
import pandas as pd

def compare(oracle, comparee):
    # Re-order the columns from two different files according to the same order
    COLS_TO_KEEP = ['CLEAR_PRESSED', 'COOKING', 'LEFT_DIGIT', 'MIDDLE_DIGIT',
            'OK', 'RIGHT_DIGIT', 'SETUP', 'START_PRESSED', 'STEPS_TO_COOK',
            'SUSPENDED', 'enable']
    same = None
    # collaps blank lines with `skip_blank_lines=True` option;
    # the seperation among test cases is not necessary when comparing them.
    try:
        dfo = pd.read_csv(oracle, skip_blank_lines=True)[COLS_TO_KEEP]
        df = pd.read_csv(comparee, skip_blank_lines=True)[COLS_TO_KEEP]
        same = df.equals(dfo)
    except IOError as e:
        print e
        same = False
    return same

def compare_all(trace_dir, oracle):
    total = 0
    kill = 0
    for trace in glob.glob(trace_dir + "/*_trace.csv"):
        tname = trace.split('/')[-1]
        if not compare(oracle, trace):
            print '  [KILLED] ' + tname + ' ...'
            kill += 1
        total += 1
        print '  [------] ' + tname + ' ...'
    print '[compare_trace.py] %d out of %d mutants killed' % (kill, total)


def main():
    if len(sys.argv) != 3:
        print 'Invalid argument'
        print 'Usage: $ %s <trace_dir> <oracle>' % sys.argv[0]
        sys.exit()
    compare_all(sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    main()

