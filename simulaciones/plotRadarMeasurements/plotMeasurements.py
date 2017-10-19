#!/usr/bin/python3

import sys
import matplotlib.pyplot as plt
import numpy as np
import os
import csv


def set_plot_environment(title, y_label, x_label, locc=None):
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.grid(True)

    if locc is not None:
        plt.legend(loc=locc)


def save_plots(filename, fig, path='../../written/thesis/Chapter5/Figs/Raster'):
        fig.tight_layout()
        fig.savefig(os.path.join(path, filename + ".png"), bbox_inches='tight')


def read_data(filename):
    with open(filename) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        header = next(spamreader)
        data = list(zip(*spamreader))
    return header, data

def find_nearest(array, value):
    return (np.abs(array-value)).argmin()


def plot(fig, name, x, y, delta, mode='Diagonal', offset=0):
    plt.plot(x, x if mode == 'Diagonal' else [offset]*len(x))
    plt.errorbar(x, y, delta, fmt='ok', lw=3)
    plt.xticks(x)

    save_plots(name, fig)

def main():
    plt.rcParams.update({'font.size': 20})
    obj = 'Corner'
    header, data = read_data(obj + "Measurements.csv")
    real_dists = list(map(float, data[0]))[::4]

    dists = list(map(float, data[2]))
    delta_dists = list(map(float, data[3]))

    fig = plt.figure(0)
    set_plot_environment('Rango Medido, pol HH', 'Rango Medido [m]', 'Rango Teórico [m]')
    plot(fig, 'measured{}RangeHH'.format(obj), real_dists, dists[::4], delta_dists[::4])

    fig = plt.figure(1)
    set_plot_environment('Rango Medido, pol HV', 'Rango Medido [m]', 'Rango Teórico [m]')
    plot(fig, 'measured{}RangeHV'.format(obj), real_dists, dists[1::4], delta_dists[1::4])

    fig = plt.figure(2)
    set_plot_environment('Rango Medido, pol VH', 'Rango Medido [m]', 'Rango Teórico [m]')
    plot(fig, 'measured{}RangeVH'.format(obj), real_dists, dists[2::4], delta_dists[2::4])

    fig = plt.figure(3)
    set_plot_environment('Rango Medido, pol VV', 'Rango Medido [m]', 'Rango Teórico [m]')
    plot(fig, 'measured{}RangeVV'.format(obj), real_dists, dists[3::4], delta_dists[3::4])

    gain = list(map(float, data[4]))
    delta_gain = list(map(float, data[5]))

    fig = plt.figure(4)
    set_plot_environment('Relación Ganancia Medida, pol HH', 'Relación Ganancia [dB]', 'Rango Teórico [m]')
    plot(fig, 'measured{}GainHH'.format(obj), real_dists, gain[::4], delta_gain[::4], mode='Lineal', offset=-1.55)

    fig = plt.figure(5)
    set_plot_environment('Relación Ganancia Medida, pol HV', 'Relación Ganancia [dB]', 'Rango Teórico [m]')
    plot(fig, 'measured{}GainHV'.format(obj), real_dists, gain[1::4], delta_gain[1::4], mode='Lineal', offset=-14)

    fig = plt.figure(6)
    set_plot_environment('Relación Ganancia Medida, pol VH', 'Relación Ganancia [dB]', 'Rango Teórico [m]')
    plot(fig, 'measured{}GainVH'.format(obj), real_dists, gain[2::4], delta_gain[2::4], mode='Lineal', offset=-14)

    fig = plt.figure(7)
    set_plot_environment('Relación Ganancia Medida, pol VV', 'Relación Ganancia [dB]', 'Rango Teórico [m]')
    plot(fig, 'measured{}GainVV'.format(obj), real_dists, gain[3::4], delta_gain[3::4], mode='Lineal', offset=-1.65)

    phase = list(map(float, data[6]))
    delta_phase = list(map(float, data[7]))

    fig = plt.figure(8)
    set_plot_environment('Relación Fase Medida, pol HH', 'Relación Fase [deg]', 'Rango Teórico [m]')
    plot(fig, 'measured{}PhaseHH'.format(obj), real_dists, phase[::4], delta_phase[::4], mode='Lineal', offset=-10)

    fig = plt.figure(9)
    set_plot_environment('Relación Fase Medida, pol HV', 'Relación Fase [deg]', 'Rango Teórico [m]')
    plot(fig, 'measured{}PhaseHV'.format(obj), real_dists, phase[1::4], delta_phase[1::4], mode='Lineal', offset=-72)

    fig = plt.figure(10)
    set_plot_environment('Relación Fase Medida, pol VH', 'Relación Fase [deg]', 'Rango Teórico [m]')
    plot(fig, 'measured{}PhaseVH'.format(obj), real_dists, phase[2::4], delta_phase[2::4], mode='Lineal', offset=-93)

    fig = plt.figure(11)
    set_plot_environment('Relación Fase Medida, pol VV', 'Relación Fase [deg]', 'Rango Teórico [m]')
    plot(fig, 'measured{}PhaseVV'.format(obj), real_dists, phase[3::4], delta_phase[3::4], mode='Lineal', offset=155)

    plt.show()


if __name__ == '__main__':
    main()
    sys.exit(0)