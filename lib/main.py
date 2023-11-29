from typing import Any
import sounddevice as sd
import numpy as np

class MixingPult():
    def __init__(self) -> None:
        self.tracks: list[np.ndarray] = [] # type: ignore
        self.settings: dict[str, Any] = {}
        self.stream = ...

class Track():
    def __init__(self, name: str, content: np.ndarray) -> None: # type:ignore
        self.name = name
        self.content = content
