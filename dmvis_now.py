import matplotlib
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.figure import Figure

font = {"size": 9}
matplotlib.rc("font", **font)

fig = plt.figure(figsize=(18, 8), layout="constrained")
fig.subplots_adjust(wspace=0.5, hspace=0.3)
fig.suptitle("Uji Otonom", fontsize=12)
gs = fig.add_gridspec(2, 4)
ax01 = fig.add_subplot(gs[0, 0])
ax012 = ax01.twinx()
ax02 = fig.add_subplot(gs[0, 1])
ax03 = fig.add_subplot(gs[1, 0:2])
ax04 = ax03.twinx()
ax05 = fig.add_subplot(gs[:, 2:4])

ax01.set_title("TTC and DTC vs Time")
ax02.set_title("Distance vs Time")
ax03.set_title("Velocity, state, and Command vs Time")
ax05.set_title("Bird Eye View")

ax01.set_ylim(0, 50)
ax012.set_ylim(0, 50)
ax02.set_ylim(0, 70)
ax03.set_ylim(-6, 8)
ax04.set_ylim(-6, 8)
ax05.set_ylim(-1, 100)

ax01.set_xlim(0, 10.0)
ax012.set_xlim(0, 10.0)
ax02.set_xlim(0, 10.0)
ax03.set_xlim(0, 10.0)
ax04.set_xlim(0, 10.0)
ax05.set_xlim(-25, 25)

ax01.grid(True)
ax02.grid(True)
ax03.grid(True)
ax05.grid(True)

ax01.set_xlabel("t")
ax01.set_ylabel("TTC")
ax012.set_ylabel("DTC")
ax02.set_xlabel("t")
ax02.set_ylabel("m")
ax03.set_xlabel("t")
ax03.set_ylabel("m/s")
ax04.set_ylabel("MC level")
ax05.set_xlabel("x")
ax05.set_ylabel("y")

ax05.axvspan(-1.2, 1.3, facecolor="gray", alpha=0.5)

ax01.plot([1, 2])
ax02.plot([1, 2])
ax03.plot([1, 2])
ax05.plot([1, 2])

plt.show()
