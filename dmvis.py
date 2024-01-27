from pydantic import BaseModel


class TramState(BaseModel):
    x: float
    y: float
    v: float
    t: float


class DMPlot(BaseModel):
    tram_state: TramState


class DMVisualisation:

    def __init__(self):
        pass

import matplotlib
import numpy as np

from matplotlib import pyplot as plt
import matplotlib.animation as animation


# Sent for figure
font = {"size": 9}
matplotlib.rc("font", **font)

# Setup figure and subplots
f0 = plt.figure(num=0, figsize=(18, 8))  # , dpi = 100)
f0.suptitle("Uji Otonom", fontsize=12)
ax01 = plt.subplot2grid((2, 4), (0, 0))
ax012 = ax01.twinx()
ax02 = plt.subplot2grid((2, 4), (0, 1))
ax03 = plt.subplot2grid((2, 4), (1, 0), colspan=2, rowspan=1)
ax04 = ax03.twinx()
ax05 = plt.subplot2grid((2, 4), (0, 2), colspan=2, rowspan=2)
plt.subplots_adjust(wspace=0.5, hspace=0.3)

# Set titles of subplots
ax01.set_title("TTC and DTC vs Time")
ax02.set_title("Distance vs Time")
ax03.set_title("Velocity, state, and Command vs Time")
ax05.set_title("Bird Eye View")

# set y-limits
ax01.set_ylim(0, 50)
ax012.set_ylim(0, 50)
ax02.set_ylim(0, 70)
ax03.set_ylim(-6, 8)
ax04.set_ylim(-6, 8)
# ax05.set_ylim(-600,-520)
# ax05.set_ylim(1455,1465)
# ax05.set_ylim(1455,1465)
ax05.set_ylim(-1, 100)

# sex x-limits
ax01.set_xlim(0, 10.0)
ax012.set_xlim(0, 10.0)
ax02.set_xlim(0, 10.0)
ax03.set_xlim(0, 10.0)
ax04.set_xlim(0, 10.0)
# ax05.set_xlim(-600,-200)
# ax05.set_xlim(-600,-520)
ax05.set_xlim(-25, 25)

# Turn on grids
ax01.grid(True)
ax02.grid(True)
ax03.grid(True)
ax05.grid(True)

# set label names
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


ystate = np.zeros(0)

yd = np.zeros(0)
ysd = np.zeros(0)

yr = np.zeros(0)
ys = np.zeros(0)
ydbw = np.zeros(0)

t = np.zeros(0)
tdbw = np.zeros(0)

xt = np.zeros(0)
yt = np.zeros(0)
xo = np.zeros(0)
yo = np.zeros(0)

yyre = np.zeros(0)
yxre = np.zeros(0)

yytp = np.zeros(0)
yxtp = np.zeros(0)

yttc = np.zeros(0)
ydtc = np.zeros(0)


# set plots
(p011,) = ax01.plot(t, yttc, "c-", label="TTC")
(p012,) = ax012.plot(t, ydtc, "-", label="DTC")

(p021,) = ax02.plot(t, yd, "y-", label="distance")
(p022,) = ax02.plot(t, ysd, "g-", label="safe distance")

(p031,) = ax03.plot(t, yr, "b-", label="reference speed")
(p032,) = ax03.plot(t, ys, "r-", label="actual speed")

(p041,) = ax04.plot(tdbw, ydbw, "m-.", label="dbw command")
(p042,) = ax04.plot(t, ystate, "k.-", label="state")

(p051,) = ax05.plot(xt, yt, "gs", label="Tram")
(p052,) = ax05.plot(xo, yo, "b^", label="Obstacle")

(p053,) = ax05.plot(yxre, yyre, "g-", label="RE")
(p054,) = ax05.plot(yxtp, yytp, "b.", label="TP")


# set legends
ax01.legend([p011, p012], [p011.get_label(), p012.get_label()])
ax02.legend([p021, p022], [p021.get_label(), p022.get_label()])
ax03.legend([p031, p032, p041], [p031.get_label(), p032.get_label(), p041.get_label()])

# Data Update
xmin = 0
xmax = 10.0
x = 0

plt.show()
