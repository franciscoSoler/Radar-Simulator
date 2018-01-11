#!/usr/bin/env python
"""
This plot displays the audio waveform, spectrum, and spectrogram from the 
microphone.

Based on updating_plot.py
"""
import sys

# Major library imports
try:
    import pyaudio
except ImportError:
    sys.exit('You need pyaudio installed to run this demo.')

from numpy import linspace, short, fromstring, hstack, transpose, reshape, zeros
import numpy as np
from scipy import fft


# Enthought library imports
from chaco.default_colormaps import jet
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Button, Float
from traitsui.api import Item, Group, View, Handler, HGroup, VGroup
from pyface.timer.api import Timer

# Chaco imports
from chaco.api import Plot, ArrayPlotData, HPlotContainer

"""
NUM_SAMPLES = 1024
SAMPLING_RATE = 11025
SPECTROGRAM_LENGTH = 100
"""
C = 299792458
B = 330E6
F0 = 2450E6
# separation between values of zero padding
P = 8

FREQUENCY_DIVIDER = 1
CUT = 0
DELAY_TIME = 100
NUM_SAMPLES = 8200
SAMPLING_RATE = 40000
SPECTROGRAM_LENGTH = 50

# ============================================================================
# Create the Chaco plot.
# ============================================================================


def _create_plot_component(obj):
    # Setup the spectrum plot
    # frequencies = linspace(0.0, float(SAMPLING_RATE)/2, num=NUM_SAMPLES/2)
    num_samples = obj.num_samples - CUT
    amount_points = int(np.exp2(np.ceil(np.log2(num_samples))+4))
    frequencies = linspace(0.0, float(SAMPLING_RATE)/(2*FREQUENCY_DIVIDER), num=amount_points/(2*FREQUENCY_DIVIDER))
    obj.spectrum_data = ArrayPlotData(frequency=frequencies)

    empty_amplitude = zeros(num_samples/(2*FREQUENCY_DIVIDER))
    obj.spectrum_data.set_data('amplitude', empty_amplitude)

    obj.spectrum_plot = Plot(obj.spectrum_data)
    obj.spectrum_plot.plot(("frequency", "amplitude"), name="Spectrum",
                           color="red")
    obj.spectrum_plot.padding = 50
    obj.spectrum_plot.title = "Spectrum"
    spec_range = obj.spectrum_plot.plots.values()[0][0].value_mapper.range
    spec_range.low = 0.0
    spec_range.high = 0.01
    obj.spectrum_plot.index_axis.title = 'Frequency (Hz)'
    obj.spectrum_plot.value_axis.title = 'Amplitude'

    # Time Series plot
    # times = linspace(0.0, float(NUM_SAMPLES)/SAMPLING_RATE, num=NUM_SAMPLES)
    times = linspace(0.0, float(num_samples)/SAMPLING_RATE, num=num_samples)
    obj.time_data = ArrayPlotData(time=times)
    # empty_amplitude = zeros(NUM_SAMPLES)
    empty_amplitude = zeros(num_samples)
    obj.time_data.set_data('amplitude', empty_amplitude)

    obj.time_plot = Plot(obj.time_data)
    obj.time_plot.plot(("time", "amplitude"), name="Time", color="blue")
    obj.time_plot.padding = 50
    obj.time_plot.title = "Time - White jack"
    obj.time_plot.index_axis.title = 'Time (seconds)'
    obj.time_plot.value_axis.title = 'Amplitude'
    time_range = obj.time_plot.plots.values()[0][0].value_mapper.range
    time_range.low = -0.2
    time_range.high = 0.2

    # Time Series plot1
    # times = linspace(0.0, float(NUM_SAMPLES)/SAMPLING_RATE, num=NUM_SAMPLES)
    obj.time_data1 = ArrayPlotData(time=times)
    # empty_amplitude = zeros(NUM_SAMPLES)
    obj.time_data1.set_data('amplitude', empty_amplitude)

    obj.time_plot1 = Plot(obj.time_data1)
    obj.time_plot1.plot(("time", "amplitude"), name="Time", color="blue")
    obj.time_plot1.padding = 50
    obj.time_plot1.title = "Time - Red jack"
    obj.time_plot1.index_axis.title = 'Time (seconds)'
    obj.time_plot1.value_axis.title = 'Amplitude'
    time_range = obj.time_plot1.plots.values()[0][0].value_mapper.range
    time_range.low = -0.2
    time_range.high = 0.2

    # Spectrogram plot
    spectrogram_data = zeros((amount_points/(2*FREQUENCY_DIVIDER), SPECTROGRAM_LENGTH))
    obj.spectrogram_plotdata = ArrayPlotData()
    print(spectrogram_data, spectrogram_data.shape)
    obj.spectrogram_plotdata.set_data('imagedata', spectrogram_data)
    spectrogram_plot = Plot(obj.spectrogram_plotdata)

    max_time = float(SPECTROGRAM_LENGTH * num_samples) / SAMPLING_RATE
    # max_freq = float(SAMPLING_RATE / 2)
    # boundary = float(C) * obj.num_samples / (4*B * FREQUENCY_DIVIDER)
    boundary = float(C) * num_samples / (4*B * FREQUENCY_DIVIDER)
    print("boundary", boundary, num_samples)
    spectrogram_plot.img_plot('imagedata',
                              name='Spectrogram',
                              xbounds=(0, max_time),
                              # ybounds=(0, max_freq),
                              # ybounds=(0, max_freq * C * num_samples / (2*B*SAMPLING_RATE)),
                              ybounds=(0, boundary),
                              colormap=jet,
                              )
    range_obj = spectrogram_plot.plots['Spectrogram'][0].value_mapper.range
    range_obj.high = 0.5
    range_obj.low = 0.0
    spectrogram_plot.title = 'Spectrogram'
    obj.spectrogram_plot = spectrogram_plot

    container = HPlotContainer()
    container.add(obj.spectrum_plot)
    container.add(obj.time_plot)
    container.add(obj.spectrogram_plot)

    return container

