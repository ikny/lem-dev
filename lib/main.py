import sounddevice as sd
import numpy as np


class MixingPult():
    def __init__(self) -> None:
        self.SAMPLERATE = 44100  # [samples per second]
        self.BLOCKSIZE = 5  # [samples]
        self.DTYPE = np.int16
        self.LATENCY = 0

        self.tracks: list[np.ndarray] = []  # type: ignore
        self.stream = ...

    def callback(self):
        """
        Handles audio
        """
        ...

    def mix_tracks(self):
        """ 
        By computing a weighed average of track blocks joins them into one.
        """
        ...

    def cut_tracks(self):
        """ 
        Gets next block of every track. 
        """
        ...


class Track():
    def __init__(self, name: str, content: np.ndarray) -> None:  # type:ignore
        self.name = name
        self.content = content
