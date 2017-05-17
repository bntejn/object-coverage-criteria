#!/usr/bin/env python

'''
Post-process a test suite in CSV generated by `lustre.jar` by dropping columns 
unrelated to input and casting the types to double.

first: Dec 17 2016
last : Jan 25 2016

@author Taejoon Byun <taejoon@umn.edu>
'''

import sys
import pandas as pd

def get_new_fname(original_fname):
    tokens = original_fname.split('.')[:-1]
    tokens += ['mod', 'csv']
    return '.'.join(tokens)

def main():
    if len(sys.argv) != 3:
        print 'Invalid argument'
        print 'Usage: $ %s <test_suite.csv> <columns.clist>' % sys.argv[0]
        sys.exit()

    CSV = sys.argv[1]
    COLS = sys.argv[2].split(',')
    df = pd.read_csv(CSV, skip_blank_lines=False)[COLS]
    df = df.convert_objects(convert_numeric=True)   # cast types to double

    # export to a csv file while dropping the header and index column
    new_fname = get_new_fname(CSV)
    print 'saving to ' + new_fname + ' ...'
    df.to_csv(new_fname, index_label=False, index=False, header=False)

if __name__ == '__main__':
    main()

def test_get_new_fname():
    fname = 'mw1.mcdc.csv'
    new_fname = get_new_fname(fname)
    assert new_fname == 'mw1.mcdc.mod.csv'