_stream = None


def get_normalized_audio():
    global _stream
    if _stream is None:
        pa = pyaudio.PyAudio()
        _stream = pa.open(format=pyaudio.paInt16, channels=2, rate=SAMPLING_RATE,
                          input=True, frames_per_buffer=NUM_SAMPLES)
    audio_data = fromstring(_stream.read(NUM_SAMPLES), dtype=short)
    audio_data = reshape(audio_data, (NUM_SAMPLES, 2))

    return audio_data / 32768.0


def get_audio_data(num_samples):
    audio_data = get_normalized_audio()

    flanks = get_stream_flanks(audio_data[:, 1])

    # I deleted the first and the last period, todo: is this necessary???
    rising_flanks = map(lambda x: x + CUT/2, flanks[2:-2:2])

    if flanks:
        length = int(round(np.mean(map(lambda x, y: x-y, flanks[1::2], flanks[0::2]))))
        normalized_data = np.mean([audio_data[i:i+length] for i in rising_flanks], axis=0)
    else:
        length = num_samples
        normalized_data = audio_data[0:length]

    return normalized_data, length, flanks


class ZccFilter(HasTraits):

    frequency = Float(0)
    view = View(Item('frequency', label='Frequency zcc', style="readonly"))

    def __init__(self):
        super(ZccFilter, self).__init__()
        self.__window = 0.1

    @staticmethod
    def __get_zero_crossings(data, delay_time=5):
        mean_data = np.mean(data)
        data2 = data - mean_data
        crossings = [i for i, value in enumerate(data2) if data2[i-1]*value < 0]
        return len([value for i, value in enumerate(crossings) if abs(value - crossings[i-1]) > delay_time])

    def calculate_frequency2(self, data):
        crossings = self.__get_zero_crossings(data)
        # print(crossings)
        freq = crossings/2. * SAMPLING_RATE/len(data)
        self.frequency = freq
        return freq

    def calculate_frequency(self, data, flanks):

        num_samples = map(lambda x, y: x-y, flanks[1::2], flanks[0::2])

        crossings_per_period = [self.__get_zero_crossings(data[flanks[2*i]:flanks[2*i]+period])
                                for i, period in enumerate(num_samples)]

        """
        data3 = np.concatenate([data[flanks[2*i]+CUT/2:flanks[2*i+1]-CUT/2] for i in range(len(flanks[::2]))], 1)
        # print(data3)
        crossings = self.__get_zero_crossings(data3, delay_time=10)
        freq = crossings * SAMPLING_RATE/(2*np.mean(num_samples)) / len(num_samples)
        """
        # print(crossings)
        # print(num_samples)
        # print(crossings_per_period)
        freq = np.mean([cross * SAMPLING_RATE/(2*num_samples[i]) for i, cross in enumerate(crossings_per_period)])
        self.frequency = freq
        return freq


