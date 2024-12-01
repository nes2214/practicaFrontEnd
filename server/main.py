import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import time

app = FastAPI()


@app.get("/api/time")
def get_current_time():
    return {"time": time.time()}


if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
