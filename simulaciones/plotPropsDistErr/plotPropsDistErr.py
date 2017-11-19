#!/usr/bin/python3

import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import os
import csv
import re


def set_plot_environment(plt, title, y_label, x_label, lineObjects, legends, locc=None):
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.grid(True)
    plt.legend()

    # hiding the upper value of ylabel
    frame1 = plt.gca()
    nbins = len(frame1.get_xticklabels())
    frame1.yaxis.set_major_locator(MaxNLocator(nbins=nbins, prune='upper'))

    if locc is not None:
        plt.legend(iter(lineObjects), tuple(legends), loc=locc, prop={'size':16})
    else:
        plt.legend(iter(lineObjects), tuple(legends), prop={'size':16})


def save_plots(filename, plt, path='../../written/thesis/Chapter5/Figs/Raster'):
    plt.savefig(os.path.join(path, filename + ".png"), bbox_inches='tight', dpi=80)


def plot(title, name, xaxis, yaxis, save_images, x, y, legends=None, locc=None):
    plt.figure(figsize=(9, 7))
    lineObjects = plt.plot(x, list(zip(*y)), linewidth=2)


    set_plot_environment(plt, title + ' medida a diferentes distancias', yaxis, xaxis, lineObjects, legends, locc=locc)

    if save_images:
        save_plots(name, plt)
    else:
        plt.show()


def plot_incert(title, name, xaxis, yaxis, save_images, x, y, legends=None, locc=None):
    plt.figure(figsize=(9, 7))
    lineObjects = plt.plot(x, list(zip(*y)), linewidth=2)


    set_plot_environment(plt, title + ' medida a diferentes distancias', yaxis, xaxis, lineObjects, legends, locc=locc)
    lim_x = 9.5
    lim_y = 30
    plt.plot([lim_x, lim_x], [0, lim_y], 'k-')
    plt.plot([0, lim_x], [lim_y, lim_y], 'k-')
    if save_images:
        save_plots(name, plt)
    else:
        plt.show()


def main():
    plt.rcParams.update({'font.size': 20})
    # plt.figure(figsize=(9, 8))
    save_images = True

    distances = [30760, 35000, 37760.1695, 40000]
    data = []
    data.append(list(map(lambda x: round(x,1), [0 , 0.9974998783 , -0.8999873159 , 0.9970854521 , 5.0829022535 , 0.9974244573 , 0.0563536612 , 0.9991246271 , 1.1021289469])))
    data.append(list(map(lambda x: round(x,1), [5 , 0.996851467 , -28.5141663823 , 0.9965158111 , -22.5305974732 , 0.9968962677 , -27.5567038267 , 0.9986251585 , -26.5105696718])))
    data.append(list(map(lambda x: round(x,1), [10 , 0.9962033718 , -56.1283462497 , 0.9959464141 , -50.1440980009 , 0.9963682879 , -55.1697621157 , 0.9981258771 , -54.1232690916])))
    data.append(list(map(lambda x: round(x,1), [40 , 0.9923214343 , -221.8134422774, 0.9925351551 , -215.8251179909, 0.9932048122 , -220.8481286728, 0.9951341194 , -219.7994824332])))
    data.append(list(map(lambda x: round(x,1), [100 , 0.984591606 , -553.1837208524, 0.9857389337 , -547.1872444906, 0.986900466 , -552.2049483068, 0.9891707856 , -551.1519956365])))

    d = list(zip(*data))
    delta = d[0]
    gain = d[1::2]
    phase = d[2::2]

    plot('Ganancia', 'deltaDistGain', 'Delta [m]', 'Ganancia [dB]', save_images, delta, gain, legends=distances, locc=1)
    plot('Fase', 'deltaDistPhase', 'Delta [m]', 'Fase [deg]', save_images, delta, phase, legends=distances, locc=2)
    
    data = []
    data.append([0 , 0.00 , 0.00 , 0.00 , 0.00 , 0.00 , 0.00 , 0.00 , 0.00])
    data.append([5 , 0.000369507 , 15.7325843211 , 0.0003330912 , 16.1431290009 , 0.0002977873 , 15.5648756904 , 0.0002884168 , 15.9418570692])
    data.append([10 , 0.0007337078 , 31.239336556 , 0.0006511433 , 31.5574962315 , 0.0006150956 , 32.1497974883 , 0.0005796089 , 32.0371315787])
    data.append([40 , 0.0029849535 , 116.5644598149 , 0.002650077 , 116.673494049 , 0.0023426065 , 112.3447856255  , 0.0023238051 , 117.0437670382])

    d = list(zip(*data))
    delta = d[0]
    phase = d[2::2]
    plot_incert('Incertidumbre de fase', 'incertDistPhase', 'Delta [m]', 'Delta Fase [deg]', save_images, delta, phase, legends=distances, locc=2)

    distances = [2.201, 2.229, 2.255]
    data = []
    data.append([0, -1.8092, 147.7, -1.8941, 133.2, -1.4372, 152.1])
    data.append([5, -1.8570, 174.8, -1.9362, 161.4, -1.4903, 179.8])
    data.append([10, -1.8940, 202, -1.9772, 188.0, -1.5177, 207.0])
    data.append([15, -1.9243, 229.5, -2.0172, 215.5, -1.5622, 234.4])

    d = list(zip(*data))
    delta = d[0]
    gain = d[1::2]
    phase = d[2::2]

    plot('Ganancia', 'deltaDistGainRadar', 'Delta [mm]', 'Ganancia [dB]', save_images, delta, gain, legends=distances, locc=1)
    plot('Fase', 'deltaDistPhaseRadar', 'Delta [mm]', 'Fase [deg]', save_images, delta, phase, legends=distances, locc=2)


if __name__ == '__main__':
    main()
    sys.exit(0)