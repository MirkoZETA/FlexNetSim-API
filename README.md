# Flask Simulation Backend API

This is a Flask-based backend API that runs C++ library Flex Net Sim.

## Prerequisites

*   Python 3.9 or higher
*   g++ (GNU C++ Compiler)
*   Docker (for containerization)
*   Google Cloud SDK (for deployment to GKE)
*   A Google Cloud Project with Google Kubernetes Engine (GKE) and Google Container Registry (GCR) enabled.

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

4.  **Compile the C++ simulation (this happens automatically on startup):**
    When you run the Flask backend for the first time, it will compile `main.cpp` to `simulation.out`.

5.  **Run the Flask backend:**
    ```bash
    python backend.py
    ```
    The backend will be accessible at `http://127.0.0.1:5000`.

6.  **Send simulation requests using `curl` or a frontend application:**
    Example `curl` request:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"algorithm": "FirstFit", "networkType": 1, "bitrate": "bitrate"}' [http://127.0.0.1:5000/run_simulation](http://127.0.0.1:5000/run_simulation)
    ```

## Dockerization

To build the Docker image:

```bash
docker build -t mi-backend-simulacion .