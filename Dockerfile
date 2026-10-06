FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=10000

CMD ["sh", "-c", "uvicorn api_server:app --host 0.0.0.0 --port ${PORT:-10000}"]
