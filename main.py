import pathlib
from typing import Annotated, List

from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel, Json

from io import BytesIO
import base64

import time

from dmvis import DMPlot, DMVisualisation, TramState

class CANTramStatus(BaseModel):
    speed: float

class TramCan(BaseModel):
    speed: float = 0.0
    cmd_torque: int = 0 + 15000
    cmd_speed_limit: float = 0.0
    cmd_autonomous_mode: int = 0x00 # 0x00 is off, 0xFA is on


class ProcessingTime(BaseModel):
    duration: int


class MoreDebugInfo:
    def __init__(self):
        self.proctime = ProcessingTime(duration=0)

    def update(self, curr_proc_time: ProcessingTime):
        self.proctime.duration = curr_proc_time.duration


dmvis = DMVisualisation()
mdi = MoreDebugInfo()
tramcan = TramCan()

app = FastAPI()

BASE_DIR = pathlib.Path(__file__).parent
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


class Contact(BaseModel):
    first_name: str
    last_name: str
    email: str


class Stuff(BaseModel):
    xs: List[float]


contact = Contact(first_name="Joe", last_name="Blow", email="joe@blow.com")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    context = {
        "request": request,
    }

    response = templates.TemplateResponse("index.html", context)
    return response


@app.get("/test")
async def server_test():
    return JSONResponse(content={"hello": "world"})


@app.get("/contact/1/edit", response_class=HTMLResponse)
async def get_contact1_edit(request: Request):
    context = {
        "request": request,
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "email": contact.email,
    }

    return templates.TemplateResponse("fragments/b.html", context)


@app.get("/contact/1", response_class=HTMLResponse)
async def get_contact1(request: Request):
    context = {
        "request": request,
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "email": contact.email,
    }

    return templates.TemplateResponse("fragments/a.html", context)


@app.put("/contact/1", response_class=HTMLResponse)
async def put_contact(
    request: Request,
    firstName: Annotated[str, Form()],
    lastName: Annotated[str, Form()],
    email: Annotated[str, Form()],
):
    contact.first_name = firstName
    contact.last_name = lastName
    contact.email = email
    context = {
        "request": request,
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "email": contact.email,
    }
    print(request.form)
    return templates.TemplateResponse("fragments/a.html", context)


@app.get("/dmvisdebug", response_class=HTMLResponse)
async def get_dmvisdebug(request: Request):
    lead_dist = dmvis.dmplot_state.tram_state_transition.lead_distance
    safe_emergency_dist = (
        dmvis.dmplot_state.tram_state_transition.safe_emergency_distance
    )
    rail_obs = dmvis.dmplot_state.hlc_state.list_detected_railway_obstacle
    rail_obs_amount = len(rail_obs)
    detected_obs = dmvis.dmplot_state.hlc_state.list_detected_obstacle
    detected_obs_amount = len(detected_obs)
    tram = dmvis.dmplot_state.tram_state
    fsm_state = dmvis.dmplot_state.tram_state_transition.fsm_state.name
    dtc = dmvis.dmplot_state.tram_state_transition.dtc
    ttc = dmvis.dmplot_state.tram_state_transition.ttc
    speed_setpoint = dmvis.dmplot_state.hlc_state.speed_setpoint

    context = {
        "request": request,
        "lead_dist": lead_dist,
        "safe_emergency_dist": safe_emergency_dist,
        "rail_obs_amount": rail_obs_amount,
        "rail_obs": rail_obs,
        "detected_obs_amount": detected_obs_amount,
        "detected_obs": detected_obs,
        "tram": tram,
        "fsm_state": fsm_state,
        "dtc": dtc,
        "ttc": ttc,
        "speed_setpoint": speed_setpoint,
    }

    return templates.TemplateResponse("fragments/dmvisdebug.html", context)

@app.get("/dmvis_data", status_code=200)
def get_dmvis_data() -> DMPlot:
    return dmvis.dmplot_state


@app.get("/dmvis", response_class=HTMLResponse)
def get_dmvis(request: Request):
    tic = time.perf_counter_ns()
    data = dmvis.draw_b64()
    toc = time.perf_counter_ns()
    print((toc - tic) / 1_000_000)

    context = {
        "request": request,
        "data": data,
    }

    return templates.TemplateResponse("fragments/plot1.html", context)


@app.post("/dmvis", status_code=201)
async def update_dmvis(p: DMPlot):
    # print(p)
    dmvis.update_dmplot_state(p)
    return


@app.get("/dmvisbak", response_class=HTMLResponse)
async def get_dmvisbak(request: Request):
    tic = time.perf_counter_ns()
    ax.clear()
    ax.plot(xs)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    toc = time.perf_counter_ns()
    print((toc - tic) / 1_000_000)

    context = {
        "request": request,
        "data": data,
    }

    return templates.TemplateResponse("fragments/plot1.html", context)


@app.post("/dmvisbak", status_code=201)
async def update_dmvisbak(stuff: Stuff):
    global xs
    xs = stuff.xs

    return


@app.get("/moredebuginfo", status_code=200)
async def get_moredebuginfo(request: Request):
    proctime = mdi.proctime.duration

    context = {
        "request": request,
        "function_duration": proctime,
    }

    return templates.TemplateResponse("fragments/mdi1.html", context)



@app.post("/moredebuginfo", status_code=201)
async def post_moredebuginfo(pt: ProcessingTime):
    mdi.proctime = pt
    return

@app.get("/tram/status/speed", status_code=200)
async def get_can_tram_speed():
    return tramcan.speed

@app.post("/tram/status/speed", status_code=201)
async def post_can_tram_speed(status: CANTramStatus):
    tramcan.speed = status.speed
    print(tramcan.speed)
