FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS base

WORKDIR /app

COPY pyproject.toml uv.lock ./

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_CACHE=1

RUN uv sync --frozen --no-dev

COPY src /app/src


FROM python:3.12.8-slim AS final

WORKDIR /app

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ARG VERSION=0.1.0
ENV APP_VERSION=${VERSION}

COPY --from=base /app /app

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]