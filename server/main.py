import os
import time

import asyncpg
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import env

app = FastAPI()


def get_postgres(request: Request) -> asyncpg.Pool:
    return request.app.state.pool


@app.get("/api/time")
def get_current_time():
    return {"time": time.time()}


app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host=env.settings.uvicorn_host, port=env.settings.uvicorn_port,
                reload=env.settings.uvicorn_reload)