class FftFilter(HasTraits):

    frequency = Float(0)

    view = View(Item('frequency', label='Frequency fft', name='', style="readonly", width=-110))

    def __init__(self):
        super(FftFilter, self).__init__()

    def calculate_frequency(self, data, length):
        # frequency = abs(fft(data[:length]))[:length/(2*FREQUENCY_DIVIDER)]

        freq = abs(fft(data[:length]))[:length/(2*FREQUENCY_DIVIDER)].argmax() * float(SAMPLING_RATE)/(
            # 2*FREQUENCY_DIVIDER)/((num_samples - CUT)/(2*FREQUENCY_DIVIDER)-1)
            2*FREQUENCY_DIVIDER)/(len(data)/(2*FREQUENCY_DIVIDER)-1)
        self.frequency = freq

        return freq


class DistanceCalculator(HasTraits):

    distance_zcc = Float(0)
    distance_fft = Float(0)

    zcc_filter = Instance(ZccFilter, ())
    fft_filter = Instance(FftFilter, ())

    view = View(
        Item('zcc_filter', style='custom', show_label=False),
        Item('fft_filter', style='custom', show_label=False),
        VGroup(
            Item('distance_zcc', label='Distance zcc', style='readonly'),
            Item('distance_fft', label='Distance fft', style='readonly'),
        ))

    def __init__(self):
        super(DistanceCalculator, self).__init__()
        self.num_samples = 0

    @staticmethod
    def __calculate_distance(frequency, num_samples):
        return num_samples * C * frequency / (2*B * SAMPLING_RATE)

    def calculate_fft_distance(self, data, length):
        frequency = self.fft_filter.calculate_frequency(data, length)
        self.distance_fft = self.__calculate_distance(frequency, len(data))

    def calculate_zcc_distance(self, data, flanks):
        frequency = self.zcc_filter.calculate_frequency(data, flanks)
        num_samples = int(round(np.mean(map(lambda x, y: x-y, flanks[1::2], flanks[::2]))))
        self.distance_zcc = self.__calculate_distance(frequency, num_samples)

    def calculate_zcc_distance2(self, data):
        frequency = self.zcc_filter.calculate_frequency2(data)
        self.distance_zcc = self.__calculate_distance(float(frequency), len(data))


# HasTraits class that supplies the callable for the timer event.
class TimerController(HasTraits):
    frequency = Float(0)
    frequency_padding = Float(0)

    distance = Float(0)

    en = Float(0)
    padded_en = Float(0)
    d_t = Float(0)
    phase = Float(0)
    accurate_distance_from_freq = Float(0)
    accurate_distance = Float(0)

    distance_calculator = Instance(DistanceCalculator, ())

    view = View(
        HGroup(
            Item("distance_calculator", style='custom', show_label=False),
            Group(Item('frequency', label='Frequency', style='readonly'),
                  Item('frequency_padding', label='Frequency Padding', style='readonly'),
                  Item('distance', label='Distance', style='readonly'),
                  ),
            Group(Item('phase', label='phase', style='readonly'),
                  Item('d_t', label='round trip time', style='readonly'),
                  )))

    def __init__(self):
        super(TimerController, self).__init__()
        self.__measure_clutter = True
        self.__clutter_time = None
        self.__clutter_data = None
        self.__clutter = None

        self.__num_samples = 0
        self.__lambda = float(C) / F0

    def initialize(self, num_samples):
        self.__num_samples = num_samples
        self.distance_calculator.num_samples = num_samples

    @property
    def num_samples(self):
        return self.__num_samples

    def onTimer(self, *args):
        time, initial_length, flanks = get_audio_data(self.__num_samples - CUT)

        if self.__measure_clutter:
            self.__measure_clutter = False
            self.__clutter_time = time[:, 0]

        # self.distance_calculator.calculate_zcc_distance(audio_data, flanks)

        if len(time) > initial_length:
            length = initial_length
            signal = time[:initial_length, 0] - self.__clutter_time
        else:
            length = len(time)
            signal = time[:, 0] #- self.__clutter_time[:len(time)]

        self.distance_calculator.calculate_fft_distance(signal, length)
        self.distance_calculator.calculate_zcc_distance2(signal[:length])

        amount_points = int(np.exp2(np.ceil(np.log2(length))+4))
        final_spectrum = fft(np.roll(signal, -int(initial_length/2)), amount_points)[:amount_points/2]*2./length

        self.frequency = abs(final_spectrum).argmax() * float(SAMPLING_RATE)/amount_points

        period = length/float(SAMPLING_RATE)

        self.distance = period * C * self.frequency / (2*B)

        self.d_t = self.frequency*period/B

        def format_phase(x):
            return (x + np.pi) % (2*np.pi) - np.pi

        k = np.pi*B/period
        rtt_phase = format_phase(2*np.pi*F0 * self.d_t - k*self.d_t**2)

        self.phase = format_phase(np.angle(final_spectrum)[np.argmax(abs(final_spectrum))] - rtt_phase)

        self.spectrum_data.set_data('amplitude', abs(final_spectrum))
        self.time_data.set_data('amplitude', signal)
        self.time_data1.set_data('amplitude', time[:, 1])
        spectrogram_data = self.spectrogram_plotdata.get_data('imagedata')
        spectrogram_data = hstack((spectrogram_data[:, 1:],
                                   transpose([abs(final_spectrum)])))
        print(final_spectrum.size)

        self.spectrogram_plotdata.set_data('imagedata', spectrogram_data)
        self.spectrum_plot.request_redraw()
        return

    def measure_clutter(self):
        self.__measure_clutter = True

    def reset_clutter(self):
        self.__clutter_time = np.zeros(len(self.__clutter_time))


