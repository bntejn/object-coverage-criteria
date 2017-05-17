#!/usr/bin/env python

# Apr 4 2017
# Taejoon Byun <taejoon@umn.edu>

import matplotlib.pyplot as plt
import pandas as pd
import sys, matplotlib, os, glob
matplotlib.style.use('ggplot')

def get_fig_path(original_fname, postfix):
    ''' Get the filename of the figure to save, prefixed with a (relative) path 
    to the destination directory '''
    return str('/'.join(original_fname.split('/')[:-1])) + '/' + postfix

def filter_criterion(df, crit):
    ''' Filter the rows that corresponds to the given criteria ``crit`` ''' 
    indices = [ind for ind in df.index.tolist() if ind.split('_')[-1] == crit]
    df = df[indices]
    df.index = [ind.split('_')[1] for ind in indices]
    df.name = crit
    return df

def save_figure(df, filename):
    plot = df.plot()
    fig = plot.get_figure()
    fig.savefig(filename)

def plot_report(filename):
    df_original = pd.read_csv(filename, index_col=0)
    oracles = [col for col in df_original.columns if 'score' in col]

    for oracle in oracles:
        df = df_original[oracle]
        df_j = filter_criterion(df, 'J')
        df_jsm = filter_criterion(df, 'JSM')
        df_jsml = filter_criterion(df, 'JSML')
        df = pd.concat([df_j, df_jsm, df_jsml], axis=1)
        save_figure(df, get_fig_path(filename, oracle))
    #plt.show() # show on the screen

def main():
    if len(sys.argv) != 2:
        print '$ %s <out_dir>' % sys.argv[0]
        sys.exit()
    outdir = sys.argv[1]
    reports = glob.glob(outdir + '/results/*/*/report.csv')
    for report in reports:
        plot_report(report)

if __name__ == '__main__':
    main()

