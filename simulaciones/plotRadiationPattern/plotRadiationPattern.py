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
    f0 = 2434262820.514000 # in Hz
    length = 32.5 # in cm
    data = []
    x = []
    for filename in sorted(os.listdir(dirname)):
        # print(filename)
        with open(os.path.join(dirname, filename)) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
            while next(spamreader)[0] != "Values":
                pass
            d = tuple(zip(*spamreader))
        data.append(max(tuple(map(float, d[1]))))
        x.append(np.arcsin(float(re.sub('.*_', '', filename))/length)*180/np.pi)
        print(np.arcsin(float(re.sub('.*_', '', filename))/length)*180/np.pi, max(tuple(map(float, d[1]))))
        # index = find_nearest(np.array(list(map(float, d[0]))), f0)
        # data.append(d[1][index])

    return x, data


def plot(fig, name, save_images, x, y):
    # x = np.array(list(map(lambda x: float(x)/ 1e9, x)))
    # e_max = find_nearest(x, 2.8)
    # e_min = find_nearest(x, 2.001)
    # plt.figure(fig, figsize=(8.0, 5.0))

    if x:
        plt.plot(list(map(lambda y: -y, x[::-1])) + x, y[::-1] + y, linewidth=2, label=name)
    else:
        plt.plot(y[::-1] + y, linewidth=2)
    # plt.plot(x[e_min:e_max], y[e_min:e_max], linewidth=2)
    set_plot_environment(plt, 'Transmitted Power ' + name, 'Power [dBm]', 'Angle [deg]', locc=4)
    # if save_images:
    #     save_plots(name, plt)

def main():
    plt.rcParams.update({'font.size': 20})
    plt.figure(figsize=(9, 8))
    save_images = False
    plot(1, 'HH pattern', save_images, *read_data("HH"))
    plot(1, 'HV pattern', save_images, *read_data("VH"))
    plot(1, 'VV pattern', save_images, *read_data("VV"))
    save_plots('patterns', plt)


if __name__ == '__main__':
    main()
    sys.exit(0)