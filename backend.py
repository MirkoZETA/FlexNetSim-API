# backend.py (Flask API)
from flask import Flask, request, jsonify
import subprocess
import os
import logging # Import the logging module
import json

# --- Flask Setup --- 
app = Flask(__name__)
#CORS(app, resources={r"/run_simulation": {"origins": 'http://localhost:5000'}}) # <-- UNCOMMENT and SET ORIGIN

# --- Setup and Compilation ---
SIMULATION_EXECUTABLE = "./src/simulation.out"
COMPILE_ERROR = None

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Compilation ---
def compile_simulation():
  """Compiles the simulation at startup. Logs compilation details."""
  global COMPILE_ERROR

  # If file exists, delete it.
  if os.path.exists(SIMULATION_EXECUTABLE):
    logger.info(f"{SIMULATION_EXECUTABLE} already exists, deleting.")
    os.remove(SIMULATION_EXECUTABLE)

  logger.info("Compiling simulation...")
  compile_result = subprocess.run(["g++", "-O3", "-o", SIMULATION_EXECUTABLE, "./src/main.cpp"], capture_output=True, text=True)

  if compile_result.returncode != 0:
    COMPILE_ERROR = {"error": "Compilation failed", "details": compile_result.stderr}
    logger.error(f"Compilation failed: {COMPILE_ERROR['error']} - Details: {COMPILE_ERROR['details']}") # Use logger.error for errors
    return False
  
  logger.info("Simulation compiled successfully.")
  return True

# --- Run Simulation Endpoint ---
@app.route("/run_simulation", methods=["POST"])
def run_simulation():
  """Runs the simulation with parameters provided in the request."""
  global COMPILE_ERROR
  if COMPILE_ERROR:
    return jsonify(COMPILE_ERROR), 500

  if not os.path.exists(SIMULATION_EXECUTABLE):
    return jsonify({"error": "Simulation executable not found. Contact developer."}), 400

  try:
    data = request.get_json()
    # if not data:
    #  return jsonify({"error": "Missing JSON parameters in request body."}), 400

    # Parameters, use default values if not provided
    algorithm = data.get("algorithm", "FirstFit")
    networkType = data.get("networkType", 1)
    goalConnections = data.get("goalConnections", 100000)
    confidence = data.get("confidence", 0.05)
    lambdaParam = data.get("lambdaParam", 1)
    mu = data.get("mu", 10)
    network = data.get("network", "NSFNet")
    bitrate = data.get("bitrate", "fixed-rate")
    K = data.get("K", 3)

    # Construct command for subprocess
    command = [
      f"./{SIMULATION_EXECUTABLE}",
      str(algorithm),
      str(networkType),
      str(goalConnections),
      str(confidence),
      str(lambdaParam),
      str(mu),
      str(network),
      str(bitrate),
      str(K)
    ]
    logger.debug(f"Running simulation with command: {' '.join(command)}")

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, error = process.communicate()

    # Error log for simulation failure
    if process.returncode != 0:
      logger.error(f"Simulation execution failed. Return code: {process.returncode}, Details: {error.strip()}")
      return jsonify({"error": "Simulation execution failed", "details": error.strip()}), 500

    # Return output in a structured JSON format
    return jsonify({"output": output.strip(), "error": error.strip()}), 200

  except Exception as e:
    logger.exception("Unexpected error during run_simulation:")
    return jsonify({"error": "An unexpected error occurred. Contact developer.", "details": str(e)}), 500

@app.route("/help", methods=["GET"])
def simulation_help():
  """Returns human-readable API documentation in plain text format."""
  
  help_message = """\
  API Endpoint: /run_simulation
  Method: POST
  Description: Runs a network simulation with provided parameters.
  
  Request Parameters (all optional, defaults shown):
    - algorithm: string (default: "FirstFit")
    - networkType: integer (default: 1)
    - goalConnections: integer (default: 100000)
    - confidence: float (default: 0.05)
    - lambdaParam: float (default: 1.0)
    - mu: float (default: 10.0)
    - network: string (default: "NSFNet")
    - bitrate: string (default: "fixed-rate")
    - K: integer (default: 3)

  Example Request:
    curl -X POST -H "Content-Type: application/json" \\
    -d '{ "algorithm": "FirstFit",
          "networkType": 1,
          "goalConnections": 1000000,
          "confidence": 0.05,
          "lambdaParam": 120,
          "mu": 1,
          "network": "NSFNet",
          "bitrate": "fixed-rate"
        }' \\
      https://fns-api-cloud-run-787143541358.us-central1.run.app/run_simulation

  Example Response (Success):
    {
      error: "",
      output: ...output from simulation...
    }

  Example Response (Failure):

    {
      error: "Simulation execution failed...",
      details: "Error details..."
    }
  """

  return app.response_class(
    response=help_message, 
    status=200, 
    mimetype="text/plain"
    )

# --- Run Setup on Application Start ---
with app.app_context():
  compile_success = compile_simulation() # Call compile directly at startup

if __name__ == "__main__":
  if not compile_success:
    print("Application start aborted due to compilation error. Contact developers!")
  else:
    print("Starting Flask application...")
    app.run(host="0.0.0.0")