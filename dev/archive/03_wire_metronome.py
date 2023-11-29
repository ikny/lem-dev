from typing import Any, Tuple, Literal
import sounddevice as sd
import numpy as np
import soundfile as sf


""" 
The purpose of this script is to test the capabilities of the callback 
by mixing metronome with the input
"""

SAMPLERATE = 44100  # [samples per second]
BLOCKSIZE = 5  # [samples]
DTYPE = np.int16
LATENCY = 0

METRONOME_SAMPLE_PATH = "lib/samples/metronome.wav"


def metronome_generator(bpm: int, path: str) -> np.ndarray:  # type: ignore
    sample, fs = sf.read(file=path, dtype="int16")
    desired_len = int((60*fs)/bpm)

    if len(sample) <= desired_len:
        # rounding desired_len introduces a distortion of bpm
        sample = np.concatenate(
            (sample, np.zeros(shape=(desired_len-len(sample), 2), dtype="int16")))
    else:
        sample = sample[:desired_len]

    return sample  # type: ignore


if __name__ == "__main__":
    # initialize metronome
    bpm = int(input("bpm: "))
    metronome = metronome_generator(bpm=bpm, path=METRONOME_SAMPLE_PATH)/4

    # initialize callback
    current_frame = 0

    def callback(indata, outdata, frames, time, status):  # type:ignore
        global current_frame
        global metronome  # in more general version this would be global tracks
        if status:
            print(status)

        # slicer
        start = current_frame % len(metronome)
        end = (current_frame+BLOCKSIZE) % len(metronome)
        if end < start:
            metronome_slice = np.concatenate(
                (metronome[start:], metronome[:end]))
        else:
            metronome_slice = metronome[start:end]

        # mixer
        data = (metronome_slice + indata)/2

        outdata[:] = data
        current_frame += BLOCKSIZE

    try:
        with sd.Stream(samplerate=SAMPLERATE, blocksize=BLOCKSIZE,
                       dtype=DTYPE, channels=2, callback=callback):
            input("press enter to quit")
    finally:
        print("Good bye!")
