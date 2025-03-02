# Tests for simulation compilation

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
    compile_result = compile_simulation(True)
    os.rename("./src/main.cpp.temp", "./src/main.cpp")
    self.assertFalse(compile_result)

    response = self.client.post('/run_simulation',
                                data=json.dumps({}),
                                content_type='application/json')
    self.assert_status(response, 500)

    os.rename("./src/main.cpp", "./src/main.cpp.temp")
    os.rename("./src/test_main.cpp", "./src/main.cpp")
    compile_result = compile_simulation(True)
    self.assertFalse(compile_result)

    response = self.client.post('/run_simulation',
                                data=json.dumps({}),
                                content_type='application/json')
    self.assert_status(response, 500)
    os.rename("./src/main.cpp", "./src/test_main.cpp")
    os.rename("./src/main.cpp.temp", "./src/main.cpp")

  def test_compilation_success(self):
    compile_result = compile_simulation(True)
    self.assertTrue(compile_result)