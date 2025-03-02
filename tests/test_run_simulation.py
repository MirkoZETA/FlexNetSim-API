# Tests for run_simulation endpoint

from flask_testing import TestCase
from backend import app
import json
import os

class TestRunSimulationEndpoint(TestCase):
  """Tests for simulation endpoint"""

  def create_app(self):
    app.config['TESTING'] = True
    return app

  def test_run_simulation_success(self):
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
    response = self.client.post('/run_simulation',
                                data=json.dumps(simulation_input),
                                content_type='application/json')
    self.assert200(response)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "success")
    self.assertIn("data", response_json)


  def test_run_simulation_executable_not_found(self):
    os.rename("./src/simulation.out", "./src/simulation.out.temp_error")
    response = self.client.post('/run_simulation',
                                data=json.dumps({}),
                                content_type='application/json')
    self.assert_status(response, 500)
    os.rename("./src/simulation.out.temp_error", "./src/simulation.out")
    
  def test_run_simulation_execution_failure(self):
    # Create a temporary, invalid executable that will fail
    with open("./src/simulation.out.temp", "w") as f:
      f.write("#!/bin/bash\necho 'Test error message' >&2\nexit 1")
    os.chmod("./src/simulation.out.temp", 0o755)
    
    # Backup the real executable and replace it with our failing one
    if os.path.exists("./src/simulation.out"):
      os.rename("./src/simulation.out", "./src/simulation.out.backup")
    os.rename("./src/simulation.out.temp", "./src/simulation.out")
    
    # Run the test
    response = self.client.post('/run_simulation',
                               data=json.dumps({"goalConnections": 10}),
                               content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Simulation execution failed")
    self.assertIn("Test error message", response_json.get("error"))
    
    # Restore the real executable
    os.remove("./src/simulation.out")
    if os.path.exists("./src/simulation.out.backup"):
      os.rename("./src/simulation.out.backup", "./src/simulation.out")

  def test_invalid_labmda_param(self):
    simulation_input = { "lambdaParam": 0 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("lambdaParam must be greater than 0", response_json.get("error"))

  def test_invalid_mu_param(self):
    simulation_input = { "mu": 0 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("mu must be greater than 0", response_json.get("error"))

  def test_invalid_goal_connections(self):
    simulation_input = { "goalConnections": 0 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("goalConnections must be greater than 0", response_json.get("error"))

    simulation_input = { "goalConnections": 10000001 }
    response = self.client.post('/run_simulation',
                                    data=json.dumps(simulation_input),
                                    content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("goalConnections must be less than 10,000,000", response_json.get("error"))

  def test_invalid_network_type(self):
    simulation_input = { "networkType": 99 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("only networkType 1 is supported", response_json.get("error"))

  def test_invalid_confidence_param(self):
    simulation_input = { "confidence": 1.1 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("confidence must be between 0 and 1", response_json.get("error"))

    simulation_input = { "confidence": -0.1 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("confidence must be between 0 and 1", response_json.get("error"))

  def test_invalid_algorithm_param(self):
    simulation_input = { "algorithm": "InvalidAlgorithm" }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("algorithm must be FirstFit or ExactFit", response_json.get("error"))

  def test_invalid_K_param(self):
    simulation_input = { "K": 0 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("Min K is 1", response_json.get("error"))

    simulation_input = { "K": 100 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("Max K is 6", response_json.get("error"))

  def test_invalid_network_name(self):
    simulation_input = { "network": "TestNetwork" }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("network must be one of", response_json.get("error"))

  def test_invalid_bitrate_param(self):
    simulation_input = { "bitrate": "TestBitRate" }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("bitrate must be one of", response_json.get("error"))

  def test_networks(self):
    for network in ["Cost239", "EuroCore", "GermanNet", "NSFNet", "UKNet"]:
      simulation_input = { "network": network,
                            "goalConnections": 1 }
      response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
      self.assert200(response)
      response_json = json.loads(response.data.decode('utf-8'))
      self.assertEqual(response_json.get("status"), "success")
      self.assertIn("data", response_json)

  def test_bitrates(self):
    for bitrate in ["fixed-rate", "flex-rate"]:
      simulation_input = { "bitrate": bitrate,
                            "goalConnections": 1 }
      response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
      self.assert200(response)
      response_json = json.loads(response.data.decode('utf-8'))
      self.assertEqual(response_json.get("status"), "success")
      self.assertIn("data", response_json)

  def test_malformed_json_triggers_exception(self):
    response = self.client.post('/run_simulation', data="{invalid_json", content_type="application/json")
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode("utf-8"))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "An unexpected error occurred")
