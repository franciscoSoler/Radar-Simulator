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


def save_plots(filename, plt, path='../../written/thesis/Chapter2/Figs/Raster'):
        plt.tight_layout()
        plt.savefig(os.path.join(path, filename + ".png"), bbox_inches='tight')


def main():
    plt.rcParams.update({'font.size': 18, 'legend.fontsize': 14})

    start = 0
    stop = 1
    step = 0.001
    up = np.arange(start, stop, step)
    down = np.arange(start, stop, step*10)[::-1]
    signal = np.concatenate((up, down, up, down))
    
    time = np.arange(start, signal.size*step, step)
    tau = 200
    received_signal = np.roll(signal, tau)

    t = signal.size/2*step
    t1 = t + tau * step

    plt.figure(1)
    plt.yticks([0, 0.5, 1], ['Fmin', 'f0', 'Fmax'])
    plt.xticks([0, t, t1, 2*t], ['0', 'T', 'T1', '2T'])
    plt.plot(time, signal, label='Transmitted Signal', linewidth=2)
    plt.plot(time, received_signal, "--", label='Received Signal', linewidth=2)

    plt.vlines(t, 0, 1, linestyles='dashed', linewidth=2)
    plt.vlines(t1, 0, 1, linestyles='dashed', linewidth=2)

    set_plot_environment(plt, 'Received Signal', 'Frequency', 'Time', 4)
    save_plots('FMCWambiguity', plt)

    plt.figure(2)
    plt.yticks([0, 0.2, 0.9], ['0', '0.2BW', '0.9BW'])
    plt.xticks([0, t, t1, 2*t], ['0', 'T', 'T1', '2T'])

    plt.plot(time, abs(signal - received_signal), label='Mixed Frequency', linewidth=2)

    plt.vlines(t, 0, 1, linestyles='dashed', linewidth=2)
    plt.vlines(t1, 0, 1, linestyles='dashed', linewidth=2)

    set_plot_environment(plt, 'Mixed Signal', 'Frequency', 'Time')
    save_plots('receivedFrequency', plt)

    plt.figure(3)
    plt.yticks([0, 0.5, 1], ['Fmin', 'f0', 'Fmax'])
    plt.plot(time, signal, label='Transmitted Signal', linewidth=2)
    plt.plot(time, received_signal, "--", label='Received Signal', linewidth=2)

    plt.annotate('', xy=(stop/2, 0.5), xycoords='data', xytext=(stop/2 + 200*step, 0.5), textcoords='data',
                 arrowprops={'arrowstyle': '<|-|>', 'shrinkA':0, 'shrinkB':0})
    plt.annotate(r'$\tau$', xy=(stop/2, 0.5), xycoords='data', xytext=(0.58, 0.51), textcoords='data', fontsize=28)

    plt.annotate('', xy=(stop/2, 0.5), xycoords='data', xytext=(0.5, received_signal[0.5/step]), textcoords='data',
                 arrowprops={'arrowstyle': '<|-|>', 'shrinkA':0, 'shrinkB':0})
    plt.annotate(r'$\Delta f$', xy=(stop/2, 0.5), xycoords='data', xytext=(0.33, 0.4), textcoords='data', fontsize=20)

    set_plot_environment(plt, 'Received Signal', 'Frequency', 'Time', 4)
    save_plots('round-tripTime', plt)

    plt.show()


if __name__ == '__main__':
    main()
    sys.exit(0)
