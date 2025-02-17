FROM python:3.9-slim-buster
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends build-essential


COPY backend.py ./
COPY src ./src
COPY networks ./networks
COPY bitrates ./bitrates


# RUN g++ -O3 -o simulation.out ./src/main.cpp

# - 'backend:app' especifica el módulo 'backend.py' y la instancia de Flask 'app'.
# - '--bind 0.0.0.0:8080' hace que Gunicorn escuche en todas las interfaces (0.0.0.0) en el puerto 8080 dentro del contenedor.
# - '--workers 3' configura Gunicorn para usar 3 procesos de trabajo para manejar las peticiones.
CMD ["gunicorn", "backend:app", "--bind", "0.0.0.0:8080", "--workers", "3"]