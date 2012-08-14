#Copyright (C) 2012 Sergio Gonzalez

#Permission is hereby granted, free of charge, to any person obtaining
#a copy of this software and associated documentation files (the "Software"), to
#deal in the Software without restriction, including without limitation the
#rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is furnished
#to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import alsaaudio as alsa
import array
import math
import random
import time


RATE = 44100
FRAME_SIZE = 16  # In bits
PERIOD = 32  # Num. frames in chunk.
CHUNKS_PER_SEC = RATE / PERIOD

frequencies = {  # Parsed from http://www.phy.mtu.edu/~suits/notefreqs.html
    'C0': 16.35,
    'Cs0': 17.32,
    'D0': 18.35,
    'Ds0': 19.45,
    'E0': 20.60,
    'F0': 21.83,
    'Fs0': 23.12,
    'G0': 24.50,
    'Gs0': 25.96,
    'A0': 27.50,
    'As0': 29.14,
    'B0': 30.87,
    'C1': 32.70,
    'Cs1': 34.65,
    'D1': 36.71,
    'Ds1': 38.89,
    'E1': 41.20,
    'F1': 43.65,
    'Fs1': 46.25,
    'G1': 49.00,
    'Gs1': 51.91,
    'A1': 55.00,
    'As1': 58.27,
    'B1': 61.74,
    'C2': 65.41,
    'Cs2': 69.30,
    'D2': 73.42,
    'Ds2': 77.78,
    'E2': 82.41,
    'F2': 87.31,
    'Fs2': 92.50,
    'G2': 98.00,
    'Gs2': 103.83,
    'A2': 110.00,
    'As2': 116.54,
    'B2': 123.47,
    'C3': 130.81,
    'Cs3': 138.59,
    'D3': 146.83,
    'Ds3': 155.56,
    'E3': 164.81,
    'F3': 174.61,
    'Fs3': 185.00,
    'G3': 196.00,
    'Gs3': 207.65,
    'A3': 220.00,
    'As3': 233.08,
    'B3': 246.94,
    'C4': 261.63,
    'Cs4': 277.18,
    'D4': 293.66,
    'Ds4': 311.13,
    'E4': 329.63,
    'F4': 349.23,
    'Fs4': 369.99,
    'G4': 392.00,
    'Gs4': 415.30,
    'A4': 440.00,
    'As4': 466.16,
    'B4': 493.88,
    'C5': 523.25,
    'Cs5': 554.37,
    'D5': 587.33,
    'Ds5': 622.25,
    'E5': 659.26,
    'F5': 698.46,
    'Fs5': 739.99,
    'G5': 783.99,
    'Gs5': 830.61,
    'A5': 880.00,
    'As5': 932.33,
    'B5': 987.77,
    'C6': 1046.50,
    'Cs6': 1108.73,
    'D6': 1174.66,
    'Ds6': 1244.51,
    'E6': 1318.51,
    'F6': 1396.91,
    'Fs6': 1479.98,
    'G6': 1567.98,
    'Gs6': 1661.22,
    'A6': 1760.00,
    'As6': 1864.66,
    'B6': 1975.53,
    'C7': 2093.00,
    'Cs7': 2217.46,
    'D7': 2349.32,
    'Ds7': 2489.02,
    'E7': 2637.02,
    'F7': 2793.83,
    'Fs7': 2959.96,
    'G7': 3135.96,
    'Gs7': 3322.44,
    'A7': 3520.00,
    'As7': 3729.31,
    'B7': 3951.07,
    'C8': 4186.01,
    'Cs8': 4434.92,
    'D8': 4698.64,
    'Ds8': 4978.03,
}

c_major_scale = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

def init_pcm():
    import alsaaudio as alsa
    pcm = alsa.PCM(type=alsa.PCM_PLAYBACK,
                   mode=alsa.PCM_NORMAL)
    pcm.setchannels(1)
    return pcm

def synth_sine(chunk_i, note):
    'Return a chunk of sinewave data for a chunk of time.'
    freq = frequencies[note]
    ticks = xrange((chunk_i - 1) * PERIOD, chunk_i * PERIOD)
    frames = array.array('h', [int(2 ** 12 * math.sin(2 * math.pi * freq * tick * 1.0 / RATE)) for tick in ticks])
    return frames

def play_chunk(pcm, chunk):
        pcm.write(chunk.tostring())

def play(pcm, generators, length_sec):
    for i in xrange(length_sec * CHUNKS_PER_SEC):
        time = float(i) / CHUNKS_PER_SEC
        chunk = array.array('h', [0 for x in xrange(PERIOD)])
        for generator in generators:
            note = generator(time)
            if note:
                subchunk = synth_sine(i, note)
                for chunk_i in xrange(PERIOD):
                    chunk[chunk_i] = chunk[chunk_i] + subchunk[chunk_i]
        play_chunk(pcm, chunk)

if __name__ == '__main__':
    pcm = init_pcm()
    # Randomly-generated music:
    duration = 40

    bass_notes = [c_major_scale[random.randint(0, 6)] + str(random.randint(2,3)) for i in xrange(duration)]
    print bass_notes
    def bass_line(time):
        if time >= duration:
            return None
        return bass_notes[int(time)]
    def melody(time):
        time = time % 7
        if time >= 7:
            return None
        if time <= 4:
            return c_major_scale[int(time)] + '4'
        else:
            return c_major_scale[7 - int(time)] + '4'
    note_duration = 0.1
    solo_notes = [c_major_scale[random.randint(0, 6)] + str(random.randint(1,6)) for i in xrange(int(duration / note_duration))]
    print solo_notes
    def random_solo(time):
        return solo_notes[int(time / note_duration)]

    play(pcm, [random_solo], 3)
    from threading import Thread
    t = Thread(target = lambda: play(pcm, [melody, bass_line, random_solo], duration))
    t.start()
    time.sleep(duration)
    play(pcm, [bass_line], 5)
