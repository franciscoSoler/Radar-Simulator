#!/usr/bin/python3

import sys
import matplotlib.pyplot as plt
import numpy as np
import os
import csv


def set_plot_environment(plt, title, y_label, x_label, locc=None):
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.grid(True)

    if locc is not None:
        plt.legend(loc=locc)


def save_plots(filename, plt, path='../../overleaf/Chapter2/Figs/Raster'):
        plt.tight_layout()
        plt.savefig(os.path.join(path, filename + ".png"), bbox_inches='tight')


def read_data(filename):
    with open(filename) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        while next(spamreader)[0] != "Values":
            pass
        data = list(zip(*spamreader))[:2]
    return data

def find_nearest(array, value):
    return (np.abs(array-value)).argmin()


def main():
    x, y = read_data("POT_TX")
    x = np.array(list(map(lambda x: float(x)/ 1e9, x)))
    e_max = find_nearest(x, 2.8)
    e_min = find_nearest(x, 2.001)
    plt.figure(1)

    plt.plot(x[e_min:e_max], y[e_min:e_max], label='Transmitted Power', linewidth=2)

    set_plot_environment(plt, 'Transmitted Power', 'Power [dBm]', 'Frequency [GHz]', 4)
    # save_plots('sawtoothSignal', plt)

    plt.show()


if __name__ == '__main__':
    main()
    sys.exit(0)