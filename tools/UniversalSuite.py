#!/usr/bin/env python
'''
Merge multiple test suites, remove duplicate test cases, and write a merged one
(or either split each test case to a separate file).

first: Jan 24 2017
last : Mar 8 2017

@author Taejoon Byun <taejoon@umn.edu>
'''

import re, sys, os, glob, shutil
import pandas as pd

header = '[UniversalSuite.py] '

class UniversalSuite:


    def __init__(self, suites):
        assert isinstance(suites, list)
        ''' File name of the test suites to merge '''
        self._suites = suites
        ''' When merging multiple suites that have different number of columns,
        # keep only the shortest header and discard any column that runs over. '''
        self._shortest_header = ''
        ''' Keep only the distinct test cases across different suites. Key is
        hashed by the string representation of each test case (2d array). '''
        self._tests = {}

    def _set_header(self):
        ''' Read all the given `self._suites` and find the shortest common
        CSV header among all. '''
        column_size = 99999
        for suite in self._suites:
            siz = 0
            header = ''
            with open(suite, 'r') as f:
                header = f.readline()
                siz = len(header.split(','))
            if siz > 0 and siz < column_size:
                self._shortest_header = header.strip()
                column_size = siz
        assert self._shortest_header != ''
        assert column_size < 99999 and column_size > 0

    def _column_size(self):
        ''' :returns: the number of columns '''
        return len(self._shortest_header.split(','))

    def merge_suites(self):
        print header + 'Merging ' + str(len(self._suites)) + ' suites'
        self._set_header()
        for suite in self._suites:
            lines = None
            with open(suite, 'r') as f:
                lines = f.readlines()
            lines = [l.strip() for l in lines]
            if len(lines) < 2:
                # empty file
                continue
            assert self._shortest_header in lines[0].strip()
            test_case = []
            for l in lines[1:]:
                if l != '':
                    step = [val for val in l.strip().split(',')][:self._column_size()]
                    test_case.append(step)
                elif len(test_case) != 0:
                    # empty line -> test case ended. Store.
                    # only if the list is not empty
                    self._tests[hash(str(test_case))] = test_case
                    test_case = []
            if len(test_case) != 0:
                self._tests[hash(str(test_case))] = test_case

    def write_universal_suite(self, filename):
        print header + 'Writing merged suite to ' + filename
        with open(filename, 'w') as f:
            f.write(self._shortest_header + '\n')
            for test in self._tests.itervalues():
                f.write(self._test_to_string(test) + '\n')
            # remove the last line break
            f.seek(-1, os.SEEK_END)
            f.truncate()

    def write_tests_separately(self, outdir, basename):
        print header + 'Splitting tests to ' + outdir
        for i, test in enumerate(self._tests.itervalues()):
            with open(outdir+'/'+basename+'_tc_'+str(i)+'.csv', 'w') as f:
                f.write(self._shortest_header + '\n')
                f.write(self._test_to_string(test))

    def _test_to_string(self, test):
        def _convert_step_to_csvrow(step):
            w = ''
            for val in step:
                w += str(val) + ','
            return w[:-1] + '\n'

        def _trim_step(step):
            return step[:len(self._shortest_header.split(','))]

        rows = ''
        for step in test:
            rows += _convert_step_to_csvrow(_trim_step(step))
        return rows


class TestUniversalSuite:

    @classmethod
    def setup_class(self):
        os.mkdir('tmp_suite')
        os.mkdir('tmp_out')
        for i in range(0, 7):
            with open('tmp_suite/dummy_suite' + str(i) + '.csv', 'w') as f:
                f.write('h1,h2\n')
                f.write(str(i % 2) + ',' + str((i+1) % 2) + '\n')
                f.write(str(i % 3) + ',' + str((i+1) % 3) + '\n')
        self.suite = UniversalSuite(glob.glob('tmp_suite/*.csv'), 'tmp_out', 'basen')

    @classmethod
    def teardown_class(self):
        shutil.rmtree('tmp_suite')
        shutil.rmtree('tmp_out')

    def test_merge_suites(self):
        self.suite.merge_suites()
        print self.suite._tests
        assert len(self.suite._tests) == 6

    def test_write_universal_suite(self):
        self.suite.merge_suites()
        outfile = 'tmp_out/out.csv'
        self.suite.write_universal_suite(outfile)
        assert len(open(outfile, 'r').readlines()) == 19

    def test_write_tests_separately(self):
        self.suite.merge_suites()
        self.suite.write_tests_separately('tmp_out', 'basen')
        assert len(glob.glob(self.suite._outdir + '/basen_tc_*.csv')) == 6


