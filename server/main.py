import time
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/api/time")
def get_current_time():
    return {"time": time.time()}
