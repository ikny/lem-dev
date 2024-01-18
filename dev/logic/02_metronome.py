import sounddevice as sd
import numpy as np
import soundfile as sf

data, fs = sf.read(file="lem-dev/lib/samples/metronome.wav", dtype="int16")

bpm=int(input("bpm: "))

desired_len = (60*fs)/bpm

# rounding desired_len introduces a distortion of bpm 
data = np.concatenate((data, np.zeros(shape=(int(desired_len)-len(data), 2), dtype="int16")))

sd.play(data=np.concatenate([data for i in range(8)]))
sd.wait()