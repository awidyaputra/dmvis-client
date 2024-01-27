import pathlib
from typing import Annotated

from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from matplotlib.figure import Figure
from io import BytesIO
import base64


app = FastAPI()

BASE_DIR = pathlib.Path(__file__).parent
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


class Contact(BaseModel):
    first_name: str
    last_name: str
    email: str


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


@app.get("/dmvis", response_class=HTMLResponse)
async def get_dmvis(request: Request):
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    context = {
        "request": request,
        "data": data,
    }

    return templates.TemplateResponse("fragments/plot1.html", context)


@app.post("/dmvis")
async def update_dmvis(p):
    print(p)
    # print(p.tram_state.x)
    # print(p.tram_state.y)
    # print(p.tram_state.v)
    # print(p.tram_state.t)
