FROM oven/bun:1 AS client
WORKDIR /app
COPY . ./
RUN  bun run build

FROM python:3.12-alpine AS server

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

COPY server ./

CMD ["poetry", "run", "python", "main.py"]

FROM python:3.12-alpine AS runtime

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=server ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=client /app/static  /app/static

COPY server  /app

CMD [".venv/bin/fastapi", "run", "main.py", "--port", "80"]
