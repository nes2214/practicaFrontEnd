import time
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/api/time")
def get_current_time():
    return {"time": time.time()}


@app.api_route("/{path_name:path}", methods=["GET"])
async def catch_all(request: Request, path_name: str):
    return {"request_method": request.method, "path_name": path_name}
