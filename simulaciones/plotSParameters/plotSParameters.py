#!/usr/bin/python3

import sys
import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import re


def set_plot_environment(plt, title, y_label, x_label, locc=None):
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.grid(True)
    plt.legend()
    if locc is not None:
        plt.legend(loc=locc, prop={'size':18})


def save_plots(filename, plt, path='../../written/thesis/Chapter3/Figs/Raster'):
    plt.tight_layout()
    plt.savefig(os.path.join(path, filename + ".png"), bbox_inches='tight')


def find_nearest(array, value):
    return (np.abs(array-value)).argmin()


def read_data(dirname):
    data = []
    x = []
    with open('AutoSave20.s2p') as f:
        while next(f)[0] == "!":
            pass
        for line in f:
            d = list(map(float, line.rstrip().split('\t')))
            x.append(float(d[0]))
            data.append([complex(d[2*i+1], d[2*i+2]) for i in range(len(d)//2)])
    return x, np.array(list(zip(*data)))


def plot(fig, name, save_images, x, y):
    if x:
        plt.plot(x, np.real(y[0,:]), linewidth=2, label=name)
    else:
        plt.plot(y, linewidth=2)
    set_plot_environment(plt, 'Transmitted Power ' + name, 'Power [dBm]', 'Angle [deg]', locc=4)


def main():
    plt.rcParams.update({'font.size': 20})
    plt.figure(figsize=(9, 8))
    save_images = False
    plot(1, 'HH pattern', save_images, *read_data("HH"))
    # plot(1, 'HV pattern', save_images, *read_data("VH"))
    # plot(1, 'VV pattern', save_images, *read_data("VV"))
    plt.show()
    # save_plots('patterns', plt)


if __name__ == '__main__':
    main()
    sys.exit(0)