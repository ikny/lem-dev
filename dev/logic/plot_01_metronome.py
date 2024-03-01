from typing import Any, List
import numpy.typing as npt

import numpy as np
import soundfile as sf
import matplotlib
import matplotlib.pyplot as plt

DTYPE = np.int16
STR_DTYPE = "int16"
CHANNELS = 2

PATH = "lib/samples/metronome.wav"


plots: dict[str, npt.NDArray[Any]] = {}


def metronome_generator(bpm: int, path: str) -> npt.NDArray[DTYPE]:
    global plots

    sample: npt.NDArray[DTYPE]
    sample, fs = sf.read(file=path, dtype=STR_DTYPE)
    plots["sample int16"] = sample

    sample_float, _ = sf.read(file=path)
    plots["sample float"] = sample_float

    desired_len = int((60*fs)/bpm)

    if len(sample) <= desired_len:
        # rounding desired_len introduces a distortion of bpm
        sample = np.concatenate(
            (sample, np.zeros(shape=(desired_len-len(sample), CHANNELS), dtype=DTYPE)))
    else:
        sample = sample[:desired_len]

    plots["rounded sample"] = sample

    return sample


metronome_generator(bpm=50, path=PATH)

fig: matplotlib.figure.Figure
axes: List[matplotlib.axes.Axes]
fig, axes = plt.subplots(ncols=len(plots))

for plot, axis in zip(plots, axes):

    axis.axhline(32767, 0)
    axis.axhline(-32768, 0)

    y1 = np.array([i[0] for i in plots[plot]])
    y2 = np.array([i[1] for i in plots[plot]])
    x = np.array([i for  i in range(len(plots[plot]))])

    axis.plot(x, y1)
    axis.plot(x, y2)

    axis.set_xlabel(f"{plot}")

plt.show()