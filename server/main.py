"""
main.py
-------
Entry point for the Clinic Manager FastAPI application.

This module initializes the FastAPI app, connects the database lifespan context,
and includes the clinic-related API routes. It also provides a way to run
the app locally using uvicorn.
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import db
from pydantic import BaseModel
from typing import List

from api import clinic_router

# Create FastAPI app instance
app = FastAPI(
    lifespan=db.lifespan,   # Async context manager for database connection pool
    title="Clinic Manager"
)

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

# Include all routes from the clinic API router
app.include_router(clinic_router, tags=["Clinic"])

if __name__ == "__main__":
    # Run the application locally with auto-reload enabled
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)