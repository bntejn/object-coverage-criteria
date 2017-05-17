#!/usr/bin/env python

'''
@author: Taejoon Byun <taejoon@umn.edu>

first: Apr 12 2017
last : Apr 13 2017
'''
import ObjectBranchCoverage as OBC
import sys, os, glob, argparse
import pandas as pd
import matplotlib.pyplot as plt

def basename(path):
    return path.split('/')[-1]

def get_report_for_each_bin(system, target, flist):
    obc = OBC.ObjectBranchCoverage(target, flist)
    cov = system + '/cov/' + basename(target) + '/universal.pincov'
    obc.update_cov_from_pincov(cov)
    return obc.get_ins_category_stats('J')[1]

def analyze_each_system(system):
    def get_sysname(path):
        compiler = path.split('/')[2].split('-')[1]
        sysname = path.split('/')[5]
        return '%s,%s' % (sysname, compiler)
    #print '\tGetting stats for [%s]' % system
    binaries = glob.glob(system + '/cov/*')
    binaries = sorted(binaries)
    binaries = [system + '/bin/' + basename(path) for path in binaries]
    flist = glob.glob(system + '/bin/*.flist')[0]
    w = get_sysname(system) + ','
    for binary in binaries:
        w += '%d,' % get_report_for_each_bin(system, binary, flist)
    print w[:-1]


def main():
    argp = argparse.ArgumentParser()
    argp.add_argument('directory', type=str, help='Path to an output directory')
    argp.add_argument('--system', '-s', action='store_true', default=True,
            help='Plot all systems in a "systems" directory (default)')
    argp.add_argument('--all', '-a', action='store_true', default=False,
            help='Plot all systems of systems in THE output directory')
    args = argp.parse_args()

    assert os.path.isdir(args.directory)
    if args.all:
        sys_paths = glob.glob(args.directory + '/*/obc/*/*')
        sys_paths = sorted(sys_paths)
        print 'system,compiler,O0,O1,O2,O3,Os'
        for system in sys_paths:
            analyze_each_system(system)
    elif args.system:
        sys_paths = glob.glob(args.directory + '/obc/*/*')
        sys_paths = sorted(sys_paths)
        for system in sys_paths:
            analyze_each_system(system)


if __name__ == '__main__':
    main()

