import time
from fastapi import FastAPI

app = FastAPI()

@app.get("/time")
def get_current_time():
    return {"time": time.time()}