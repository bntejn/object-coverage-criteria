#!/usr/bin/env python
# ObcSuiteGenerator.py
#
# Randomly generate reduced OBC suites while retaining the same (OBC) coverage
#
# @author: Taejoon Byun <taejoon@umn.edu>
#
# first: Jan 25 2017
# last : Mar 8 2017

# /cov/{version}

import sys, glob, random, copy, re
import pandas as pd
from ObjectBranchCoverage import ObjectBranchCoverage
from UniversalSuite import UniversalSuite

class ObcSuiteGenerator(object):

    def __init__(self, target, covdir, testdir, obc_types):
        self._target = target   # target binary
        self._covdir = covdir   # directory where the coverage log is stored
        self._testdir = testdir # directory where the splitted test cases are
        # list of functions to count
        self._flist = glob.glob(self._covdir+'/../../bin/*.flist')[0]
        # type of OBC instructions to consider when generating
        self._obc_types = obc_types
        # list of the coverage files (for each test case)
        self._cov_files = sorted(glob.glob(self._covdir+'/*tc_*.pincov'))
        self._obc_univ = None    # OBC of a universal test suite
        self._obc_dic = {}
        self._cov_matrix = []    # OBC coverage matrix [test_case by branch]
        # a set of obligations that are satisfiable by the universal suite
        self._sat_obligations = set()

    def read_univ_obc_suite(self):
        self._obc_univ = ObjectBranchCoverage(self._target, self._flist, \
                self._obc_types)
        pincov = glob.glob(self._covdir+'/'+'/*universal.pincov')[0]
        self._obc_univ.update_cov_from_pincov(pincov)
    
    def _construct_coverage_matrix(self):
        ''' Construct a Numpy matrix where the row represents the index of 
        test case and the column represents the branch vector. 
        
        Ex:
                b1_taken    b1_fallen   b2_taken    b2_fallen
        test1   1           0           1           0
        test2   0           1           1           0
        '''
        if len(self._obc_dic) == 0:
            for cf in self._cov_files:
                obc = ObjectBranchCoverage(self._target, self._flist, \
                        self._obc_types)
                obc.update_cov_from_pincov(cf)
                self._obc_dic[cf] = obc
        self._cov_matrix = np.array([obc.get_coverage_vector() \
                for obc in self._obc_dic])

    def _get_satisfiable_obligations(self):
        if len(self._obc_dic) == 0:
            for cf in self._cov_files:
                obc = ObjectBranchCoverage(self._target, self._flist, \
                        self._obc_types)
                obc.update_cov_from_pincov(cf)
                self._obc_dic[cf] = obc
                self._sat_obligations |= obc.get_sat_obligations()

    def select_minimum(self):
        import numpy as np
        ''' Reduce the test suites to a minimum one. The algorithm starts from 
        the original set and removes one by one, randomly, while maintaining 
        the same coverage. This algorithm ensures a *minimum* reduction since 
        it goes through all the test cases and discard each if it doesn't 
        contribute to the coverage.
        :returns: the list of `self._cov_files` indices
        '''
        self._construct_coverage_matrix()
        indices = range(0, len(self._cov_files))
        random.shuffle(indices)
        del_list = []    # indices to delete
        original_vector_flat = np.logical_or.reduce(self._cov_matrix)
        for ind in indices:
            new_del_list = list(del_list) + [ind]
            removed = np.delete(self._cov_matrix, new_del_list, axis=0)
            # remove if it doesn't contribute to the coverage
            if np.array_equal(np.logical_or.reduce(removed), original_vector_flat):
                del_list = new_del_list
        return set(indices) - set(del_list)

    def select_minimal(self):
        ''' Reduce the test suite to a minimal one. The algorithm starts from 
        an empty set and gathers any test case that contributes to the coverage.
        It does not ensure a minimum suite.
        '''
        def verify(selection):
            selected_oblg = set()
            for sel in selection:
                selected_oblg |= self._obc_dic[sel].get_sat_obligations()
            #print '(verify) selected: %d' % len(selected_oblg)
            assert selected_oblg == self._sat_obligations

        selected = []
        self._get_satisfiable_obligations()
        to_satisfy = copy.deepcopy(self._sat_obligations)

        tests = copy.deepcopy(self._cov_files)
        random.shuffle(tests)
        for sel in tests:
            sat_selected = self._obc_dic[sel].get_sat_obligations()
            sat_after = to_satisfy - sat_selected
            if len(sat_after) < len(to_satisfy):
                selected.append(sel)
                to_satisfy = sat_after
            if len(to_satisfy) == 0:
                break;
        # double check
        verify(selected)
        return selected

    def merge_and_write(self, selection, outfile):
        assert isinstance(selection, set)
        suite = UniversalSuite(selection)
        suite.merge_suites()
        suite.write_universal_suite(outfile)

    def write_reduced_suites(self, selections, outfile):
        ''' Write the reduced suite to `outfile`. Each row in the CSV 
        corresponds to a test suite, and each column is the id (int) of the 
        test case in the universal test suite.
        :param selections: two dimensional array of test case ids (int)
        :param outfile: output CSV file name
        '''
        def extract_test_case_id(path):
            return re.findall("tc_(\d+).pincov", path)[0]
        f = open(outfile, 'w')
        row = ''
        for suite in selections:
            for col in suite:
                row += extract_test_case_id(col) + ','
            row = row[:-1] + '\n'
            f.write(row)
            row = ''
        f.close()


def generate_random_minimal(target, covdir, suite_dir, out_fname, \
        n_suite, types):
    gtor = ObcSuiteGenerator(target, covdir, suite_dir, types)
    gtor.read_univ_obc_suite()
    sels = []
    for i in range(0, n_suite):
        sels.append(gtor.select_minimal())
    #print sels
    gtor.write_reduced_suites(sels, out_fname)
    #gtor.merge_and_write(sel, out_fname)


def main():
    if len(sys.argv) != 7:
        print 'Invalid number of arguments (expected 6)'
        print 'Usage: $ %s <target> <cov_dir> <testsuite_dir> <out_filename> \
                <n_test_suite> <types>' % sys.argv[0]
        sys.exit()

    target = sys.argv[1]
    covdir = sys.argv[2]
    suite_dir = sys.argv[3]
    out_fname = sys.argv[4]
    n_suite = int(sys.argv[5])
    types = sys.argv[6]
    generate_random_minimal(\
            target, covdir, suite_dir, out_fname, n_suite, types)

if __name__ == '__main__':
    main()

