from utils.config import *
import subprocess
import os
from flask import jsonify

def compile_simulation(debug=False):
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

  # Verify source file exists
  if not os.path.exists("./src/main.cpp"):
    COMPILE_ERROR = {
      "error": "main.cpp not found", 
      "details": "Ensure main.cpp is in the correct directory."
    }
    logger.error(f"Compilation failed: {COMPILE_ERROR['error']} - {COMPILE_ERROR['details']}")
    return False
    
  # Run compilation with optimization
  logger.info("Compiling simulation...")
  compile_result = subprocess.run(
    ["g++", "-O3", "-o", SIMULATION_EXECUTABLE, "./src/main.cpp"], 
    capture_output=True, 
    text=True
  )
  if compile_result.returncode != 0:
    COMPILE_ERROR = {
      "error": "Compilation failed",
      "details": compile_result.stderr
    }
    logger.error(f"Compilation failed: {COMPILE_ERROR['error']} - {COMPILE_ERROR['details']}")
    return False
  
  if debug: COMPILE_ERROR = None
  logger.info("Simulation compiled successfully")
  return True

def validate_simulation_prerequisites():
  """
  Validates compilation status and executable existence.
  
  Returns:
      tuple: (is_valid, response) where is_valid is a boolean and 
             response is an optional error response
  """
  # Check if compilation failed during startup
  if COMPILE_ERROR:
    return False, (jsonify({
      "status": "error",
      "message": COMPILE_ERROR["error"],
      "error": COMPILE_ERROR["details"]
    }), 500)

  # Verify executable exists
  if not os.path.exists(SIMULATION_EXECUTABLE):
    return False, (jsonify({
      "status": "error",
      "message": "Simulation executable not found",
      "error": "Contact administrator for assistance"
    }), 500)
    
  return True, None

def parse_simulation_parameters(data):
  """
  Parses and validates simulation parameters from request data.
  
  Args:
      data (dict): Request JSON data
      
  Returns:
      tuple: Either (True, parameters) if valid, or (False, error_response) if invalid
  """
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
  
  # Validate networkType
  if networkType != 1:
    return False, (jsonify({
      "status": "error",
      "message": "Invalid parameters",
      "error": "At the moment only networkType 1 is supported"
    }), 400)
  
  # Validate goalConnections
  if goalConnections > 10000000:
    return False, (jsonify({
      "status": "error",
      "message": "Invalid parameters",
      "error": "goalConnections must be less than 10,000,000"
    }), 400)
  elif goalConnections < 1:
    return False, (jsonify({
      "status": "error",
      "message": "Invalid parameters",
      "error": "goalConnections must be greater than 0"
    }), 400)
  
  # Validate K
  if K > 6:
    return False, (jsonify({
      "status": "error",
      "message": "Invalid parameters",
      "error": "Max K is 6"
    }), 400)
  elif K < 1:
    return False, (jsonify({
      "status": "error",
      "message": "Invalid parameters",
      "error": "Min K is 1"
    }), 400)
  
  # Validate confidence
  if confidence >= 1 or confidence <= 0:
    return False, (jsonify({
      "status": "error",
      "message": "Invalid parameters",
      "error": "confidence must be between 0 and 1"
    }), 400)
  
  # Validate lambda
  if lambdaParam <= 0:
    return False, (jsonify({
      "status": "error",
      "message": "Invalid parameters",
      "error": "lambdaParam must be greater than 0"
    }), 400)
  
  # Validate mu
  if mu <= 0:
    return False, (jsonify({
      "status": "error", 
      "message": "Invalid parameters",
      "error": "mu must be greater than 0"
    }), 400)
  
  # Validate algorithm
  if algorithm not in ["FirstFit", "BestFit"]:
    return False, (jsonify({
      "status": "error",
      "message": "Invalid parameters",
      "error": "algorithm must be FirstFit or BestFit"
    }), 400)
  
  # Validate network
  if network not in valid_networks:
    return False, (jsonify({
      "status": "error",
      "message": "Invalid parameters",
      "error": f"network must be one of: {', '.join(valid_networks)}"
    }), 400)
  
  # Validate bitrate
  if bitrate not in valid_bitrates:
    return False, (jsonify({
      "status": "error",
      "message": "Invalid parameters",
      "error": f"bitrate must be one of: {', '.join(valid_bitrates)}"
    }), 400)
  
  # All parameters are valid, return the parameter tuple
  return True, (algorithm, networkType, goalConnections, confidence, 
          lambdaParam, mu, network, bitrate, K)

def build_simulation_command(params):
  """
  Builds command for simulation process.
  
  Args:
      params (tuple): Simulation parameters
      
  Returns:
      list: Command list for subprocess
  """
  algorithm, networkType, goalConnections, confidence, lambdaParam, mu, network, bitrate, K = params
  
  return [
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