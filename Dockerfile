FROM python:3.12-slim

WORKDIR /app

# Zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod
COPY . .

# Zmienne środowiskowe
ENV ANTHROPIC_API_KEY=""
ENV TZ="Europe/Warsaw"

# Uruchom scheduler
CMD ["python", "scheduler.py"]
