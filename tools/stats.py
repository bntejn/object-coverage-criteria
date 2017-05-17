#!/usr/bin/env python
# generateObcStats.py

'''
@author: Taejoon Byun <taejoon@umn.edu>

first: Mar 8 2017
last : Apr 7 2017
'''
import ObjectBranchCoverage as OBC
import sys, os, glob, argparse

def basename(path):
    return path.split('/')[-1]

def get_report_for_each_bin(system, target, flist):
    ret = ''
    ret += basename(target) + '\n'
    ret += '-' * len(basename(target)) + '\n\n'
    pngs = glob.glob('%s/../../../results/*/%s/*.png' % \
            (system, basename(system)))
    for png in pngs:
        path = '/'.join(png.split('/')[-4:])
        ret += '![%s](%s)\n\n' % (basename(png).split('.')[0], path)
    obc = OBC.ObjectBranchCoverage(target, flist)
    cov = system + '/cov/' + basename(target) + '/universal.pincov'
    ret += '- target: %s\n- cov   : %s\n- flist : %s\n\n' % (target, cov, flist)
    obc.update_cov_from_pincov(cov)
    stats = obc.get_stats()
    print '%s - %s' % (basename(target), obc.get_jump_stats())
    ret += stats + '\n'
    return ret
    for b in obc._branches.itervalues():
        ret += '\t%s\n' % str(b)

def analyze_each_system(system):
    ret = ''
    print '\tGetting stats for [%s]' % system
    binaries = glob.glob(system + '/cov/*')
    binaries = sorted(binaries)
    binaries = [system + '/bin/' + basename(path) for path in binaries]
    flist = glob.glob(system + '/bin/*.flist')[0]
    # print system name
    ret += basename(system) + '\n'
    ret += '=' * len(basename(system)) + '\n'
    for target in binaries:
        ret += get_report_for_each_bin(system, target, flist) + '\n'
    with open('%s/../../../stats.md' % system, 'w') as f:
        f.write(ret)


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
        for system in sys_paths:
            analyze_each_system(system)
    elif args.system:
        sys_paths = glob.glob(args.directory + '/obc/*/*')
        for system in sys_paths:
            analyze_each_system(system)


if __name__ == '__main__':
    main()

