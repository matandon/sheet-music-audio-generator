import numpy as np
from scipy.io import wavfile
import os
from playsound import playsound

#put this stuff into class and all the beginning math can go in init)

# code gotten from https://towardsdatascience.com/music-in-python-2f054deb41f4

class playPiece(object):
    def __init__(self, frequency, i, j, z):
        self.frequency = frequency

        self.i = i
        self.j = j
        self.z = z

        # Pure sine wave
        sine_wave = self.get_sine_wave(self.frequency, duration=2, amplitude=2048)
        wavfile.write('note.wav', rate=44100, data=sine_wave.astype(np.int16))

        # Load data from wav file
        #print(os.getcwd() + '\\piano.wav')
        self.sample_rate, pianoC = wavfile.read(os.getcwd() + '\\piano.wav')

        #FFT    
        t = np.arange(pianoC.shape[0])
        freq = np.fft.fftfreq(t.shape[-1])*self.sample_rate
        sp = np.fft.fft(pianoC)

        # Get positive frequency
        idx = np.where(freq > 0)[0]
        freq = freq[idx]
        sp = sp[idx]

        # Get dominant frequencies
        sort = np.argsort(-abs(sp.real))[:100]
        dom_freq = freq[sort]

        # Round and calculate amplitude ratio
        freq_ratio = np.round(dom_freq/frequency)
        unique_freq_ratio = np.unique(freq_ratio)
        amp_ratio = abs(sp.real[sort]/np.sum(sp.real[sort]))
        factor = np.zeros((int(unique_freq_ratio[-1]), ))
        for i in range(factor.shape[0]):
            idx = np.where(freq_ratio==i+1)[0]
            factor[i] = np.sum(amp_ratio[idx])
        
        self.factor = factor/np.sum(factor)

    def get_sine_wave(self, frequency, duration, sample_rate=44100, amplitude=2048):
        t = np.linspace(0, duration, int(sample_rate*duration)) # Time axis
        wave = amplitude*np.sin(2*np.pi*frequency*t)
        return wave

    def play(self, duration):
        note = self.apply_overtones(duration = duration)
        wavfile.write(f"new note {self.z} {self.j} {self.i}.wav", self.sample_rate, note.astype(np.int16))
        playsound(f"new note {self.z} {self.j} {self.i}.wav")

    def apply_overtones(self, duration, sample_rate=44100, amplitude=2048):
        assert abs(1-sum(self.factor)) < 1e-8
        
        frequencies = np.minimum(np.array([self.frequency*(x+1) for x in range(len(self.factor))]), sample_rate//2)
        amplitudes = np.array([amplitude*x for x in self.factor])
           
        fundamental = self.get_sine_wave(frequencies[0], duration, sample_rate, amplitudes[0])
        for i in range(1, len(self.factor)):
            overtone = self.get_sine_wave(frequencies[i], duration, sample_rate, amplitudes[i])
            fundamental += overtone
        return fundamental

#piece = playPiece(523.2511, 1)
#note = piece.play(0.25)