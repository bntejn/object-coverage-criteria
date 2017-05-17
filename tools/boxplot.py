#!/usr/bin/env python

# Taejoon Byun <taejoon@umn.edu>

# first: Apr 5 2017 (copied scatter.py on Apr 7)
# last : Apr 12 2017

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys, glob, argparse


def basename(path):
    return path.split('/')[-1]

class Plotter():
    OPTS = ['o0', 'o1', 'o2', 'o3', 'os']
    COMPS = ['gcc', 'clang', 'ccomp']
    TYPES = ['J', 'JSMB']
    MAXIMUM_ORACLE = False

    def __init__(self, basedir, global_minmax=False, max_oracle=True):
        self.basedir = basedir
        self.dict_opt_type = {}
        self.global_minmax = global_minmax
        self.MAXIMUM_ORACLE = max_oracle

    def get_oracle_col_name(self, df, is_max=True):
        scores = [col for col in df.columns if 'score' in col]
        int_scores= [int(score.split('_')[-1]) for score in scores]
        ind = int_scores.index(max(int_scores) if is_max else min(int_scores))
        self.max_oracle_col_name = scores[ind]
        return scores[ind]

    def _get_df_from_ff(self, basedir, criterion):
        ''' Get a dataframe from a fault finding report '''
        csv = glob.glob('%s/*.%s.ff.csv' % (basedir, criterion))[0]
        #print '\t%s' % basename(csv)
        df = pd.read_csv(csv)
        score_col = self.get_oracle_col_name(df, self.MAXIMUM_ORACLE)
        df = df[score_col]
        if 'obc' in criterion:
            df.name = criterion.split('_')[1]
        else:
            df.name = criterion
        return df

    def _get_mcdc_df(self):
        dfs = pd.DataFrame()
        dfs['mcdc'] = self._get_df_from_ff(self.basedir, 'mcdc')
        return dfs

    def _get_obc_df(self, obc_type):
        dfs = pd.DataFrame()
        for opt in self.OPTS:
            # column represents optimization levels
            criterion = 'obc_%s_%s' % (opt, obc_type)
            df = self._get_df_from_ff(self.basedir, criterion)
            dfs[df.name] = df
        return dfs

    def get_min_max(self):
        assert self.global_minmax is True
        sysdir_base = '-'.join(self.basedir.split('/')[-4].split('-')[:-1])
        sysname = self.basedir.split('/')[-1]
        dirs = []
        for cc in self.COMPS:
            globbed = glob.glob('%s/../../../../%s-%s/results/*/%s' % \
                    (self.basedir, sysdir_base, cc, sysname))
            dirs += globbed
        minv, maxv= 100, 0
        for d in dirs:
            for typ in self.TYPES:
                dfs = pd.DataFrame()
                for opt in self.OPTS:
                    criterion = 'obc_%s_%s' % (opt, typ)
                    df = self._get_df_from_ff(d, criterion)
                    dfs[df.name] = df
                dfs['mcdc'] = self._get_df_from_ff(d, 'mcdc')
                minv = dfs.min().min() if dfs.min().min() < minv else minv
                maxv = dfs.max().max() if dfs.max().max() > maxv else maxv

        print 'min: %d, max: %d' % (minv, maxv)
        self.minv, self.maxv = minv, maxv


    def plot_box(self, cov_type):
        ''' http://matplotlib.org/examples/statistics/boxplot_demo.html '''
        plt.clf()
        dfs = self._get_obc_df(cov_type)

        fig, axs = plt.subplots(1,1,figsize=(5,8))
        #box = dfs.boxplot(**kwds)
        box = dfs.boxplot(**self._get_kwds())
        if self.global_minmax:
            box.set_ylim(self.minv - 1, self.maxv + 1)
        #fig.set_size_inches(4, 6)
        axs.set_xticklabels([], visible=False)
        axs.set_yticklabels([], visible=False)
        axs.grid(linestyle='-', linewidth='0.5', color='gray')
        axs.xaxis.grid(False)

    def _get_kwds(self):
        bp = dict(linewidth=2.5, color='black')
        wp = dict(linewidth=2)
        mp = dict(linewidth=3, color='red')
        mlp = dict(linestyle='--', linewidth=2.5, color='blue')
        mpp= dict(marker='o', markeredgecolor='black',
                markerfacecolor='firebrick', linewidth=4, color='red')
        return dict(widths=0.7, boxprops=bp, medianprops=mpp,
                meanprops=mlp, meanline=True, showmeans=True, whiskerprops=wp)

    def plot_mcdc(self):
        ''' http://matplotlib.org/examples/statistics/boxplot_demo.html '''
        #fig, axes = plt.subplots(nrows=1, ncols=2)
        #boxes = []
        plt.clf()
        dfs = self._get_mcdc_df()

        fig, axs = plt.subplots(1,1,figsize=(1,8))
        box = dfs.boxplot(**self._get_kwds())
        box.tick_params(labelsize=24)
        #box.set_ylabel('mutation score (%)', fontsize=18)
        #fig.set_size_inches(1, 6)
        axs.set_xticklabels([], visible=False)
        if self.global_minmax:
            box.set_ylim(self.minv - 1, self.maxv + 1)
        yticks = axs.yaxis.get_major_ticks()
        yticks[0].label1.set_visible(False)
        axs.grid(linestyle='-', linewidth='0.5')
        axs.xaxis.grid(False)


    def show(self):
        plt.show()

    def savefig(self, name):
        print 'saving a figure to %s' % name
        fig = plt.gcf()
        #fig.tight_layout()
        fig.savefig(name, bbox_inches='tight', pad_inches=0)
        plt.clf()

def plot_box(ff_dir, is_all=False, max_oracle=False):
    plotter = Plotter(ff_dir, global_minmax=True, max_oracle=max_oracle)
    plotter.get_min_max()
    plotter.plot_box('J')
    plotter = Plotter(ff_dir, global_minmax=True, max_oracle=max_oracle)
    plotter.get_min_max()
    plotter.savefig(ff_dir + '/boxplot1.pdf')
    plotter.plot_box('JSMB')
    plotter.savefig(ff_dir + '/boxplot2.pdf')
    plotter.plot_mcdc()
    plotter.savefig(ff_dir + '/boxplot3.pdf')

def main():
    argp = argparse.ArgumentParser()
    argp.add_argument('directory', type=str, help='Path to an output directory')
    argp.add_argument('--individual', '-i', action='store_true',
            help='Plot an individual system', default=False)
    argp.add_argument('--system', '-s', action='store_true', default=True,
            help='Plot all systems in a "systems" directory (default)')
    argp.add_argument('--all', '-a', action='store_true', default=False,
            help='Plot all systems of systems in THE output directory')
    argp.add_argument('--maximum', '-m', action='store_true', default=False,
            help='Enable maximum oracle')
    args = argp.parse_args()

    if args.all:
        dirs = glob.glob(args.directory + '/*/results/*/*')
        for d in dirs:
            print '\n' + d
            try:
                plot_box(d, is_all=True)
            except Exception as e:
                print '\033[91m%s\033[0m' % str(e)
    elif args.individual:
        plot_box(args.directory, is_all=args.maximum, max_oracle=args.maximum)
    elif args.system:
        dirs = glob.glob(args.directory + '/results/*/*')
        dirs = sorted(dirs)
        for d in dirs:
            print d
            plot_box(d)

if __name__ == '__main__':
    main()

