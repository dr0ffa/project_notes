FROM python:3.13-slim

ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

CMD cd app && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000