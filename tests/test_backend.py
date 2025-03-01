# Flex Net Sim API Test Suite
# Tests for API endpoints and functionality

from flask_testing import TestCase
from backend import app, compile_simulation
import json
import os

class TestCompilation(TestCase):
  """Tests for simulation compilation"""
  
  def create_app(self):
    app.config['TESTING'] = True
    return app

  def test_compilation_failure(self):
    os.rename("./src/main.cpp", "./src/main.cpp.temp")
    compile_result = compile_simulation()
    os.rename("./src/main.cpp.temp", "./src/main.cpp")
    self.assertFalse(compile_result)

    response = self.client.post('/run_simulation',
                                data=json.dumps({}),
                                content_type='application/json')
    self.assert_status(response, 500)

    os.rename("./src/main.cpp", "./src/main.cpp.temp")
    os.rename("./src/test_main.cpp", "./src/main.cpp")
    compile_result = compile_simulation()
    self.assertFalse(compile_result)

    response = self.client.post('/run_simulation',
                                data=json.dumps({}),
                                content_type='application/json')
    self.assert_status(response, 500)
    os.rename("./src/main.cpp", "./src/test_main.cpp")
    os.rename("./src/main.cpp.temp", "./src/main.cpp")

  def test_compilation_success(self):
    compile_result = compile_simulation()
    self.assertTrue(compile_result)

class TestHelpEndpoint(TestCase):
  """Tests for help endpoint"""
  
  def create_app(self):
    app.config['TESTING'] = True
    return app
  
  def test_help_endpoint_success(self):
    response = self.client.get('/help')
    self.assert200(response)


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
    self.assertEqual(response_json.get("error"), "")


  def test_run_simulation_executable_not_found(self):
    os.rename("./src/simulation.out", "./src/simulation.out.temp_error")
    response = self.client.post('/run_simulation',
                                data=json.dumps({}),
                                content_type='application/json')
    self.assert_status(response, 500)
    os.rename("./src/simulation.out.temp_error", "./src/simulation.out")

  def test_invalid_labmda_param(self):
    simulation_input = { "lambdaParam": 0 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertIn("Simulation execution failed", response_json.get("error"))

  def test_invalid_mu_param(self):
    simulation_input = { "mu": 0 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertIn("Simulation execution failed", response_json.get("error"))

  def test_invalid_goal_connections(self):
    simulation_input = { "goalConnections": 0 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertIn("Simulation execution failed", response_json.get("error"))

    simulation_input = { "goalConnections": 10000001 }
    response = self.client.post('/run_simulation',
                                    data=json.dumps(simulation_input),
                                    content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertIn("Simulation execution failed", response_json.get("error"))

  def test_invalid_network_type(self):
    simulation_input = { "networkType": 99 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertIn("Simulation execution failed", response_json.get("error"))

  def test_invalid_confidence_param(self):
    simulation_input = { "confidence": 1.1 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertIn("Simulation execution failed", response_json.get("error"))

    simulation_input = { "confidence": -0.1 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertIn("Simulation execution failed", response_json.get("error"))

  def test_invalid_algorithm_param(self):
    simulation_input = { "algorithm": "InvalidAlgorithm" }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertIn("Simulation execution failed", response_json.get("error"))

  def test_invalid_K_param(self):
    simulation_input = { "K": 0 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertIn("Simulation execution failed", response_json.get("error"))

    simulation_input = { "K": 100 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertIn("Simulation execution failed", response_json.get("error"))

  def test_invalid_network_name(self):
    simulation_input = { "network": "TestNetwork" }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertIn("Simulation execution failed", response_json.get("error"))

  def test_invalid_bitrate_param(self):
    simulation_input = { "bitrate": "TestBitRate" }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertIn("Simulation execution failed", response_json.get("error"))

  def test_networks(self):
    for network in ["Cost239", "EuroCore", "GermanNet", "NSFNet", "UKNet"]:
      simulation_input = { "network": network,
                            "goalConnections": 1 }
      response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
      self.assert200(response)
      response_json = json.loads(response.data.decode('utf-8'))
      self.assertEqual(response_json.get("error"), "")

  def test_bitrates(self):
    for bitrate in ["fixed-rate", "flex-rate"]:
      simulation_input = { "bitrate": bitrate,
                            "goalConnections": 1 }
      response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
      self.assert200(response)
      response_json = json.loads(response.data.decode('utf-8'))
      self.assertEqual(response_json.get("error"), "")

  def test_malformed_json_triggers_exception(self):
    response = self.client.post('/run_simulation', data="{invalid_json", content_type="application/json")
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode("utf-8"))
    self.assertIn("An unexpected error occurred", response_json.get("error"))
