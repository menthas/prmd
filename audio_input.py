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
            'specflux', self.window_size, self.buffersize, self.sample_rate)
        self.onset.set_threshold(0.3)
        self.onset.set_silence(-20.)
        self.tempo = aubio.tempo(
            'default', self.window_size, self.buffersize, self.sample_rate)

        self.energy = aubio.specdesc('specflux', self.buffersize * 2)
        self.pv = aubio.pvoc(self.buffersize * 2, self.buffersize)

        self.pitch = aubio.pitch(
            "yinfft", self.window_size, self.buffersize, self.sample_rate)
        self.pitch.set_unit("midi")
        self.pitch.set_tolerance(0.8)

        self.py_audio = pyaudio.PyAudio()

    def init_stream(self, input_device_index=None, channels=None):
        if not input_device_index or not channels:
            input_device_index, channels = self._get_input_device()

        logging.info("Using input device %s with %s channels" % (
            input_device_index, channels
        ))

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
                        data.get('name'), data.get('defaultSampleRate'))
                )
                print(data)
        if len(valid_devices) == 0:
            logging.error('AudioInput: Couldn\'t find a valid input device')
            raise Exception('AudioInput: invalid input device')
        if len(valid_devices) > 1:
            logging.info(
                'AudioInput: Found the following devices, using the last one:'
                '\n%s' % '\n'.join([
                    '%s. %s (i:%s ch:%s SR:%s)' % (
                        i, info[2], info[1], info[0], info[3]
                    )
                    for i, info in enumerate(valid_devices)
                ])
            )
        return valid_devices[-1][1], valid_devices[-1][0]

    def register_read_listener(self, callback):
        self._read_listeners.append(callback)
        return len(self._read_listeners)

    def unregister_read_listener(self, callback):
        self._read_listeners.remove(callback)

    def read_loop(self):
        _time = time.time()
        while True:
            f = numpy.fromstring(
                self.stream.read(self.buffersize), dtype=numpy.dtype('<f'))

            data = {
                'is_beat': self.tempo(f),
                'onset': self.onset(f),
                'left_energy': 30,
                'energy': self.energy(self.pv(f[:self.buffersize]))[0],
                'pitch_midi': int(self.pitch(f)[0])
            }
            data['energy_norm'] = min(1, data['energy'] / 1500)
            data['pitch_norm'] = min(1, data['pitch_midi'] / 137)

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
