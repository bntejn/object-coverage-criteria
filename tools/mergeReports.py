#!/usr/bin/env python
# mergeReports.py

#TODO
'''
Merge all the reports into a single spread sheet

first: Feb 13 2017
last : Mar 15 2017

@author Taejoon Byun <taejoon@umn.edu>
'''

import re, sys, csv, glob
import pandas as pd

sysout_dir = ''

def bname(path):
    ''' basename of a path '''
    path = path.strip()[:-1] if path.strip()[-1] is '/' else path
    return path.split('/')[-1]

def get_criterion(path, postfix):
    return re.findall('.+\.(\w+)\.%s\.csv' % postfix, path)[0]

def df_to_markdown_table(df, outfile):
    cols = df.columns
    df2 = pd.DataFrame([['---',]*len(cols)], columns=cols)
    pd.concat([df2, df]).to_csv(outfile, sep='|')

def get_ff_means(system):
    ''' Get the mean values for fault-finding reports
    :param system: a system directory to analyze

    Example:
        key: obc_o2
        value:
            suite_size    19.50
            killed_105     4.00
            score_105     25.00
            killed_11      3.00
            score_11      18.75
    '''
    ff_reports = glob.glob('%s/*ff.csv' % system)
    dfs = {get_criterion(report, 'ff'): pd.read_csv(report) for report in ff_reports}
    return {key: df.mean(axis=0) for key, df in dfs.iteritems()}

def get_cov(system):
    cov_reports = glob.glob('%s/*cov.csv' % system)
    dfs = {get_criterion(report, 'cov'): pd.read_csv(report, index_col=False) for report in cov_reports}
    return {key: df.mean(axis=0) for key, df in dfs.iteritems()}

def analyze_all(sysout_dir):
    systems = glob.glob(sysout_dir + '/*')
    # ff_dd[system][criterion] = pd.DataFrame (:fault finding dict of dicts)
    ff_dd = {bname(system): get_ff_means(system) for system in systems}
    # cov_dd[system][criterion] = pd.DataFrame (:coverage dict of dicts)
    cov_dd = {bname(system): get_cov(system) for system in systems}
    for system, cov_dict in cov_dd.iteritems():
        for criterion, cov in cov_dict.iteritems():
            ff_dd[system][criterion]['obc'] = cov[0]    #TODO
    for system in systems:
        df = pd.DataFrame(ff_dd[bname(system)]).T
        df = df[sorted(df.columns, reverse=True)]
        df = df.round(2)
        df.index.name = 'criterion'
        df.to_csv('%s/report.csv' % system)


def main():
    if len(sys.argv) != 2:
        print 'Invalid number of arguments (expected 1)'
        print 'Usage: $ %s <result_systems_dir>' % sys.argv[0]
        sys.exit()

    global sysout_dir
    sysout_dir = sys.argv[1]
    analyze_all(sysout_dir)

if __name__ == '__main__':
    main()

