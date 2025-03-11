# Tests for run_simulation_stream endpoint

from flask_testing import TestCase
from backend import app
from utils.config import valid_networks, valid_bitrates
import json

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
    
    # Assert response is successful
    self.assert200(response)
    # Assert response is a server-sent event stream
    self.assertEqual(response.mimetype, "text/event-stream")
    # Assert Cache-Control header prevents caching
    self.assertEqual(response.headers.get("Cache-Control"), "no-cache")
    # Assert Connection header is 'keep-alive' for persistent connection
    self.assertEqual(response.headers.get("Connection"), "keep-alive")
    
  def test_stream_networks(self):
    for network in valid_networks:
      simulation_input = { "network": network,
                            "goalConnections": 1 }
      response = self.client.post('/run_simulation_stream',
                                data=json.dumps(simulation_input),
                                content_type='application/json')
      self.assert200(response)

      # Consume the response stream
      for line in response.response:
        pass

      
  def test_stream_bitrates(self):
    for bitrate in valid_bitrates:
      simulation_input = { "bitrate": bitrate,
                            "goalConnections": 1 }
      response = self.client.post('/run_simulation_stream',
                                data=json.dumps(simulation_input),
                                content_type='application/json')
      self.assert200(response)

      # Consume the response stream
      for line in response.response:
          pass

  def test_stream_malformed_json(self):
    response = self.client.post('/run_simulation_stream', data="{invalid_json", content_type="application/json")
    self.assert_status(response, 500)
    response_json = json.loads(response.data.decode("utf-8"))
    self.assertEqual(response_json.get("status"), "error")
    self.assertEqual(response_json.get("message"), "An unexpected error occurred")
    
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