from typing import List
from enum import IntEnum
from pydantic import BaseModel

import matplotlib
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import matplotlib.animation as animation
from io import BytesIO
import base64

import requests


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
    y: float
    v: float
    d: float


class HLCState(BaseModel):
    speed_setpoint: float

    list_rail_horizon: List[Position]
    list_detected_object: List[Position]
    list_trajectory_prediction: List[Position]
    list_detected_obstacle: List[ObstacleState]
    list_detected_railway_obstacle: List[ObstacleState]


class DMPlot(BaseModel):
    tram_state: TramState
    tram_state_transition: TramStateTransition
    hlc_state: HLCState


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

        self.ystate = [0.0]
        self.yd = [0.0]
        self.ysd = [0.0]
        self.yr = [0.0]
        self.ys = [0.0]
        self.ydbw = [0.0]
        self.t = [0.0]
        self.yttc = [0.0]
        self.ydtc = [0.0]

        self.xt = [0.0]
        self.yt = [0.0]
        self.yo = [0.0]
        self.xo = [0.0]
        self.yxre = [0.0]
        self.yyre = [0.0]
        self.yxtp = [0.0]
        self.yytp = [0.0]
        self.xmin = 0
        self.xmax = 10.0
        self.x = 0.0

        (self.p011,) = self.ax01.plot(self.t, self.yttc, "c-", label="TTC")
        (self.p012,) = self.ax012.plot(self.t, self.ydtc, "-", label="DTC")
        (self.p021,) = self.ax02.plot(self.t, self.yd, "y-", label="distance")
        (self.p022,) = self.ax02.plot(self.t, self.ysd, "g-", label="safe distance")
        (self.p031,) = self.ax03.plot(self.t, self.yr, "b-", label="reference speed")
        (self.p032,) = self.ax03.plot(self.t, self.ys, "r-", label="actual speed")
        (self.p041,) = self.ax04.plot(self.t, self.ydbw, "m-.", label="dbw command")
        (self.p042,) = self.ax04.plot(self.t, self.ystate, "k.-", label="state")
        (self.p051,) = self.ax05.plot(self.xt, self.yt, "gs", label="Tram")
        (self.p052,) = self.ax05.plot(self.xo, self.yo, "b^", label="Obstacle")
        (self.p053,) = self.ax05.plot(self.yxre, self.yyre, "g-", label="RE")
        (self.p054,) = self.ax05.plot(self.yxtp, self.yytp, "b.", label="TP")

        self.ax01.legend(
            [self.p011, self.p012], [self.p011.get_label(), self.p012.get_label()]
        )
        self.ax02.legend(
            [self.p021, self.p022], [self.p021.get_label(), self.p022.get_label()]
        )
        self.ax03.legend(
            [self.p031, self.p032, self.p041],
            [self.p031.get_label(), self.p032.get_label(), self.p041.get_label()],
        )

    def draw_b64(self):
        self.xt = [0.0]
        self.yt = [0.0]
        self.yo = [0.0]
        self.xo = [0.0]
        self.yxre = [0.0]
        self.yyre = [0.0]
        self.yxtp = [0.0]
        self.yytp = [0.0]

        self.ystate.append(self.dmplot_state.tram_state_transition.fsm_state)
        self.yd.append(self.dmplot_state.tram_state_transition.lead_distance)
        self.ysd.append(self.dmplot_state.tram_state_transition.safe_emergency_distance)
        self.yr.append(self.dmplot_state.hlc_state.speed_setpoint)
        self.ys.append(self.dmplot_state.tram_state.v)
        self.yttc.append(self.dmplot_state.tram_state_transition.ttc)
        self.ydtc.append(self.dmplot_state.tram_state_transition.dtc)
        self.yt.append(self.dmplot_state.tram_state.x)
        self.xt.append(self.dmplot_state.tram_state.y)
        self.ydbw.append(self.dmplot_state.tram_state.current_command)

        self.x = self.dmplot_state.tram_state.t
        self.t.append(self.x)

        self.yo = [o.y for o in self.dmplot_state.hlc_state.list_detected_object]
        self.xo = [o.x for o in self.dmplot_state.hlc_state.list_detected_object]
        self.yyre = [o.y for o in self.dmplot_state.hlc_state.list_rail_horizon]
        self.yxre = [o.x for o in self.dmplot_state.hlc_state.list_rail_horizon]
        self.yytp = [
            o.y for o in self.dmplot_state.hlc_state.list_trajectory_prediction
        ]
        self.yxtp = [
            o.x for o in self.dmplot_state.hlc_state.list_trajectory_prediction
        ]

        self.p011.set_data(self.t, self.yttc)
        self.p011.set_data(self.t, self.ydtc)
        self.p021.set_data(self.t, self.yd)
        self.p022.set_data(self.t, self.ysd)
        self.p031.set_data(self.t, self.yr)
        self.p032.set_data(self.t, self.ys)
        self.p041.set_data(self.t, self.ydbw)
        self.p042.set_data(self.t, self.ystate)
        self.p051.set_data(self.yt, self.xt)
        self.p052.set_data(self.yo, self.xo)
        self.p053.set_data(self.yyre, self.yxre)
        self.p054.set_data(self.yytp, self.yxtp)

        if self.x >= self.xmax - 1.00:
            self.p011.axes.set_xlim(self.x - self.xmax + 1.0, self.x + 1.0)
            self.p021.axes.set_xlim(self.x - self.xmax + 1.0, self.x + 1.0)
            self.p032.axes.set_xlim(self.x - self.xmax + 1.0, self.x + 1.0)
            self.p041.axes.set_xlim(self.x - self.xmax + 1.0, self.x + 1.0)

        buf = BytesIO()
        self.fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")

        return data

    def update_dmplot_state(self, curr: DMPlot):
        self.dmplot_state = curr

    def get_dmplot_state(self):
        r = requests.get("http://localhost:8000/dmvis_data")

        j = r.json()

        self.update_dmplot_state(j)

    def mpl_func_animation_cb(self, frame):
        self.get_dmplot_state()

        self.xt = [0.0]
        self.yt = [0.0]
        self.yo = [0.0]
        self.xo = [0.0]
        self.yxre = [0.0]
        self.yyre = [0.0]
        self.yxtp = [0.0]
        self.yytp = [0.0]

        self.ystate.append(self.dmplot_state.tram_state_transition.fsm_state)
        self.yd.append(self.dmplot_state.tram_state_transition.lead_distance)
        self.ysd.append(self.dmplot_state.tram_state_transition.safe_emergency_distance)
        self.yr.append(self.dmplot_state.hlc_state.speed_setpoint)
        self.ys.append(self.dmplot_state.tram_state.v)
        self.yttc.append(self.dmplot_state.tram_state_transition.ttc)
        self.ydtc.append(self.dmplot_state.tram_state_transition.dtc)
        self.yt.append(self.dmplot_state.tram_state.x)
        self.xt.append(self.dmplot_state.tram_state.y)
        self.ydbw.append(self.dmplot_state.tram_state.current_command)

        self.x = self.dmplot_state.tram_state.t
        self.t.append(self.x)

        self.yo = [o.y for o in self.dmplot_state.hlc_state.list_detected_object]
        self.xo = [o.x for o in self.dmplot_state.hlc_state.list_detected_object]
        self.yyre = [o.y for o in self.dmplot_state.hlc_state.list_rail_horizon]
        self.yxre = [o.x for o in self.dmplot_state.hlc_state.list_rail_horizon]
        self.yytp = [
            o.y for o in self.dmplot_state.hlc_state.list_trajectory_prediction
        ]
        self.yxtp = [
            o.x for o in self.dmplot_state.hlc_state.list_trajectory_prediction
        ]

        self.p011.set_data(self.t, self.yttc)
        self.p011.set_data(self.t, self.ydtc)
        self.p021.set_data(self.t, self.yd)
        self.p022.set_data(self.t, self.ysd)
        self.p031.set_data(self.t, self.yr)
        self.p032.set_data(self.t, self.ys)
        self.p041.set_data(self.t, self.ydbw)
        self.p042.set_data(self.t, self.ystate)
        self.p051.set_data(self.yt, self.xt)
        self.p052.set_data(self.yo, self.xo)
        self.p053.set_data(self.yyre, self.yxre)
        self.p054.set_data(self.yytp, self.yxtp)

        if self.x >= self.xmax - 1.00:
            self.p011.axes.set_xlim(self.x - self.xmax + 1.0, self.x + 1.0)
            self.p021.axes.set_xlim(self.x - self.xmax + 1.0, self.x + 1.0)
            self.p032.axes.set_xlim(self.x - self.xmax + 1.0, self.x + 1.0)
            self.p041.axes.set_xlim(self.x - self.xmax + 1.0, self.x + 1.0)

        return (
            self.p011,
            self.p012,
            self.p021,
            self.p022,
            self.p031,
            self.p032,
            self.p041,
            self.p051,
            self.p052,
            self.p053,
            self.p054,
        )

    def show(self):
        self.simulation = animation.FuncAnimation(
            self.fig, self.mpl_func_animation_cb, blit=False, interval=20, repeat=False
        )
        plt.show()
