FROM python:3.11-slim

WORKDIR /app

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python3", "Services_Market.py"]
