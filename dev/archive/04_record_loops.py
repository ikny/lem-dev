from typing import Any
import numpy.typing as npt

import sounddevice as sd
import numpy as np
import soundfile as sf
import threading


""" 
The purpose of this script is to simulate the logic behind recording and looping 
before trying to do it with class abstraction.
"""

SAMPLERATE = 44100  # [samples per second]
BLOCKSIZE = 10000  # [samples]
DTYPE = np.int16
STR_DTYPE = "int16"
CHANNELS = 2
LATENCY = 0

METRONOME_SAMPLE_PATH = "lib/samples/metronome.wav"

recording = False
stream_active = True

tracks: list[npt.NDArray[DTYPE]] = []
recorded_track: npt.NDArray[DTYPE] = np.empty(shape=(0, CHANNELS), dtype=DTYPE)
current_frame = 0
len_beat: int  # number of samples per beat


def metronome_generator(bpm: int, path: str) -> npt.NDArray[DTYPE]:
    global len_beat

    sample: npt.NDArray[DTYPE]
    sample, fs = sf.read(file=path, dtype=STR_DTYPE)

    desired_len = int((60*fs)/bpm)
    len_beat = desired_len

    if len(sample) <= desired_len:
        # rounding desired_len introduces a distortion of bpm
        sample = np.concatenate(
            (sample, np.zeros(shape=(desired_len-len(sample), CHANNELS), dtype=DTYPE)))
    else:
        sample = sample[:desired_len]

    sample = (sample/4).astype(dtype=DTYPE)

    return sample


def input_checker() -> None:
    """ sets the flags in response to user console inputs """
    global recording
    global stream_active

    while True:
        msg = input("press enter to start recording, or q to quit ").lower()
        if msg == "q":
            stream_active = False
            break
        recording = True

        msg = input("press enter to stop recording, or q to quit ").lower()
        if msg == "q":
            stream_active = False
            break
        recording = False

        post_production()


def post_production() -> None:
    """ cut/fill newly recorded track to bpm, add to tracks and clear recorded_track  """
    global tracks
    global recorded_track
    global len_beat

    remainder = len(recorded_track) % len_beat
    if remainder > len_beat/2:
        zeros = np.zeros(shape=(len_beat-remainder, CHANNELS), dtype=DTYPE)
        recorded_track = np.concatenate([recorded_track, zeros])
    elif remainder < len_beat/2:
        recorded_track = recorded_track[:len(recorded_track)-remainder]

    tracks.append(recorded_track)
    recorded_track = np.empty(shape=(0, CHANNELS), dtype=DTYPE)


def initialize_metronome() -> None:
    global tracks
    # initialize metronome
    bpm = int(input("bpm: "))
    metronome = metronome_generator(bpm=bpm, path=METRONOME_SAMPLE_PATH)
    tracks.append(metronome)


def main() -> None:
    """ processes the audio """
    global stream_active

    def callback(indata: npt.NDArray[DTYPE], outdata: npt.NDArray[DTYPE],
                 frames: int, time: Any, status: sd.CallbackFlags) -> None:
        global current_frame
        global tracks
        global recorded_track

        if status:
            print(status)

        if recording:
            recorded_track = np.concatenate([recorded_track, indata])

        # mixer & slicer
        num_tracks = len(tracks)
        data = (indata/(num_tracks + 1)).astype(dtype=DTYPE)

        for i, track in enumerate(tracks):
            # slice
            start = current_frame % len(track)
            end = (current_frame+frames) % len(track)
            if end < start:
                track_slice = np.concatenate(
                    (track[start:], track[:end]))
            else:
                track_slice = track[start:end]
            # mix
            track_slice = (track_slice/(num_tracks+1)).astype(dtype=DTYPE)

            data += track_slice

        outdata[:] = data
        current_frame += frames

    try:
        with sd.Stream(samplerate=SAMPLERATE, blocksize=BLOCKSIZE, dtype=STR_DTYPE,
                       channels=CHANNELS, callback=callback):
            while stream_active:
                pass
    finally:
        print("Good bye!")


if __name__ == "__main__":
    initialize_metronome()

    audio_thread = threading.Thread(target=main)
    input_thread = threading.Thread(target=input_checker)

    audio_thread.start()
    input_thread.start()

    audio_thread.join()
    input_thread.join()
