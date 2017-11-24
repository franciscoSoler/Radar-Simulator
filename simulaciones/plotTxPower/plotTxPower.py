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


def save_plots(filename, plt, path='../../written/thesis/Chapter3/Figs/Raster'):
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


def plot(fig, name, x, y):
    x = np.array(list(map(lambda x: float(x)/ 1e9, x)))
    e_max = find_nearest(x, 2.8)
    e_min = find_nearest(x, 2.001)
    plt.figure(fig)

    plt.plot(x[e_min:e_max], y[e_min:e_max], linewidth=2)
    set_plot_environment(plt, 'Potencia Transmitida', 'Potencia [dBm]', 'Frecuencia [GHz]')
    save_plots(name, plt)

def main():
    plt.rcParams.update({'font.size': 20})

    x, y = read_data("POT_TX")
    plot(1, 'txPower', *read_data("POT_TX"))
    f0_peak = np.array(list(map(float, y))).max() 
    f0 = float(x[np.array(list(map(float, y))).argmax()])
    x, y = read_data("CABEZA_CHIRP_NUEVA")
    plot(2, 'chripHeadPower', x, y)
    y = np.array(list(map(float, y)))
    distances = np.abs(y.max() - 3 - y)
    distances[distances.argmin()] = 100
    fmax = float(x[distances.argmin()])
    distances[distances.argmin()] = 100
    fmin = float(x[distances.argmin()])
    
    print('f0 Peak:', f0_peak)
    print("f0 [GHz]:", f0/1e9)
    print("fmin [GHz]:", fmin/1e9)
    print("fmax [GHz]:", fmax/1e9)
    print("BW [MHz]:", (fmax - fmin)/1e6)
    # plt.show()


if __name__ == '__main__':
    main()
    sys.exit(0)
