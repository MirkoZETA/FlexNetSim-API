# FlexNetSim Backend API
# A Flask API for running FlexNetSim network simulations

from flask import Flask, request, jsonify
import subprocess
import os
import logging

# --- Flask Application Setup --- 
app = Flask(__name__)
#CORS(app, resources={r"/run_simulation": {"origins": 'http://localhost:5000'}}) # Enable for local development

# --- Configuration ---
SIMULATION_EXECUTABLE = "./src/simulation.out"
COMPILE_ERROR = None

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Simulation Compilation ---
def compile_simulation():
  """
  Compiles the C++ simulation executable on startup.
  
  Returns:
      bool: True if compilation succeeds, False otherwise
  """
  global COMPILE_ERROR

  # Clean existing executable
  if os.path.exists(SIMULATION_EXECUTABLE):
    logger.info(f"Removing existing executable: {SIMULATION_EXECUTABLE}")
    os.remove(SIMULATION_EXECUTABLE)

  logger.info("Compiling simulation...")

  # Verify source file exists
  if not os.path.exists("./src/main.cpp"):
    COMPILE_ERROR = {
      "error": "main.cpp not found", 
      "details": "Ensure main.cpp is in the correct directory."
    }
    logger.error(f"Compilation failed: {COMPILE_ERROR['error']} - {COMPILE_ERROR['details']}")
    return False
    
  # Run compilation with optimization
  compile_result = subprocess.run(
    ["g++", "-O3", "-o", SIMULATION_EXECUTABLE, "./src/main.cpp"], 
    capture_output=True, 
    text=True
  )

  # Handle compilation result
  if compile_result.returncode != 0:
    COMPILE_ERROR = {"error": "Compilation failed", "details": compile_result.stderr}
    logger.error(f"Compilation failed: {COMPILE_ERROR['error']} - {COMPILE_ERROR['details']}")
    return False
  
  COMPILE_ERROR = None
  logger.info("Simulation compiled successfully")
  return True

# --- API Endpoints ---
@app.route("/run_simulation", methods=["POST"])
def run_simulation():
  """
  Executes a network simulation with the provided parameters.
  
  Accepts a JSON request with simulation parameters and runs the C++ executable
  with those parameters. Returns the simulation results.
  
  Returns:
      JSON response: Simulation output or error details
  """
 
  # Check if compilation failed during startup
  if COMPILE_ERROR:
    return jsonify(COMPILE_ERROR), 500

  # Verify executable exists
  if not os.path.exists(SIMULATION_EXECUTABLE):
    return jsonify({"error": "Simulation executable not found. Contact administrator."}), 500

  try:
    # Parse request data
    data = request.get_json()

    # Extract parameters with default values
    algorithm = data.get("algorithm", "FirstFit")
    networkType = data.get("networkType", 1)
    goalConnections = data.get("goalConnections", 100000)
    confidence = data.get("confidence", 0.05)
    lambdaParam = data.get("lambdaParam", 1)
    mu = data.get("mu", 10)
    network = data.get("network", "NSFNet")
    bitrate = data.get("bitrate", "fixed-rate")
    K = data.get("K", 3)

    # Build command for simulation process
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

    # Execute simulation
    process = subprocess.Popen(
      command, 
      stdout=subprocess.PIPE, 
      stderr=subprocess.PIPE, 
      text=True
    )
    output, error = process.communicate()

    # Handle execution result
    if process.returncode != 0:
      logger.error(f"Simulation execution failed. Return code: {process.returncode}, Details: {error.strip()}")
      return jsonify({
        "error": "Simulation execution failed", 
        "details": error.strip()
      }), 500

    # Return successful result
    return jsonify({
      "output": output.strip(), 
      "error": error.strip()
    }), 200

  except Exception as e:
    # Handle unexpected errors
    logger.exception("Unexpected error during simulation:")
    return jsonify({
      "error": "An unexpected error occurred", 
      "details": str(e)
    }), 500

@app.route("/help", methods=["GET"])
def simulation_help():
  """
  Provides API documentation in plain text format.
  
  Returns information about available endpoints, parameters,
  and example usage for the FlexNetSim API.
  
  Returns:
      Plain text response: API documentation
  """
  
  help_message = """\
FlexNetSim API Documentation

ENDPOINT: /run_simulation
METHOD: POST
DESCRIPTION: Runs an optical network simulation with the provided parameters

PARAMETERS (all optional with defaults):
  - algorithm: Routing and spectrum assignment algorithm
      Values: "FirstFit", "ExactFit"
      Default: "FirstFit"
  
  - networkType: Type of optical network
      Values: 1 (EON - Elastic Optical Network)
      Default: 1
  
  - goalConnections: Number of connection requests to simulate
      Default: 100000
      Constraints: Must be > 0
  
  - confidence: Statistical confidence level
      Default: 0.05
      Constraints: Must be > 0
  
  - lambdaParam: Connection arrival rate
      Default: 1.0
      Constraints: Must be > 0
  
  - mu: Connection service rate
      Default: 10.0
      Constraints: Must be > 0
  
  - network: Network topology
      Values: "NSFNet", "Cost239", "EuroCore", "GermanNet", "UKNet"
      Default: "NSFNet"
  
  - bitrate: Bitrate allocation type
      Values: "fixed-rate", "flex-rate"
      Default: "fixed-rate"
  
  - K: Number of paths to consider
      Default: 3
      Constraints: Must be > 0

EXAMPLE REQUEST:
  curl -X POST -H "Content-Type: application/json" \\
  -d '{
    "algorithm": "FirstFit",
    "networkType": 1,
    "goalConnections": 1000000,
    "confidence": 0.05,
    "lambdaParam": 120,
    "mu": 1,
    "network": "NSFNet",
    "bitrate": "fixed-rate"
  }' \\
  https://fns-api-cloud-run-787143541358.us-central1.run.app/run_simulation

RESPONSES:
  Success (200 OK):
    {
      "output": "simulation results...",
      "error": ""
    }

  Error (400/500):
    {
      "error": "Error message",
      "details": "Detailed error information"
    }
  """

  return app.response_class(
    response=help_message, 
    status=200, 
    mimetype="text/plain"
  )

# --- Application Initialization ---
with app.app_context():
  # Compile the simulation on startup
  compile_success = compile_simulation()

# --- Main Entry Point ---
if not compile_success:
  logger.error("Application startup failed: Compilation error. Check logs for details.")
else:
  logger.info("Starting FlexNetSim API server...")
  app.run(host="0.0.0.0")
