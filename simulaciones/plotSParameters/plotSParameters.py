#!/usr/bin/python3

import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import os
import csv
import re


def set_plot_environment(plt, title, y_label, x_label, locc=None):
    plt.set_title(title)
    plt.set_ylabel(y_label)
    plt.set_xlabel(x_label)
    plt.grid(True)
    plt.legend()
    
    plt.axvline(x=2.3E9, color='k')
    plt.axvline(x=2.45E9, color='k', linestyle='--')
    plt.axvline(x=2.6E9, color='k')
    
    if locc is not None:
        plt.legend(loc=locc, prop={'size':18})


def save_plots(filename, plt, path='../../written/thesis/Chapter3/Figs/Raster'):
    plt.savefig(os.path.join(path, filename + ".png"), bbox_inches='tight', dpi=60)


def find_nearest(array, value):
    return (np.abs(array-value)).argmin()


def read_data(dirname):
    data = []
    x = []
    with open(dirname) as f:
        while next(f)[0] == "!":
            pass
        for line in f:
            d = list(map(float, line.rstrip().split('\t')))
            x.append(float(d[0]))
            data.append([complex(d[2*i+1], d[2*i+2]) for i in range(len(d)//2)])
    return x[100:-100], np.array(list(zip(*data)))[:, 100:-100]


def plot(name, save_images, x, y):

    print('S11', name, np.real(y[0, find_nearest(np.matrix(x), 2450000000)]))
    print('S21', name, np.real(y[1, find_nearest(np.matrix(x), 2450000000)]))
    print('S12', name, np.real(y[2, find_nearest(np.matrix(x), 2450000000)]))
    print('S22', name, np.real(y[3, find_nearest(np.matrix(x), 2450000000)]))
    print()

    f, axarr = plt.subplots(3, sharex=True, figsize=(12, 8))
    f.subplots_adjust(hspace=0)
    axarr[0].plot(x, np.real(y[0,:]), linewidth=2, label='$S_{11}$')
    axarr[1].plot(x, np.real(y[1,:]), linewidth=2, label='$S_{21}$')
    axarr[2].plot(x, np.real(y[3,:]), linewidth=2, label='$S_{22}$')
    
    axarr[0].yaxis.set_major_locator(MaxNLocator(nbins=len(axarr[0].get_xticklabels()), prune='both'))
    axarr[1].yaxis.set_major_locator(MaxNLocator(nbins=len(axarr[1].get_xticklabels()), prune='both'))
    axarr[2].yaxis.set_major_locator(MaxNLocator(nbins=len(axarr[2].get_xticklabels()), prune='both'))
    
    set_plot_environment(axarr[0], 'Parámetros S de las antenas, polarizaciones ' + name, '', '', locc=2)
    set_plot_environment(axarr[1], '', 'Power [dB]', '', locc=2)
    set_plot_environment(axarr[2], '', '', 'Angle [deg]', locc=2)
    plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)

    if save_images:
        save_plots('SParams' + name, plt)
    else:
        plt.show()

def main():
    plt.rcParams.update({'font.size': 20})
    plt.figure(figsize=(9, 8))
    save_images = True
    plot('HH', save_images, *read_data('TxHRxH.s2p'))
    plot('HV', save_images, *read_data('TxHRxV.s2p'))
    plot('VH', save_images, *read_data('TxVRxH.s2p'))
    plot('VV', save_images, *read_data('TxVRxV.s2p'))


if __name__ == '__main__':
    main()
    sys.exit(0)