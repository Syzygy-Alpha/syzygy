FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

RUN useradd --create-home --shell /usr/sbin/nologin syzygy
USER syzygy

EXPOSE 8000

CMD ["uvicorn", "syzygy_foundation.main:app", "--host", "0.0.0.0", "--port", "8000"]

