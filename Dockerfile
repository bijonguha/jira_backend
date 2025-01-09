# Stage 1 - Install build dependencies
FROM python:3.10-slim AS builder

WORKDIR /app

RUN python -m venv .venv && .venv/bin/pip install --no-cache-dir -U pip setuptools

COPY requirements.txt .
COPY grollm-0.0.9a2-py3-none-any.whl .

RUN .venv/bin/pip install --no-cache-dir -r requirements.txt
RUN .venv/bin/pip install --no-cache-dir grollm-0.0.9a2-py3-none-any.whl

# Stage 2 - Copy only necessary files to the runner stage
FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /app /app

COPY . /app

ENV PATH="/app/.venv/bin:$PATH"

ENV APP_ENV=PROD 

RUN chmod a+x ./start

CMD ["sh","./start"]