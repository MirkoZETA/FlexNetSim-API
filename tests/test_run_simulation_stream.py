# Tests for run_simulation_stream endpoint

from flask_testing import TestCase
from backend import app
import json
import os

class TestRunSimulationStreamEndpoint(TestCase):
  """Tests for streaming simulation endpoint"""

  def create_app(self):
    app.config['TESTING'] = True
    return app

  def test_run_simulation_stream_success(self):
    simulation_input = {
      "algorithm": "FirstFit",
      "networkType": 1,
      "goalConnections": 10,
      "confidence": 0.05,
      "lambdaParam": 1,
      "mu": 10,
      "network": "NSFNet",
      "bitrate": "fixed-rate",
      "K": 3
    }
    response = self.client.post('/run_simulation_stream',
                              data=json.dumps(simulation_input),
                              content_type='application/json')
    self.assert200(response)
    self.assertEqual(response.mimetype, "text/event-stream")
    self.assertEqual(response.headers.get("Cache-Control"), "no-cache")
    self.assertEqual(response.headers.get("Connection"), "keep-alive")
    
  def test_stream_malformed_json(self):
    response = self.client.post('/run_simulation_stream', data="{invalid_json", content_type="application/json")
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode("utf-8"))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "An unexpected error occurred")
    
  def test_stream_executable_not_found(self):
    os.rename("./src/simulation.out", "./src/simulation.out.temp_error")
    response = self.client.post('/run_simulation_stream',
                                data=json.dumps({}),
                                content_type='application/json')
    self.assert_status(response, 500)
    os.rename("./src/simulation.out.temp_error", "./src/simulation.out")
    
  def test_stream_execution_failure(self):
    # Create a temporary, invalid executable that will fail
    with open("./src/simulation.out.temp", "w") as f:
      f.write("#!/bin/bash\necho 'Line 1'\necho 'Line 2'\necho 'Error line' >&2\nexit 1")
    os.chmod("./src/simulation.out.temp", 0o755)
    
    # Backup the real executable and replace it with our failing one
    if os.path.exists("./src/simulation.out"):
      os.rename("./src/simulation.out", "./src/simulation.out.backup")
    os.rename("./src/simulation.out.temp", "./src/simulation.out")
    
    # Run the test - we can't easily check the stream content here
    # but we can at least ensure it returns the correct response type
    response = self.client.post('/run_simulation_stream',
                               data=json.dumps({"goalConnections": 10}),
                               content_type='application/json')
    self.assert200(response)
    self.assertEqual(response.mimetype, "text/event-stream")
    
    # Check for the correct data in the response
    # The stream will contain all the events in this case
    response_data = response.data.decode('utf-8')
    self.assertIn("event: start", response_data)
    self.assertIn("event: data", response_data)
    self.assertIn("Line 1", response_data)
    self.assertIn("Line 2", response_data)
    self.assertIn("event: error", response_data)
    self.assertIn("Error line", response_data)
    self.assertIn("event: end", response_data)
    
    # Restore the real executable
    os.remove("./src/simulation.out")
    if os.path.exists("./src/simulation.out.backup"):
      os.rename("./src/simulation.out.backup", "./src/simulation.out")
    
  def test_stream_invalid_parameters(self):
    # Test with invalid lambda parameter
    simulation_input = { "lambdaParam": 0 }
    response = self.client.post('/run_simulation_stream',
                               data=json.dumps(simulation_input),
                               content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("lambdaParam must be greater than 0", response_json.get("error"))