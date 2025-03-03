# Flex Net Sim Backend API
# A Flask API for running Flex Net Sim network simulations

from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
from utils.helpers import *

# --- Flask Application Setup --- 
app = Flask(__name__)

# Enable CORS only for /run_simulation_stream
CORS(app, resources={r"/run_simulation_stream": {"origins": "*"}})

@app.route("/run_simulation", methods=["POST"])
def run_simulation():
  """
  Executes a network simulation with the provided parameters.
  
  Accepts a JSON request with simulation parameters and runs the C++ executable
  with those parameters. Returns the simulation results.
  
  Returns:
      JSON response: Simulation data or error details
  """
  # Validate prerequisites
  is_valid, error_response = validate_simulation_prerequisites()
  if not is_valid:
    return error_response
    
  try:
    data = request.get_json()
    
    # Parse and validate parameters
    is_valid, result = parse_simulation_parameters(data)
    if not is_valid:
      return result
    
    # Build and execute command
    command = build_simulation_command(result)
    logger.debug(f"Running simulation with command: {' '.join(command)}")

    # Execute simulation
    process = subprocess.Popen(
      command, 
      stdout=subprocess.PIPE, 
      stderr=subprocess.PIPE, 
      text=True
    )
    stdout, stderr = process.communicate()

    # Handle execution result
    if process.returncode != 0:
      logger.error(f"Simulation execution failed. Return code: {process.returncode}, Error: {stderr.strip()}")
      return jsonify({
        "status": "error",
        "message": "Simulation execution failed", 
        "error": stderr.strip()
      }), 500

    # Return successful result
    return jsonify({
      "status": "success",
      "data": stdout.strip()
    }), 200

  except Exception as e:
    # Handle unexpected errors
    logger.exception("Unexpected error during simulation:")
    return jsonify({
      "status": "error",
      "message": "An unexpected error occurred", 
      "error": str(e)
    }), 500

@app.route("/run_simulation_stream", methods=["POST"])
def run_simulation_stream():
  """
  Executes a network simulation with the provided parameters and streams the output.
  
  Accepts a JSON request with simulation parameters and runs the C++ executable
  with those parameters. Returns a streaming response with simulation results
  as they become available.
  
  Returns:
      Streaming response: Line-by-line simulation data
  """
  # Validate prerequisites
  is_valid, error_response = validate_simulation_prerequisites()
  if not is_valid:
    return error_response
    
  try:
    data = request.get_json()
    
    # Parse and validate parameters
    is_valid, result = parse_simulation_parameters(data)
    if not is_valid:
      return result
    
    # Build command
    command = build_simulation_command(result)
    logger.debug(f"Running streaming simulation with command: {' '.join(command)}")

    # Create streaming function
    def generate():
      # Send initial event
      yield f"event: start\ndata: {{\n  \"status\": \"started\",\n  \"message\": \"Simulation started\"\n}}\n\n"
      
      # Execute simulation with streaming output
      process = subprocess.Popen(
        command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True,
        bufsize=1  # Line buffered
      )
      
      # Stream stdout
      for line in iter(process.stdout.readline, ""):
        if line:
          yield f"event: data\ndata: {{\n  \"status\": \"running\",\n  \"data\": \"{line.strip()}\"\n}}\n\n"
          
      # Check for errors at the end
      process.stdout.close()
      return_code = process.wait()
      
      if return_code != 0:
        error = process.stderr.read()
        yield f"event: error\ndata: {{\n  \"status\": \"error\",\n  \"message\": \"Simulation execution failed\",\n  \"error\": \"{error.strip()}\"\n}}\n\n"
        logger.error(f"Streaming simulation failed. Return code: {return_code}, Error: {error.strip()}")

      # Close the stream resources
      process.stderr.close()
      
      # Send completion event
      yield f"event: end\ndata: {{\n  \"status\": \"completed\",\n  \"message\": \"Simulation completed\"\n}}\n\n"
    
    return Response(
      stream_with_context(generate()),
      mimetype="text/event-stream",
      headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive"
      }
    )

  except Exception as e:
    # Handle unexpected errors
    logger.exception("Unexpected error during streaming simulation:")
    return jsonify({
      "status": "error",
      "message": "An unexpected error occurred", 
      "error": str(e)
    }), 500

@app.route("/help", methods=["GET"])
def simulation_help():
  """
  Provides API documentation in plain text format.
  
  Returns information about available endpoints, parameters,
  and example usage for the Flex Net Sim API.
  
  Returns:
      Plain text response: API documentation
  """
  
  help_message = """\
  Flex Net Sim API Documentation

  ENDPOINTS:
    - /run_simulation (POST): Returns complete simulation results
    - /run_simulation_stream (POST): Streams results in real-time using Server-Sent Events

  COMMON PARAMETERS (JSON body, all optional):
    algorithm: "FirstFit" or "ExactFit" (default: "FirstFit")
    networkType: 1 for EON (default: 1)
    goalConnections: 1-10000000 (default: 100000)
    confidence: 0-1 (default: 0.05)
    lambdaParam: > 0 (default: 1.0)
    mu: > 0 (default: 10.0)
    network: "NSFNet", "Cost239", "EuroCore", "GermanNet", "UKNet" (default: "NSFNet")
    bitrate: "fixed-rate" or "flex-rate" (default: "fixed-rate")
    K: 1-6 (default: 3)

  EXAMPLE - STANDARD REQUEST:
    curl -X POST -H "Content-Type: application/json" \\
    -d '{"algorithm": "FirstFit", "goalConnections": 1000000, "lambdaParam": 120, "mu": 1}' \\
    https://fns-api-cloud-run-787143541358.us-central1.run.app/run_simulation

  EXAMPLE - STREAMING REQUEST:
    curl -X POST -H "Content-Type: application/json" \\
    -d '{"algorithm": "FirstFit", "goalConnections": 1000000, "lambdaParam": 120, "mu": 1}' \\
    https://fns-api-cloud-run-787143541358.us-central1.run.app/run_simulation_stream

  RESPONSES:
    Standard (/run_simulation):
      Success (200): {"status": "success", "data": "simulation results..."}
      Invalid Parameters (400): {"status": "error", "message": "Invalid parameters", "error": "Details"}
      Error (500): {"status": "error", "message": "Error message", "error": "Details"}

    Streaming (/run_simulation_stream):
      Success (200): Server-Sent Events (text/event-stream)
        event: start
        data: {"status": "started", "message": "Simulation started"}

        event: data
        data: {"status": "running", "data": "Line of output"}

        event: end
        data: {"status": "completed", "message": "Simulation completed"}
      
      Invalid Parameters (400): {"status": "error", "message": "Invalid parameters", "error": "Details"}
      Error (500): {"status": "error", "message": "Error message", "error": "Details"}
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
if __name__ == "__main__":  
  if not compile_success:
    logger.error("Application startup failed: Compilation error. Check logs for details.")
  else:
    logger.info("Starting Flex Net Sim API server...")
    app.run(host="0.0.0.0")
