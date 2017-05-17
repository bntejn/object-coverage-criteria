#!/usr/bin/env python

'''

first: Feb 8 2017
last : Feb 8 2017

@author Taejoon Byun <taejoon@umn.edu>
'''

import sys, glob

from ObjectBranchCoverage import ObjectBranchCoverage

def main():
    if len(sys.argv) != 4:
        print 'Invalid number of arguments (expected 3)'
        print 'Usage: $ %s <bin> <pincov_dir> <flist>' % sys.argv[0]
        sys.exit()

    binary = sys.argv[1]
    pincov_dir = sys.argv[2]
    flist = sys.argv[3]

    obc = ObjectBranchCoverage(binary, flist)
    for cov in glob.glob(pincov_dir + '/*.pincov'):
        obc.update_cov_from_pincov(cov)
    obc.calc_coverage()
    print obc

if __name__ == '__main__':
    main()

