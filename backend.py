# backend.py (Flask API)
from flask import Flask, request, jsonify
import subprocess
import os
import logging # Import the logging module
from flask_cors import CORS # Import Flask-CORS (if you use it)

# --- Flask Setup --- 
app = Flask(__name__)
CORS(app, resources={r"/run_simulation": {"origins": 'http://localhost:5000'}}) # <-- UNCOMMENT and SET ORIGIN

# --- Setup and Compilation ---
SIMULATION_EXECUTABLE = "./src/simulation.out"
COMPILE_ERROR = None # Global variable to store compilation errors

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,  # Set the minimum level to INFO (or DEBUG for more verbosity)
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Get a logger instance for this module

# --- Compilation ---
def compile_simulation():
    """Compiles the simulation at startup. Logs compilation details."""
    global COMPILE_ERROR

    # If file exists, delete it.
    if os.path.exists(SIMULATION_EXECUTABLE):
        logger.info(f"{SIMULATION_EXECUTABLE} already exists, deleting.") # Use logger.info instead of print
        os.remove(SIMULATION_EXECUTABLE)

    logger.info("Compiling simulation...") # Use logger.info
    compile_result = subprocess.run(["g++", "-O3", "-o", SIMULATION_EXECUTABLE, "./src/main.cpp"], capture_output=True, text=True)
    if compile_result.returncode != 0:
        COMPILE_ERROR = {"error": "Compilation failed", "details": compile_result.stderr}
        logger.error(f"Compilation failed: {COMPILE_ERROR['error']} - Details: {COMPILE_ERROR['details']}") # Use logger.error for errors
        return False
    logger.info("Simulation compiled successfully.") # Use logger.info
    return True

# --- Run Simulation Endpoint ---
@app.route("/run_simulation", methods=["POST"])
@app.route("/run_simulation", methods=["POST"])
def run_simulation():
    """Runs the simulation with parameters provided in the request."""
    global COMPILE_ERROR
    if COMPILE_ERROR:
        return jsonify(COMPILE_ERROR), 500 # Return compilation error if it exists from startup

    if not os.path.exists(SIMULATION_EXECUTABLE): # Double check if executable exists
        return jsonify({"error": "Simulation executable not found. Contact developer."}), 400

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON parameters in request body."}), 400

        # Parameters, use default values if not provided
        algorithm = data.get("algorithm", "FirstFit")
        networkType = data.get("networkType", 1)
        goal_connections = data.get("goal_connections", 100000)
        confidence = data.get("confidence", 0.05)
        lambda_param = data.get("lambda", 1)
        mu = data.get("mu", 10)
        network = data.get("network", "NSFNet")
        bitrate = data.get("bitrate", "fixed-rate")
        K = data.get("K", 3)

        # Construct command for subprocess
        command = [
            f"./{SIMULATION_EXECUTABLE}",
            str(algorithm),
            str(networkType),
            str(goal_connections),
            str(confidence),
            str(lambda_param),
            str(mu),
            str(network),
            str(bitrate),
            str(K)
        ]
        logger.debug(f"Running simulation with command: {' '.join(command)}") # Debug log for command

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()

        if process.returncode != 0:
            logger.error(f"Simulation execution failed. Return code: {process.returncode}, Details: {error.strip()}") # Error log for simulation failure
            return jsonify({"error": "Simulation execution failed", "details": error.strip()}), 500

        # Return output in a structured JSON format
        return jsonify({"output": output.strip(), "error": error.strip()}), 200

    except Exception as e:
        logger.exception("Unexpected error during run_simulation:")
        return jsonify({"error": "An unexpected error occurred. Contact developer.", "details": str(e)}), 500

@app.route("/help", methods=["GET"])
def simulation_help():
    """Returns information about the /run_simulation endpoint, including request structure and parameter details."""
    schema = {
        "endpoint": "/run_simulation",
        "method": "POST",
        "request_body_format": "application/json",
        "description": "Runs a network simulation with provided parameters.",
        "request_parameters": [
            {
                "name": "algorithm",
                "type": "string",
                "description": "Routing and spectrum assignment algorithm to use.",
                "allowed_values": ["FirstFit", "ExactFit"],
                "default": "FirstFit",
                "required": False
            },
            {
                "name": "networkType",
                "type": "integer",
                "description": "Type of optical network.",
                "allowed_values": [1],
                "value_meanings": {"1": "EON (Elastic Optical Network)"},
                "note": "Only EON (networkType: 1) is currently available in this playground. SDM (2) and BDM (3) are not yet implemented.",
                "default": 1,
                "required": False
            },
            {
                "name": "goal_connections",
                "type": "integer",
                "description": "Target number of connection requests for the simulation.",
                "constraints": "Must be an integer greater than 0.",
                "default": 100000,
                "required": False
            },
            {
                "name": "confidence",
                "type": "number (float)",
                "description": "Confidence level for the simulation results.",
                "constraints": "Must be a number greater than 0.",
                "default": 0.05,
                "required": False
            },
            {
                "name": "lambda_param",
                "type": "number (float)",
                "description": "Arrival rate (lambda) of connection requests.",
                "constraints": "Must be a number greater than 0.",
                "default": 1.0,
                "required": False
            },
            {
                "name": "mu",
                "type": "number (float)",
                "description": "Service rate (mu) of connection requests.",
                "constraints": "Must be a number greater than 0.",
                "default": 10.0,
                "required": False
            },
            {
                "name": "network",
                "type": "string",
                "description": "Network topology to simulate.",
                "allowed_values": ["NSFNet", "Cost239", "EuroCore", "GermanNet", "UKNet"],
                "default": "NSFNet",
                "required": False
            },
            {
                "name": "bitrate",
                "type": "string",
                "description": "Type of bitrate allocation.",
                "allowed_values": ["fixed-rate", "flex-rate"],
                "default": "fixed-rate",
                "required": False
            },
             {
                "name": "K",
                "type": "integer",
                "description": "Number of paths to considers.",
                "default": 3,
                "required": False
            },
        ],
        "response_body_format": "application/json",
        "response_structure": {
            "output": "string",
            "error": "string (empty if no error)"
        },
        "example_request": {
            "algorithm": "FirstFit",
            "networkType": 1,
            "goal_connections": 10000,
            "confidence": 0.05,
            "lambda_param": 120,
            "mu": 1,
            "network": "NSFNet",
            "bitrate": "flex-rate",
            "K": 3
        },
        "example_response_success": {
            "output": "Simulation output will be a string containing simulation results.",
            "error": ""
        },
        "example_response_error": {
            "error": "Simulation execution failed",
            "details": "Detailed error message from the simulation or backend."
        }
    }
    return jsonify(schema), 200

# --- Run Setup on Application Start ---
with app.app_context(): # Context needed to call route function outside request
    compile_success = compile_simulation() # Call compile directly at startup

if __name__ == "__main__":
    if not compile_success:
        print("Application start aborted due to compilation error. Please check /setup endpoint.")
    else:
        print("Starting Flask application...")
        app.run(debug=True, host="0.0.0.0") # Enable debug for development