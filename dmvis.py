from pydantic import BaseModel


class TramState(BaseModel):
    x: float
    y: float
    v: float
    t: float


class DMPlot(BaseModel):
    tram_state: TramState


import matplotlib
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from io import BytesIO
import base64


class DMVisualisation:
    def __init__(self, tram_state: TramState = TramState(x=0, y=0, v=0, t=0)):
        font = {"size": 9}
        matplotlib.rc("font", **font)

        fig = plt.figure(figsize=(18, 8))
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

        self.fig = fig
        self.ax01 = ax01
        self.ax012 = ax012
        self.ax02 = ax02
        self.ax03 = ax03
        self.ax04 = ax04
        self.ax05 = ax05

        self.all_axes = [
            self.ax01,
            self.ax012,
            self.ax02,
            self.ax03,
            self.ax04,
            self.ax05,
        ]

        self.dmplot_state = DMPlot(tram_state=tram_state)

        xt = self.dmplot_state.tram_state.x
        yt = self.dmplot_state.tram_state.y
        (self.p051,) = self.ax05.plot(xt, yt, "gs", label="Tram")

    def draw_b64(self):
        self.p051.set_data(
            self.dmplot_state.tram_state.y, self.dmplot_state.tram_state.x
        )

        buf = BytesIO()
        self.fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")

        return data

    def update_dmplot_state(self, curr: DMPlot):
        self.dmplot_state.tram_state.t += 1
        self.dmplot_state.tram_state.x = curr.tram_state.x
        self.dmplot_state.tram_state.y = curr.tram_state.y
