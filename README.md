# Flex Net Sim Backend API

This is a Flask-based backend API that runs the FlexNetSim C++ library. It is an unofficial API that powers the backend for the web app deployed at [www.in-progress.com](www.in-progress.com).

## Prerequisites

*   Python 3.9 or higher
*   g++ (GNU C++ Compiler)
*   Docker (for containerization)
*   Google Cloud SDK (for deployment to GKE) -> In progress.
*   A Google Cloud Project with Google Kubernetes Engine (GKE) and Google Container Registry (GCR) enabled -> In progress.

## Getting Started (Local Development)

1.  **Clone the repository:**
    ```bash
    git clone [repository-url]
    cd flask-simulation-backend
    ```

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    .venv\Scripts\activate  # On Windows
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask backend:**
    ```bash
    flask --app backend run
    ```
    The backend will be accessible at `http://127.0.0.1:5000`.

5.  **Send simulation requests using `curl` or a frontend application:**
    Example `curl` request with minimal parameters (defaults applied):
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"algorithm": "FirstFit", "networkType": 1, "bitrate": "bitrate"}' [http://127.0.0.1:5000/run_simulation](http://127.0.0.1:5000/run_simulation)
    ```

    Example `curl` request with all parameters specified
    ```bash
    curl -X POST -H "Content-Type: application/json" \
     -d '{
          "algorithm": "FirstFit",
          "networkType": 1, -> (Only EONs available for the moment)
          "goal_connections": 10000000,
          "confidence": 0.05,
          "lambda": 120,
          "mu": 1,
          "network": "NSFNet",
          "bitrate": "bitrate" -> (filename in the ./bitrates folder)
         }' \
     http://127.0.0.1:5000/run_simulation
    ```

## Dockerization

To build the Docker image:

```bash
docker build -t fns-api .
```
To run:
```bash
docker run -p 8080:8080 fns-api
```
To stop:
```bash
docker stop fns-api
```