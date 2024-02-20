# types
from typing import Any
import numpy.typing as npt
import numpy as np

from enum import Enum


class Queue():
    """A simple queue that can only push and pop.
    """

    def __init__(self) -> None:
        self._items: list[Any] = []

    def push(self, item: Any) -> None:
        self._items.append(item)

    def pop(self) -> Any:
        return self._items.pop(0)

    def empty(self) -> bool:
        return bool(self._items)


class CircularBuffer():
    def __init__(self, length: int, channels: int, dtype: npt.DTypeLike) -> None:
        self._length = length
        self._data = np.empty(
            shape=(self._length, channels), dtype=dtype)
        self._index = 0

    def write(self, data: npt.NDArray) -> None:  # type: ignore
        len_data = len(data)
        total_len = self._index + len_data
        if len_data > self._length:
            raise NotImplementedError(
                "Data too long! This circular buffer cannot write longer data than its set length.")
        if total_len > self._length:
            left = self._length - self._index
            overflown = len_data - left
            self._data[self._index:] = data[:left]
            self._data[:overflown] = data[left:]
        else:
            self._data[self._index:total_len] = data
        self._index = total_len % self._length

    def start_to_index(self) -> npt.NDArray:  # type: ignore
        return self._data[:self._index]

    def position(self) -> int:
        return self._index


class UserRecordingEvents(Enum):
    START = 1
    STOP = 2
