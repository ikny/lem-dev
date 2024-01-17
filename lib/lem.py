from typing import Any
import numpy.typing as npt

import sounddevice as sd
import numpy as np
import soundfile as sf
import threading


# constants
SAMPLERATE = 44100  # [samples per second]
BLOCKSIZE = 10000  # [samples]
DTYPE = np.int16
STR_DTYPE = "int16"
CHANNELS = 2
LATENCY = 0

METRONOME_SAMPLE_PATH = "lib/samples/metronome.wav"


class Lem():
    def __init__(self) -> None:
        # flags
        self.recording = False
        self.stream_active = True

        self.stream_thread: threading.Thread
        self.tracks: list[npt.NDArray[DTYPE]] = []
        self.recorded_track: npt.NDArray[DTYPE] = np.empty(
            shape=(0, CHANNELS), dtype=DTYPE)
        self.current_frame = 0
        self.len_beat: int  # number of samples per beat

    def set_bpm(self, bpm: int) -> None:
        # initialize the metronome sample and start a stream
        metronome = self.metronome_generator(
            bpm=bpm, path=METRONOME_SAMPLE_PATH)
        self.tracks.append(metronome)

        self.start_stream()

    def metronome_generator(self, bpm: int, path: str) -> npt.NDArray[DTYPE]:
        sample: npt.NDArray[DTYPE]
        sample, samplerate = sf.read(file=path, dtype=STR_DTYPE)

        desired_len = int((60*samplerate)/bpm)
        self.len_beat = desired_len

        if len(sample) <= desired_len:
            # rounding desired_len introduces a slight distortion of bpm
            sample = np.concatenate(
                (sample, np.zeros(shape=(desired_len-len(sample), CHANNELS), dtype=DTYPE)))
        else:
            sample = sample[:desired_len]

        # adjust volume; TODO: this is a magic number, find better practice
        sample = (sample/4).astype(dtype=DTYPE)

        return sample

    def post_production(self) -> None:
        """ cut/fill newly recorded track to bpm, add to tracks and clear recorded_track  """
        remainder = len(self.recorded_track) % self.len_beat

        if remainder > self.len_beat/2:
            zeros = np.zeros(
                shape=(self.len_beat-remainder, CHANNELS), dtype=DTYPE)
            recorded_track = np.concatenate([self.recorded_track, zeros])
        elif remainder <= self.len_beat/2:
            recorded_track = self.recorded_track[:len(
                recorded_track)-remainder]

        self.tracks.append(recorded_track)
        self.recorded_track = np.empty(shape=(0, CHANNELS), dtype=DTYPE)

    def start_stream(self) -> None:
        """ Make a new thread, in which the stream will be active """
        self.stream_thread = threading.Thread(target=self.main)
        self.stream_thread.start()
        # the thread will end 

    def terminate(self) -> None:
        self.stream_thread.join()    

    def main(self) -> None:
        """ processes the audio """

        def callback(indata: npt.NDArray[DTYPE], outdata: npt.NDArray[DTYPE],
                     frames: int, time: Any, status: sd.CallbackFlags) -> None:

            if status:
                print(status)

            if self.recording:
                self.recorded_track = np.concatenate(
                    [self.recorded_track, indata])

            # mixer & slicer
            num_tracks = len(self.tracks)
            data = (indata/(num_tracks + 1)).astype(dtype=DTYPE)

            for track in self.tracks:
                # slice
                start = self.current_frame % len(track)
                end = (self.current_frame+frames) % len(track)
                if end < start:
                    track_slice = np.concatenate(
                        (track[start:], track[:end]))
                else:
                    track_slice = track[start:end]
                # mix
                track_slice = (track_slice/(num_tracks+1)).astype(dtype=DTYPE)

                data += track_slice

            outdata[:] = data
            self.current_frame += frames

        with sd.Stream(samplerate=SAMPLERATE, blocksize=BLOCKSIZE, dtype=STR_DTYPE,
                       channels=CHANNELS, callback=callback):
            while self.stream_active:
                pass
