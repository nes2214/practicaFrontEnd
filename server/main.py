import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import time

app = FastAPI()


@app.get("/api/time")
def get_current_time():
    return {"time": time.time()}


if os.path.exists("../static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)

