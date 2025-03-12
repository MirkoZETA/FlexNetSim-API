# Tests for utils/helpers.py

import pytest
import os
from flask_testing import TestCase
from backend import app
from utils.helpers import *
from tests.test_utils import temporarily_rename_file

class TestHelpers(TestCase):
    """Tests for utils functions"""

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_compile_simulation(self):
        # Test compilation failure
        with temporarily_rename_file("./src/main.cpp", "./src/main.cpp.temp"):
            self.assertFalse(compile_simulation(debug=True))

        # Test compilation success
        self.assertTrue(compile_simulation(debug=True))

    def test_validate_simulation_prerequisites(self):
        # Test when executable is not found
        with temporarily_rename_file("./src/simulation.out", "./src/simulation.out.temp_error"):
            is_valid, response = validate_simulation_prerequisites()
            self.assertFalse(is_valid)
            self.assertEqual(response[1], 500)

        # Test when executable is found
        self.assertTrue(compile_simulation(debug=True))
        is_valid, response = validate_simulation_prerequisites()
        self.assertTrue(is_valid)

    def test_invalid_lambda_param(self):
        # Test lambda = 0
        is_valid, response = parse_simulation_parameters({"lambdaParam": 0})
        self._assert_invalid_param(is_valid, response, "lambdaParam must be greater than 0")
        
        # Test lambda as string
        is_valid, response = parse_simulation_parameters({"lambdaParam": "string"})
        self._assert_invalid_param(is_valid, response, "lambdaParam must be a number")

    def test_invalid_mu_param(self):
        # Test mu = 0
        is_valid, response = parse_simulation_parameters({"mu": 0})
        self._assert_invalid_param(is_valid, response, "mu must be greater than 0")
        
        # Test mu as string
        is_valid, response = parse_simulation_parameters({"mu": "string"})
        self._assert_invalid_param(is_valid, response, "mu must be a number")

    def test_invalid_goal_connections(self):
        # Test goalConnections = 0
        is_valid, response = parse_simulation_parameters({"goalConnections": 0})
        self._assert_invalid_param(is_valid, response, "goalConnections must be greater than 0")
        
        # Test goalConnections too high
        is_valid, response = parse_simulation_parameters({"goalConnections": 10000001})
        self._assert_invalid_param(is_valid, response, "goalConnections must be less than 10,000,000")
        
        # Test goalConnections as string
        is_valid, response = parse_simulation_parameters({"goalConnections": "string"})
        self._assert_invalid_param(is_valid, response, "goalConnections must be an integer")

    def test_invalid_network_type(self):
        # Test unsupported network type
        is_valid, response = parse_simulation_parameters({"networkType": 99})
        self._assert_invalid_param(is_valid, response, "At the moment only networkType 1 is supported")
        
        # Test network type as string
        is_valid, response = parse_simulation_parameters({"networkType": "string"})
        self._assert_invalid_param(is_valid, response, "networkType must be an integer")

    def test_invalid_confidence(self):
        # Test confidence too high
        is_valid, response = parse_simulation_parameters({"confidence": 1.1})
        self._assert_invalid_param(is_valid, response, "confidence must be between 0 and 1")
        
        # Test confidence too low
        is_valid, response = parse_simulation_parameters({"confidence": -0.1})
        self._assert_invalid_param(is_valid, response, "confidence must be between 0 and 1")
        
        # Test confidence as string
        is_valid, response = parse_simulation_parameters({"confidence": "string"})
        self._assert_invalid_param(is_valid, response, "confidence must be a number")

    def test_invalid_algorithm(self):
        # Test invalid algorithm name
        is_valid, response = parse_simulation_parameters({"algorithm": "InvalidAlgorithm"})
        self._assert_invalid_param(is_valid, response, "algorithm must be FirstFit or BestFit")
        
        # Test algorithm as number
        is_valid, response = parse_simulation_parameters({"algorithm": 123})
        self._assert_invalid_param(is_valid, response, "algorithm must be a string")

    def test_invalid_k(self):
        # Test K too small
        is_valid, response = parse_simulation_parameters({"K": 0})
        self._assert_invalid_param(is_valid, response, "Min K is 1")
        
        # Test K too large
        is_valid, response = parse_simulation_parameters({"K": 100})
        self._assert_invalid_param(is_valid, response, "Max K is 6")
        
        # Test K as string
        is_valid, response = parse_simulation_parameters({"K": "string"})
        self._assert_invalid_param(is_valid, response, "K must be an integer")

    def test_invalid_network(self):
        # Test invalid network name
        is_valid, response = parse_simulation_parameters({"network": "TestNetwork"})
        self._assert_invalid_param(is_valid, response, "network must be one of")
        
        # Test network as number
        is_valid, response = parse_simulation_parameters({"network": 123})
        self._assert_invalid_param(is_valid, response, "network must be a string")

    def test_invalid_bitrate(self):
        # Test invalid bitrate name
        is_valid, response = parse_simulation_parameters({"bitrate": "TestBitRate"})
        self._assert_invalid_param(is_valid, response, "bitrate must be one of")
        
        # Test bitrate as number
        is_valid, response = parse_simulation_parameters({"bitrate": 123})
        self._assert_invalid_param(is_valid, response, "bitrate must be a string")

    def _assert_invalid_param(self, is_valid, response, expected_error):
        """Helper method to validate common assertions for invalid parameters"""
        self.assertFalse(is_valid)
        response_json = response[0].json
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid parameters")
        self.assertIn(expected_error, response_json["error"])

    def test_parse_simulation_parameters_valid(self):
        data = {
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
        is_valid, params = parse_simulation_parameters(data)
        self.assertTrue(is_valid)
        self.assertEqual(params, ("FirstFit", 1, 10, 0.05, 1, 10, "NSFNet", "fixed-rate", 3))

    def test_build_simulation_command(self):
        params = ("FirstFit", 1, 10, 0.05, 1, 10, "NSFNet", "fixed-rate", 3)
        command = build_simulation_command(params)
        expected_command = [
            f"./{SIMULATION_EXECUTABLE}",
            "FirstFit",
            "1",
            "10",
            "0.05",
            "1",
            "10",
            "NSFNet",
            "fixed-rate",
            "3"
        ]
        self.assertEqual(command, expected_command)
