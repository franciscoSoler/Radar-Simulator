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


def save_plots(filename, fig, path='../../overleaf/Chapter3/Figs/Raster'):
        fig.tight_layout()
        fig.savefig(os.path.join(path, filename + ".png"), bbox_inches='tight')


def read_data(filename):
    with open(filename) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        header = next(spamreader)
        data = list(zip(*spamreader))[:4]
    return header, data

def find_nearest(array, value):
    return (np.abs(array-value)).argmin()


def plot(fig, name, x, y1, y2):
    # plt.figure(fig)
    
    fig, ax1 = plt.subplots()

    ax1.plot(x, y1, 'b-', linewidth=2)
    
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Phase [deg]', color='b')
    ax1.tick_params('y', colors='b')
    ax1.tick_params('x', length=10, width=2, which='major')
    ax1.tick_params('x', length=5, width=2, which='minor')
    ax1.set_xscale('log')
    plt.xticks([0, 10, 100, 1000, 10000, 20000])
    # ax1.xaxis.set_tick_params(width=5)
    # ax1.xaxis.set_tick_params()
    ax1.grid(True, which='both')

    ax2 = ax1.twinx()
    ax2.axhline(y=10.45, color='k', linestyle='--')
    ax2.axhline(y=7.45, color='k', linestyle='--')
    # ax2.axvline(x=20235.8, color='k', linestyle='--')
    
    ax2.plot(x, y2, 'r', linewidth=2)
    ax2.set_ylabel('Gain [dB]', color='r')
    ax2.tick_params('y', colors='r', length=10)


    # save_plots(name, plt)

def main():
    plt.rcParams.update({'font.size': 20})

    header, data = read_data("transference")
    freq = list(map(float, data[0]))
    vin = list(map(lambda x: float(x)*1e-3, data[1]))
    vout = list(map(float, data[2]))
    time_interval = list(map(lambda x:float(x)*1e-6, data[3]))

    phase = list(map(lambda x, y: x*y*360 % 360, freq, time_interval))
    gain = list(map(lambda x, y: 20*np.log10(abs(y/x)), vin, vout))

    plot(1, 'Transference', freq, phase, gain)
    plt.show()


if __name__ == '__main__':
    main()
    sys.exit(0)