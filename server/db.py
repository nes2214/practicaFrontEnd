import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import asyncpg
from fastapi import FastAPI

import env

DATABASE_URL = f"postgres://{env.settings.database_user}:{env.settings.database_password}@{env.settings.database_host}/clinic"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # app.state is where the connection pool is created, which can be accessed later inside views.
    # This is only run once during app startup.
    app.state.pool = asyncpg.create_pool(
        dsn=DATABASE_URL,
        min_size=1,
        max_size=10,
    )
    try:
        await init_db(app.state.pool)
        # This is where the app runs all the URL route functions.
        yield
    finally:
        # This is run once when the app is shut down.
        try:
            await app.state.pool.close()
        except Exception as e:
            logging.error(f"Error closing database connection pool: {e}")
            raise


doctors_table = '''
    create table if not exists doctors (
        user text primary key,
        name text not null
    ); 
'''


async def init_db(pool: asyncpg.Pool) -> None:
    try:
        async with pool.acquire() as conn:
            await conn.execute(doctors_table)
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise
