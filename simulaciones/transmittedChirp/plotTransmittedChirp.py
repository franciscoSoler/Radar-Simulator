#!/usr/bin/python3

import sys
import matplotlib.pyplot as plt
import numpy as np
import os


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


def main():
    start = 0
    stop = 1
    step = 0.001
    up = np.arange(start, stop, step)
    down = np.arange(start, stop, step*10)[::-1]
    signal = np.concatenate((up, down, up, down, up, down, up, down))
    t = (up.size + down.size) * step
    time = np.arange(start, signal.size*step, step)

    plt.figure(1)
    plt.yticks([0, 0.5, 1], ['Fmin', 'f0', 'Fmax'])
    plt.xticks([t, 2*t, 3*t, 4*t], ['T', '2T', '3T', '4T'])
    plt.plot(time, signal, label='Transmitted Signal', linewidth=2)

    set_plot_environment(plt, 'Transmitted Signal', 'Frequency', 'Time', 4)
    save_plots('transmittedChirp', plt)

    plt.show()


if __name__ == '__main__':
    main()
    sys.exit(0)