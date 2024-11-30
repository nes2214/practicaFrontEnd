import time
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/", StaticFiles(directory="dist"), name="static")

@app.get("/api/time")
def get_current_time():
    return {"time": time.time()}
