#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import numpy
import pyaudio
import aubio
import time


class AudioInput(object):
    sample_rate = 44100
    buffersize = 512
    max_energy = 5000

    _read_listeners = []

    def __init__(self, sample_rate=None, buffersize=None):
        self.sample_rate = sample_rate or self.sample_rate
        self.buffersize = buffersize or self.buffersize
        self.window_size = self.buffersize * 2
        self.stream = None

        self.onset = aubio.onset(
            'default', self.window_size, self.buffersize, self.sample_rate)
        self.onset.set_threshold(0.3)
        self.onset.set_silence(-20.)
        self.tempo = aubio.tempo(
            'default', self.window_size, self.buffersize, self.sample_rate)

        self.py_audio = pyaudio.PyAudio()

    def init_stream(self, input_device_index=None, channels=None):
        if not input_device_index or not channels:
            input_device_index, channels = self._get_input_device()

        self.stream = self.py_audio.open(
            format=pyaudio.paFloat32,
            channels=2,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.buffersize,
            input_device_index=input_device_index)

    def _get_input_device(self):
        valid_devices = []
        for i in range(self.py_audio.get_device_count()):
            data = self.py_audio.get_device_info_by_index(i)
            if data.get('maxInputChannels', 0) > 0:
                valid_devices.append(
                    (data['maxInputChannels'], data.get('index'),
                        data.get('name'))
                )
        if len(valid_devices) == 0:
            logging.error('AudioInput: Couldn\'t find a valid input device')
            raise Exception('AudioInput: invalid input device')
        if len(valid_devices) > 1:
            logging.info(
                'AudioInput: Found the following devices, using the last one:'
                '\n%s' % '\n'.join([
                    '%s. %s' % (i, info[2])
                    for i, info in enumerate(valid_devices)
                ])
            )
        return valid_devices[-1][1], valid_devices[-1][0]

    def register_read_listener(self, callback):
        self._read_listeners.append(callback)
        return len(self._read_listeners)

    def unregister_read_listener(self, callback):
        self._read_listeners.remove(callback)

    def fft(self, data, log_scale=False):
        left, right = numpy.split(numpy.abs(numpy.fft.fft(data)), 2)
        ys = numpy.add(left, right[::-1])
        if log_scale:
            ys = numpy.multiply(20, numpy.log10(ys))
        return ys

    def read_loop(self):
        _time = time.time()
        while True:
            f = numpy.fromstring(
                self.stream.read(self.buffersize), dtype=numpy.dtype('<f'))
            fft = self.fft(f)
            tone = (
                numpy.mean(numpy.log10(fft) * numpy.arange(len(fft)))
                if max(fft) > 0 else 0
            )
            if tone > self.max_energy:
                tone = self.max_energy
            elif tone < -1 * self.max_energy:
                tone = -1 * self.max_energy
            tone /= float(self.max_energy)
            data = {
                'is_beat': self.tempo(f),
                'onset': self.onset(f),
                'energy': numpy.sum(fft),
                # this is the overall tone of the song, the sign indicates
                # lower/high spectrom. the magnitude indicates intensity
                'tone': tone
            }

            time_diff = time.time() - _time
            _time = time.time()
            for callback in self._read_listeners:
                callback(data, time_diff=time_diff)

    def drop_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.py_audio.terminate()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    t = AudioInput()
    t.init_stream()
    t.read_loop()
