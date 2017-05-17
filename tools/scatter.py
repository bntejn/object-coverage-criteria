#!/usr/bin/env python

# Taejoon Byun <taejoon@umn.edu>

# first: Apr 5 2017
# last : Apr 5 2017

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys, glob

rootdir = './'

class Plotter():
    OPTS = ['o0', 'o1', 'o2', 'o3', 'os']
    TYPES = ['J', 'JSM', 'JSMB', 'JSML']
    COLORS = ['r', 'b', 'g', 'k']
    MARKERS= ['o', 'x', 'x', 'o']

    def __init__(self, basedir):
        self.basedir = basedir
        self.plot = plt.figure().add_subplot(1, 1, 1)
        self.dict_opt_type = {}

    def _get_max_oracle_col_name(self, df):
        scores = [col for col in df.columns if 'score' in col]
        int_scores= [int(score.split('_')[-1]) for score in scores]
        max_ind = int_scores.index(max(int_scores))
        self.max_oracle_col_name = scores[max_ind]
        return scores[max_ind]

    def _get_df_from_ff(self, opt, typ):
        ''' Get a dataframe from a fault finding report
        :param opt: optimization level: {o0, o1, o2, ...}
        :param typ: coverage type: {J, JSM, JSML, ...}
        '''
        csv = glob.glob('%s/*.obc_%s_%s.ff.csv' % (self.basedir, opt, typ))[0]
        print '\t%s' % csv
        df = pd.read_csv(csv)
        df['optimization'] = opt
        score_col = self._get_max_oracle_col_name(df)
        if opt not in self.dict_opt_type:
            self.dict_opt_type[opt] = {}
        self.dict_opt_type[opt][typ] = df[score_col].mean()
        return df[['optimization', score_col]]

    def _parse_data(self):
        type_dfs = {}
        for typ in self.TYPES:
            dfs = []
            for opt in self.OPTS:
                dfs.append(self._get_df_from_ff(opt, typ))
            type_dfs[typ] = pd.concat(dfs, ignore_index=True)
        self.df_mean = pd.DataFrame(self.dict_opt_type).T
        return type_dfs
    
    def plot_scatter(self):
        dict_type_df = self._parse_data()
        assert len(dict_type_df) > 0
        for i, typ in enumerate(dict_type_df):
            df = dict_type_df[typ]
            Xuniques, X = np.unique(df['optimization'], return_inverse=True)
            self.plot.scatter(X, df[self.max_oracle_col_name], 
                    color=self.COLORS[i], s=4, marker=self.MARKERS[i], 
                    label=typ)
            Xuniquesp, Xp = np.unique(self.df_mean.index, return_inverse=True)
            self.plot.plot(Xp, self.df_mean[typ], 
                    color=self.COLORS[i], linewidth=1)
            self.plot.set(xticks=range(len(Xuniques)), xticklabels=Xuniques)

    def show(self):
        plt.legend(loc='lower left', numpoints=1, ncol=2, fontsize=8, 
                bbox_to_anchor=(0, 0))
        plt.show()

    def savefig(self, name):
        plt.legend(loc='lower left', numpoints=1, ncol=2, fontsize=8, 
                bbox_to_anchor=(0, 0))
        plt.savefig(name)

def plot_scatter(ff_dir):
    plotter = Plotter(ff_dir)
    plotter.plot_scatter()
    plotter.savefig(ff_dir + '/scatter.png')
    plotter.show()

def main():
    INDIVIDUAL = False

    if INDIVIDUAL:
        if len(sys.argv) != 2:
            print '$ python %s <ff_dir>' % sys.argv[0]
            sys.exit()
        plot_scatter(sys.argv[1])
    else:
        # for all <ff_dir>s in <out_dir>
        if len(sys.argv) != 2:
            print '$ python %s <out_systems_dir>' % sys.argv[0]
            sys.exit()
        dirs = glob.glob(sys.argv[1] + '/results/*/*')
        for d in dirs:
            print d
            plot_scatter(d)

if __name__ == '__main__':
    main()

