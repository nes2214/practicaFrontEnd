import os
import time

import asyncpg
import uvicorn

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from db import lifespan
import env

from pydantic import BaseModel
from typing import List

app = FastAPI(lifespan=lifespan)

# CORS només per desenvolupament amb React/Vite
origins = [
    "http://localhost:3000",  # React/Vite
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servei web de prova.
@app.get("/api/time")
def get_current_time():
    return {"time": time.time()}

def get_postgres(request: Request) -> asyncpg.Pool:
    return request.app.state.pool

@app.get("/api/health/db")
async def get_health_db():
    async with app.state.pool.acquire() as conn:
        value = await conn.fetchval("SELECT 1")
    return {
        "database": "ok",
        "value": value
    }

class DoctorOut(BaseModel):
    username: str
    name: str

@app.get("/api/doctors", response_model=List[DoctorOut])
async def get_doctors():
    query = "SELECT username, name FROM doctors"
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch(query)
    return [
        {"username": r["username"], "name": r["name"]}
        for r in rows
    ]

# Aquesta linia em dona problemes.
# app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host=env.settings.uvicorn_host, port=env.settings.uvicorn_port,
                reload=env.settings.uvicorn_reload)
