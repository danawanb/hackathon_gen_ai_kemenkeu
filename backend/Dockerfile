FROM python:3.10 AS builder
RUN apt-get update && \
    apt-get install -y libpq-dev gcc

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install poetry
RUN pip install "psycopg[binary,pool]"
RUN pip install psycopg2
RUN pip install psycopg2-binary
RUN poetry config virtualenvs.in-project true
COPY pyproject.toml poetry.lock ./
RUN poetry install

FROM python:3.10-slim
WORKDIR /app

RUN apt-get update && \
    apt-get install -y libpq-dev gcc

COPY --from=builder /app/.venv .venv/
COPY .. .

EXPOSE 8000

CMD ["/app/.venv/bin/fastapi", "run"]
