#!/usr/bin/python3.4
import matplotlib.pyplot as plt
import scipy as sp
import numpy as np

f = 400
initial_phase = np.pi / 2
d_time = 1/40e3
# stop = 0.0145
stop = 0.0201
t = np.arange(0, stop, d_time)
signal1 = np.cos(2*np.pi*f*t + initial_phase)
# signal = np.cos(2*np.pi*f*t + initial_phase)
# signal = np.sin(2*np.pi*f*t)
print(t.size/2)
# signal = np.roll(np.sin(2*np.pi*f*t), -250)
signal = np.concatenate((signal1, signal1, signal1, signal1, signal1, signal1))
# print(signal.size)
# print(np.fft.fftfreq(n, d=d_time))
plt.grid(True)
max_freq = 1000
"""
n = signal.size
index_max_freq = max_freq*n*d_time +1 
freq_values = np.fft.fftfreq(n, d=d_time)[:index_max_freq]

plt.plot(freq_values, abs(np.fft.fft(signal, n)[:index_max_freq])/signal.size, 'k')
# plt.plot(np.fft.fftshift(np.fft.fftfreq(n, d=d_time)[:index_max_freq]), np.fft.fftshift(np.fft.fft(signal, n)[:index_max_freq].real/signal.size), 'k')


n = 1000
index_max_freq = max_freq*n*d_time + 1
freq_values = np.fft.fftfreq(n, d=d_time)[:index_max_freq]
plt.plot(freq_values, abs(np.fft.fft(signal, n)[:index_max_freq]/signal.size), 'b')
# plt.plot(np.fft.fftshift(np.fft.fftfreq(n, d=d_time)), np.fft.fftshift(np.fft.fft(signal, n)).real/signal.size, 'b')
"""
n = 10000
index_max_freq = int(max_freq*n*d_time + 1)
freq_values = np.fft.fftfreq(n, d=d_time)[:index_max_freq]
ffft = np.fft.fft(signal, n)[:index_max_freq]/signal.size
# ffft = np.abs(np.fft.fft(signal, n)[:index_max_freq].real)/signal.size
# ffft = np.abs(np.fft.fftshift(np.fft.fft(signal, n)).real)/signal.size
plt.plot(freq_values, abs(ffft), 'r')
# plt.text(20, .25, np.fft.fftfreq(n, d=d_time)[np.argmax(abs(ffft.real))])
# plt.plot(np.fft.fftshift(np.fft.fftfreq(n, d=d_time)), ffft, 'r')
# plt.text(20, .25, np.fft.fftshift(np.fft.fftfreq(n, d=d_time))[np.argmax(ffft)])

plt.plot(freq_values, np.angle(ffft), 'k')
plt.text(20, 0.45, "freq Peak: " + str(freq_values[np.argmax(abs(ffft))]) + "\nphase in Peak: " + str(np.angle(ffft, deg=True)[np.argmax(abs(ffft))]))


# plt.plot(np.fft.fftshift(np.fft.fftfreq(n, d=d_time)), np.angle(np.fft.fftshift(np.fft.fft(signal, n))/signal.size), 'k')
# plt.plot(np.fft.fftfreq(n, d=d_time)[:n/2], np.fft.fft(signal, n).real[:n/2]/signal.size)


plt.figure()
# plt.plot(t, signal1, 'k')
plt.plot(signal, 'b')
plt.plot(np.fft.ifft(np.fft.fft(signal)).real, 'r')

# If I perform an fftshift I can't obtain the real signal
# plt.plot(t, np.fft.ifft(np.fft.fftshift(np.fft.fft(signal).real)).real)
plt.show()

# Conclusion tengo que agarrar mas periodos.... que gil como no lo pense antes...
# tengo que mirarlo en el simulador que es lo que pasa....