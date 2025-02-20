# tests/test_backend.py
import pytest
from flask_testing import TestCase
from backend import app  # Import your Flask app from backend.py
import json
import os

class TestCompilation(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_compilation_success(self):
        # Accessing any endpoint implies successful app startup, which depends on successful compilation.
        response = self.client.get('/help')
        self.assert200(response)

class TestHelpEndpoint(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_help_endpoint_success(self):
        response = self.client.get('/help')
        self.assert200(response)
        self.assert_content_type(response, "text/plain") # Keep this for now

class TestRunSimulationEndpoint(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_run_simulation_success(self):
        # Basic successful run test - adjust parameters as needed for a quick test
        simulation_input = {
            "algorithm": "FirstFit",
            "networkType": 1,
            "goalConnections": 1000, # Reduced goal connections for faster test
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
        self.assertIn("output", response_json)
        self.assertEqual(response_json.get("error"), "") # Expecting no error

    def test_run_simulation_compilation_error(self):
        # Simulate compilation error by modifying the executable path (or similar)
        original_executable_path = "./src/simulation.out"
        temp_executable_path = "./src/simulation.out.temp_error"
        os.rename(original_executable_path, temp_executable_path) # Rename to break execution

        response = self.client.post('/run_simulation',
                                     data=json.dumps({}), # Empty data should still trigger the error check
                                     content_type='application/json')
        self.assert_status(response, 500) # Use assert_status here
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertIn("Compilation failed", response_json.get("error"))

        os.rename(temp_executable_path, original_executable_path) # Rename back to fix

    def test_run_simulation_executable_not_found(self):
        # Temporarily remove the executable
        original_executable_path = "./src/simulation.out"
        temp_executable_path = "./src/simulation.out.temp_error"

        # Check if executable exists before attempting to rename
        if os.path.exists(original_executable_path): # Add this check
            os.rename(original_executable_path, temp_executable_path) # Rename to break execution
        else:
            print(f"Warning: Executable not found at {original_executable_path}, test may not be valid.") # Warning if not found


        # Recompile to ensure COMPILE_ERROR is None for this specific test case
        from backend import compile_simulation
        compile_simulation() # Recompile so COMPILE_ERROR is cleared if previous test failed

        response = self.client.post('/run_simulation',
                                     data=json.dumps({}),
                                     content_type='application/json')
        self.assert_status(response, 400) # Use assert_status here
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertIn("Simulation executable not found", response_json.get("error"))

        # Rename back only if the original path existed and we renamed it
        if os.path.exists(temp_executable_path): # Check if temp file exists (meaning we renamed)
            os.rename(temp_executable_path, original_executable_path) # Rename back


    class TestRunSimulationExecutionFailure(TestCase): # Group tests for execution failures
        def create_app(self):
            app.config['TESTING'] = True
            return app

        def test_invalid_lambda_param(self):
            simulation_input = { "lambdaParam": 0 } # Invalid lambda
            response = self.client.post('/run_simulation',
                                         data=json.dumps(simulation_input),
                                         content_type='application/json')
            self.assert_status(response, 500) # Use assert_status
            response_json = json.loads(response.data.decode('utf-8'))
            self.assertIn("Simulation execution failed", response_json.get("error"))

        def test_invalid_mu_param(self):
            simulation_input = { "mu": 0 } # Invalid mu
            response = self.client.post('/run_simulation',
                                         data=json.dumps(simulation_input),
                                         content_type='application/json')
            self.assert_status(response, 500) # Use assert_status
            response_json = json.loads(response.data.decode('utf-8'))
            self.assertIn("Simulation execution failed", response_json.get("error"))

        def test_invalid_goal_connections(self):
            simulation_input = { "goalConnections": 0 } # Invalid goalConnections
            response = self.client.post('/run_simulation',
                                         data=json.dumps(simulation_input),
                                         content_type='application/json')
            self.assert_status(response, 500) # Use assert_status
            response_json = json.loads(response.data.decode('utf-8'))
            self.assertIn("Simulation execution failed", response_json.get("error"))

        def test_invalid_network_type(self):
            simulation_input = { "networkType": 99 } # Invalid networkType
            response = self.client.post('/run_simulation',
                                         data=json.dumps(simulation_input),
                                         content_type='application/json')
            self.assert_status(response, 500) # Use assert_status
            response_json = json.loads(response.data.decode('utf-8'))
            self.assertIn("Simulation execution failed", response_json.get("error"))

        def test_invalid_confidence_param_too_high(self):
            simulation_input = { "confidence": 2.0 } # Invalid confidence (greater than 1)
            response = self.client.post('/run_simulation',
                                         data=json.dumps(simulation_input),
                                         content_type='application/json')
            self.assert_status(response, 500) # Use assert_status
            response_json = json.loads(response.data.decode('utf-8'))
            self.assertIn("Simulation execution failed", response_json.get("error"))

        def test_invalid_confidence_param_too_low(self):
            simulation_input = { "confidence": 0.0 } # Invalid confidence (equal to 0)
            response = self.client.post('/run_simulation',
                                         data=json.dumps(simulation_input),
                                         content_type='application/json')
            self.assert_status(response, 500) # Use assert_status
            response_json = json.loads(response.data.decode('utf-8'))
            self.assertIn("Simulation execution failed", response_json.get("error"))

        def test_invalid_algorithm_param(self):
            simulation_input = { "algorithm": "InvalidAlgorithm" } # Invalid algorithm
            response = self.client.post('/run_simulation',
                                         data=json.dumps(simulation_input),
                                         content_type='application/json')
            self.assert_status(response, 500) # Use assert_status
            response_json = json.loads(response.data.decode('utf-8'))
            self.assertIn("Simulation execution failed", response_json.get("error"))

        def test_invalid_K_param(self):
            simulation_input = { "K": 0 } # Invalid K (less than 1)
            response = self.client.post('/run_simulation',
                                         data=json.dumps(simulation_input),
                                         content_type='application/json')
            self.assert_status(response, 500) # Use assert_status
            response_json = json.loads(response.data.decode('utf-8'))
            self.assertIn("Simulation execution failed", response_json.get("error"))

        def test_invalid_network_name(self):
            simulation_input = { "network": "TestNetwork" } # Invalid network name
            response = self.client.post('/run_simulation',
                                         data=json.dumps(simulation_input),
                                         content_type='application/json')
            self.assert_status(response, 500) # Use assert_status
            response_json = json.loads(response.data.decode('utf-8'))
            self.assertIn("Simulation execution failed", response_json.get("error"))

        def test_invalid_bitrate_param(self):
            simulation_input = { "bitrate": "invalid-rate" } # Invalid bitrate
            response = self.client.post('/run_simulation',
                                         data=json.dumps(simulation_input),
                                         content_type='application/json')
            self.assert_status(response, 500) # Use assert_status
            response_json = json.loads(response.data.decode('utf-8'))
            self.assertIn("Simulation execution failed", response_json.get("error"))