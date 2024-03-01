import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd


data = np.load("export.npy")
sd.play(data)

fig, axis = plt.subplots()

axis.axhline(32767, 0)
axis.axhline(-32768, 0)
y1 = np.array([i[0] for i in data])
y2 = np.array([i[1] for i in data])
x = np.array([i for i in range(len(data))])
axis.plot(x, y1)
axis.plot(x, y2)

plt.show()
