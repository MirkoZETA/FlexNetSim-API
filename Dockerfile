FROM python:3.12-slim-bookworm
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends build-essential # Update OS packages and keep build-essential

COPY backend.py ./
COPY src ./src
COPY networks ./networks
COPY bitrates ./bitrates

# CMD ["g++ -O3 -o simulation.out ./src/main.cpp"]  # Commented out as per original Dockerfile

CMD ["gunicorn", "backend:app", "--bind", "0.0.0.0:8080", "--workers", "3"]