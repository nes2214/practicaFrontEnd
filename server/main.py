"""
main.py
-------
Entry point for the Clinic Manager FastAPI application.

This module initializes the FastAPI app, connects the database lifespan context,
and includes the clinic-related API routes. It also provides a way to run
the app locally using uvicorn.
"""

import uvicorn
from fastapi import FastAPI

import db
from api import clinic_router

# Create FastAPI app instance
app = FastAPI(
    lifespan=db.lifespan,   # Async context manager for database connection pool
    title="Clinic Manager"
)

# Include all routes from the clinic API router
app.include_router(clinic_router, tags=["Clinic"])

if __name__ == "__main__":
    # Run the application locally with auto-reload enabled
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)