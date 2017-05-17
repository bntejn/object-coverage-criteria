#!/usr/bin/env python
# measureReducedObc.py

'''
Calculate OBC from reduced test suites

first: Feb 8 2017
last : Mar 14 2017

@author Taejoon Byun <taejoon@umn.edu>
'''

import re, sys, csv, subprocess, glob

from ObjectBranchCoverage import ObjectBranchCoverage
from termcolor import colored

base = ''       # the base name (e.g. obsnop)
root = ''       # the path of the root of output directory
sysdir = ''     # the name of the systems (input) directory
header = '\033[35m[measureReducedObc.py] \033[0m'

def bname(path):
    ''' Basename of a path string '''
    path = path.strip()
    path = path[:-1] if path[-1] is '/' else path
    return path.split('/')[-1]

def measure_each_suite(sysname, binary_name, obc_type, suites):
    ''' Measure average OBC for each suite.
    :param binary_name: the name of an executable program to calculate the 
                        object-based coverage upon
    :param obc_type: the type of object-based criterion to use. It is a 
                     partial permutation of {'J', 'S', 'M', 'L', 'B'}.
    :param suites: A list of suite is a list of string where each string 
                   (line) corresponds to a list of test case IDs in a suite.
    :returns: a list of ``ObjectBranchCoverage`` for each test suite.
    '''
    global root, sysdir

    path_pref = root + '/obc/' + sysdir + '/' + sysname
    binary = path_pref + '/bin/' + binary_name
    flist = glob.glob(path_pref + '/bin/*.flist')[0]
    cov_list = []

    for line in suites:
        # for each test suite in a suite set
        obc = ObjectBranchCoverage(binary, flist, obc_type)
        test_cases = line.strip().split(',')
        for test_case_id in test_cases:
            cov_trace = glob.glob('%s/cov/%s/*_%s.pincov' 
                    % (path_pref, binary_name, test_case_id))[0]
            obc.update_cov_from_pincov(cov_trace)
        cov_list.append(obc)
    return cov_list

def each_criterion(system, criterion):
    ''' for each coverage criterion, measure the OBC and write the result '''
    suites = None
    # each line consists of a list of test cases to include in a suite
    with open(criterion, 'r') as f:
        suites = f.readlines()
    found = re.findall('obc_(o\w+)_(\w+)_tests_reduced\.csv', criterion)[0]
    binary = found[0]
    obc_type = found[1]
#TODO
    cov_list = measure_each_suite(bname(system), binary, obc_type, suites)
    result_file = '%s/results/%s/%s/%s.obc_%s_%s.cov.csv' % \
            (root, sysdir, bname(system), base, binary, obc_type)
    with open(result_file, 'w') as f:
        print header + 'Writing coverage to `' + bname(result_file) + '`'
        f.write('OBC_' + binary + '\n')   # header
        for obc in cov_list:
            obc.calc_coverage()
            f.write(str(obc.get_coverage()) + '\n')

def get_coverage_for_all():
    # for each system / test suite / suite
    global root, sysdir

    for system in glob.glob(root + '/suites/' + sysdir + '/*'):
        # for each system
        for criterion in glob.glob(system + '/reduced/*_reduced.csv'):
            # for each set of suites
            if not 'obc' in bname(criterion):
                continue
            #print '\t`' + bname(criterion) + '`'
            print header + 'For system %s, criterion %s' % \
                    (bname(system), bname(criterion))
            try:
                each_criterion(system, criterion)
            except Exception as e:
                print header + colored('Failure occurred', 'red') + \
                        ' while analyzing `' + colored(bname(criterion), 'red')\
                        + '` in `' + bname(system) + '`'
                print e

def main():
    if len(sys.argv) != 4:
        print 'Invalid number of arguments (expected 3)'
        print 'Usage: $ %s <system_dir> <output_dir> <base>' % sys.argv[0]
        sys.exit()
    global root, sysdir, base
    sysdir = bname(sys.argv[1])
    root = sys.argv[2]
    base = sys.argv[3]
    get_coverage_for_all()


if __name__ == '__main__':
    main()

