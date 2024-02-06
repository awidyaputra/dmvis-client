from dmvis import *
import matplotlib
import matplotlib.animation as animation
from matplotlib import pyplot as plt


tram_state: TramState = TramState(current_command=PowerLevel.N, x=0, y=0, v=0, t=0)
tram_state_transition: TramStateTransition = TramStateTransition(
    fsm_state=FSMState.ACC,
    safe_emergency_distance=15,
    lead_distance=1000,
    ttc=1000,
    dtc=1000,
    speed=1000,
)
hlc_state: HLCState = HLCState(
    speed_setpoint=0,
    list_rail_horizon=[],
    list_detected_object=[],
    list_trajectory_prediction=[],
    list_detected_obstacle=[],
    list_detected_railway_obstacle=[],
)
dmplot_state = DMPlot(
    tram_state=tram_state,
    tram_state_transition=tram_state_transition,
    hlc_state=hlc_state,
)


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

global ystate

global yd
global ysd

global yr
global ys
global ydbw

global t
global x

global yxre
global yyre

global yxtp
global yytp

global xt
global yt

global xo
global yo

global start
global yttc
global ydtc

global tdbw

ystate = [0.0]
yd = [0.0]
ysd = [0.0]
yr = [0.0]
ys = [0.0]
ydbw = [0.0]
t = [0.0]
yttc = [0.0]
ydtc = [0.0]

xt = [0.0]
yt = [0.0]
yo = [0.0]
xo = [0.0]
yxre = [0.0]
yyre = [0.0]
yxtp = [0.0]
yytp = [0.0]
xmin = 0
xmax = 10.0
x = 0.0


(p011,) = ax01.plot(t, yttc, "c-", label="TTC")
(p012,) = ax012.plot(t, ydtc, "-", label="DTC")
(p021,) = ax02.plot(t, yd, "y-", label="distance")
(p022,) = ax02.plot(t, ysd, "g-", label="safe distance")
(p031,) = ax03.plot(t, yr, "b-", label="reference speed")
(p032,) = ax03.plot(t, ys, "r-", label="actual speed")
(p041,) = ax04.plot(t, ydbw, "m-.", label="dbw command")
(p042,) = ax04.plot(t, ystate, "k.-", label="state")
(p051,) = ax05.plot(xt, yt, "gs", label="Tram")
(p052,) = ax05.plot(xo, yo, "b^", label="Obstacle")
(p053,) = ax05.plot(yxre, yyre, "g-", label="RE")
(p054,) = ax05.plot(yxtp, yytp, "b.", label="TP")

ax01.legend([p011, p012], [p011.get_label(), p012.get_label()])
ax02.legend([p021, p022], [p021.get_label(), p022.get_label()])
ax03.legend(
    [p031, p032, p041],
    [p031.get_label(), p032.get_label(), p041.get_label()],
)


def mpl_func_animation_cb(frame):
    r = requests.get("http://localhost:8000/dmvis_data")

    j = r.json()

    dmplot_state = DMPlot.model_validate(j)

    xt = [0.0]
    yt = [0.0]
    yo = [0.0]
    xo = [0.0]
    yxre = [0.0]
    yyre = [0.0]
    yxtp = [0.0]
    yytp = [0.0]

    ystate.append(dmplot_state.tram_state_transition.fsm_state)
    yd.append(dmplot_state.tram_state_transition.lead_distance)
    ysd.append(dmplot_state.tram_state_transition.safe_emergency_distance)
    yr.append(dmplot_state.hlc_state.speed_setpoint)
    ys.append(dmplot_state.tram_state.v)
    yttc.append(dmplot_state.tram_state_transition.ttc)
    ydtc.append(dmplot_state.tram_state_transition.dtc)
    yt.append(dmplot_state.tram_state.x)
    xt.append(dmplot_state.tram_state.y)
    ydbw.append(dmplot_state.tram_state.current_command)

    x = dmplot_state.tram_state.t
    t.append(x)

    yo = [o.y for o in dmplot_state.hlc_state.list_detected_object]
    xo = [o.x for o in dmplot_state.hlc_state.list_detected_object]
    yyre = [o.y for o in dmplot_state.hlc_state.list_rail_horizon]
    yxre = [o.x for o in dmplot_state.hlc_state.list_rail_horizon]
    yytp = [o.y for o in dmplot_state.hlc_state.list_trajectory_prediction]
    yxtp = [o.x for o in dmplot_state.hlc_state.list_trajectory_prediction]

    p011.set_data(t, yttc)
    p011.set_data(t, ydtc)
    p021.set_data(t, yd)
    p022.set_data(t, ysd)
    p031.set_data(t, yr)
    p032.set_data(t, ys)
    p041.set_data(t, ydbw)
    p042.set_data(t, ystate)
    p051.set_data(yt, xt)
    p052.set_data(yo, xo)
    p053.set_data(yyre, yxre)
    p054.set_data(yytp, yxtp)

    if x >= xmax - 1.00:
        p011.axes.set_xlim(x - xmax + 1.0, x + 1.0)
        p021.axes.set_xlim(x - xmax + 1.0, x + 1.0)
        p032.axes.set_xlim(x - xmax + 1.0, x + 1.0)
        p041.axes.set_xlim(x - xmax + 1.0, x + 1.0)

    return (
        p011,
        p012,
        p021,
        p022,
        p031,
        p032,
        p041,
        p051,
        p052,
        p053,
        p054,
    )


simulation = animation.FuncAnimation(
    plt.gcf(), mpl_func_animation_cb, blit=False, interval=20, repeat=False
)

plt.show()
