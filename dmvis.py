from typing import List
from enum import IntEnum
from pydantic import BaseModel


class PowerLevel(IntEnum):
    B5 = -5
    B4 = -4
    B3 = -3
    B2 = -2
    B1 = -1
    N = 0
    P1 = 1
    P2 = 2
    P3 = 3
    P4 = 4
    P5 = 5
    P6 = 6
    P7 = 7


class TramState(BaseModel):
    current_command: PowerLevel

    x: float
    y: float
    v: float
    t: float


class FSMState(IntEnum):
    ACC = 0
    CA = 1
    EBS = 2


class TramStateTransition(BaseModel):
    fsm_state: FSMState

    safe_emergency_distance: float
    lead_distance: float
    ttc: float
    dtc: float
    speed: float


class Position(BaseModel):
    x: float
    y: float


class ObstacleState(BaseModel):
    id: int
    x: float
    v: float
    d: float


class HLCState(BaseModel):
    speed_setpoint: float

    list_rail_horizon: List[Position]
    list_detected_object: List[Position]
    list_trajectory_prediction: List[Position]
    list_detected_obstacle: List[ObstacleState]
    list_detected_railway_obstacle: List[Position]


class DMPlot(BaseModel):
    tram_state: TramState
    tram_state_transition: TramStateTransition
    hlc_state: HLCState


import matplotlib
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from io import BytesIO
import base64


class DMVisualisation:
    def __init__(
        self,
        tram_state: TramState = TramState(
            current_command=PowerLevel.N, x=0, y=0, v=0, t=0
        ),
        tram_state_transition: TramStateTransition = TramStateTransition(
            fsm_state=FSMState.ACC,
            safe_emergency_distance=15,
            lead_distance=1000,
            ttc=1000,
            dtc=1000,
            speed=1000,
        ),
        hlc_state: HLCState = HLCState(
            speed_setpoint=0,
            list_rail_horizon=[],
            list_detected_object=[],
            list_trajectory_prediction=[],
            list_detected_obstacle=[],
            list_detected_railway_obstacle=[],
        ),
    ):
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

        self.dmplot_state = DMPlot(
            tram_state=tram_state,
            tram_state_transition=tram_state_transition,
            hlc_state=hlc_state,
        )

        self.t = [self.dmplot_state.tram_state.t]
        self.yttc = [self.dmplot_state.tram_state_transition.ttc]
        self.ydtc = [self.dmplot_state.tram_state_transition.dtc]

        self.xt = [self.dmplot_state.tram_state.x]
        self.yt = [self.dmplot_state.tram_state.y]

        (self.p011,) = self.ax01.plot(self.t, self.yttc, "c-", label="TTC")
        (self.p012,) = self.ax012.plot(self.t, self.ydtc, "-", label="DTC")
        (self.p051,) = self.ax05.plot(self.xt, self.yt, "gs", label="Tram")

    def draw_b64(self):
        self.t.append(self.dmplot_state.tram_state.t)
        self.yttc.append(self.dmplot_state.tram_state_transition.ttc)
        self.ydtc.append(self.dmplot_state.tram_state_transition.dtc)

        self.xt.append(self.dmplot_state.tram_state.x)
        self.yt.append(self.dmplot_state.tram_state.y)

        self.p011.set_data(self.t, self.yttc)
        self.p011.set_data(self.t, self.ydtc)

        self.p051.set_data(self.yt, self.xt)

        buf = BytesIO()
        self.fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")

        return data

    def update_dmplot_state(self, curr: DMPlot):
        self.dmplot_state = curr
