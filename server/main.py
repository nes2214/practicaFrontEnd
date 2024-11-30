import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/api/time")
def get_current_time():
    return {"time": time.time()}


app.mount("/", StaticFiles(directory="static", html= True), name="static")

