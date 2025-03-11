# Tests for run_simulation endpoint

from flask_testing import TestCase
from backend import app
from utils.config import valid_networks, valid_bitrates
import json

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
    
    # Assert response is successful
    self.assert200(response)
    response_json = json.loads(response.data.decode('utf-8'))
    # Assert response contains success status and data
    self.assertEqual(response_json.get("status"), "success")
    self.assertIn("data", response_json)

  def test_networks(self):
    for network in valid_networks:
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
    for bitrate in valid_bitrates:
      simulation_input = { "bitrate": bitrate,
                            "goalConnections": 1 }
      response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
      self.assert200(response)
      response_json = json.loads(response.data.decode('utf-8'))
      self.assertEqual(response_json.get("status"), "success")
      self.assertIn("data", response_json)

  def test_malformed_json(self):
    response = self.client.post('/run_simulation', data="{invalid_json", content_type="application/json")
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode("utf-8"))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "An unexpected error occurred")

  def test_invalid_parameters(self):
    simulation_input = { "lambdaParam": 0 }
    response = self.client.post('/run_simulation',
                                  data=json.dumps(simulation_input),
                                  content_type='application/json')
    self.assert_status(response, 400)
    response_json = json.loads(response.data.decode('utf-8'))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "Invalid parameters")
    self.assertIn("lambdaParam must be greater than 0", response_json.get("error"))