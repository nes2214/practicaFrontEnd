FROM denoland/deno AS client

WORKDIR /app
COPY . ./
RUN deno install
RUN deno install --allow-scripts=npm:@swc/core

# https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile

FROM python:3.13-alpine AS server
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY .python-version pyproject.toml uv.lock ./
COPY server ./
RUN uv sync --compile-bytecode --no-dev
#RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR


FROM python:3.13-alpine AS runtime

WORKDIR /app
COPY --from=server app/.venv/lib /usr/local/lib
#COPY --from=client /app/static  /app/static
# TODO ignore __pycache__
COPY server ./

ENV UVICORN_HOST=0.0.0.0 UVICORN_PORT=80 UVICORN_RELOAD=False
CMD ["python", "main.py"]