# ============================================================================
# Attributes to use for the plot view.
size = (900, 500)
title = "Audio Spectrum"

# ============================================================================
# Demo class that is used by the demo.py application.
# ============================================================================


class DemoHandler(Handler):

    def closed(self, info, is_ok):
        """ Handles a dialog-based user interface being closed by the user.
        Overridden here to stop the timer once the window is destroyed.
        """
        info.object.timer.Stop()
        return


class Demo(HasTraits):

    plot = Instance(Component)

    controller = Instance(TimerController, ())

    timer = Instance(Timer)

    remove_clutter = Button("Remove Clutter")
    reset_clutter = Button("Reset Clutter")

    traits_view = View(
        Group(
            HGroup(
                Item('remove_clutter', width=.10, height=32, show_label=False),
                Item('reset_clutter', width=.10, height=32, show_label=False)),
            Item("controller", style='custom', show_label=False),
            Item('plot', editor=ComponentEditor(size=size),
                 show_label=False),
            orientation="vertical"),
        resizable=True, title=title,
        width=size[0], height=size[1],
        handler=DemoHandler
    )

    def __init__(self, num_samples, **traits):
        super(Demo, self).__init__(**traits)
        # self.controller.num_samples =
        self.controller.initialize(num_samples)
        self.plot = _create_plot_component(self.controller)

    def _remove_clutter_fired(self):
        self.controller.measure_clutter()

    def _reset_clutter_fired(self):
        self.controller.reset_clutter()

    def edit_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(20, self.controller.onTimer)
        return super(Demo, self).edit_traits(*args, **kws)

    def configure_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(20, self.controller.onTimer)
        return super(Demo, self).configure_traits(*args, **kws)


def get_stream_flanks(stream, delay_time=DELAY_TIME, window=0.5):
    win = (max(stream) - min(stream)) / 4
    final_window = win if win > window else window
    flanks = [i for i, value in enumerate(stream) if abs(stream[i-1] - value) > final_window]
    return sum([[flanks[i-1], val] for i, val in enumerate(flanks) if val - flanks[i - 1] > delay_time], [])


def get_stream_num_samples_per_period(stream):
    num_samples = 0
    flanks = get_stream_flanks(stream)

    if len(flanks) > 5:
        print(flanks[3] - flanks[2])
        # num_samples = int(round(np.mean(map(lambda x, y: x-y, flanks[1::2], flanks[0::2]))))
        # I remove the first and the last block.
        num_samples = int(round(np.mean(map(lambda x, y: x-y, flanks[3:-2:2], flanks[2:-2:2]))))
    return num_samples


if __name__ == "__main__":
    quantity_samples = 500
    while quantity_samples == 0:
        quantity_samples = get_stream_num_samples_per_period(get_normalized_audio()[:, 1])
    print("working", quantity_samples)

    popup = Demo(quantity_samples)
    try:
        popup.configure_traits()
    finally:
        if _stream is not None:
            _stream.close()
        print("closing")
