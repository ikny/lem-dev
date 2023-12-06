import numpy as np
import sounddevice as sd

SAMPLERATE = 44100  # [samples per second]
BLOCKSIZE = 10  # [samples]
DTYPE = np.int16
LATENCY = 0


GENERATED_FREQUENCY = 40  # [Hz]
VOLUME = 16383  # half of the amplitude of int16

# init the sample
# formula: volume*sin(2*pi*x*frequency)
arr = np.arange(SAMPLERATE)
arr = np.divide(arr, SAMPLERATE)
arr = np.multiply(arr, 2*np.pi*GENERATED_FREQUENCY)
sine = np.sin(arr)*VOLUME
sine = np.array([sine], dtype=DTYPE)
sine = sine.transpose()

print(max(sine))

# now the sd part:

current_frame = 0


def callback(indata, outdata, frames, time, status):
    global current_frame
    if status:
        print(status)
    outdata[:] = sine[current_frame %
                      len(sine):current_frame % len(sine)+BLOCKSIZE]
    current_frame += BLOCKSIZE


with sd.Stream(samplerate=SAMPLERATE, blocksize=BLOCKSIZE,
               dtype=DTYPE, channels=1, callback=callback):
    print('#' * 80)
    print('press Return to quit')
    print('#' * 80)
    input()
