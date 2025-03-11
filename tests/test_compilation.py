# Tests for simulation compilation

from flask_testing import TestCase
from backend import app, compile_simulation
from tests.test_utils import temporarily_rename_file
import json
import os


class TestCompilation(TestCase):
  """Tests for simulation compilation"""
  
  def create_app(self):
    app.config['TESTING'] = True
    return app

  def test_compilation_failure(self):
    # Test with missing main.cpp file
    with temporarily_rename_file("./src/main.cpp", "./src/main.cpp.temp"):
      compile_result = compile_simulation(debug=True)
      self.assertFalse(compile_result)

      response = self.client.post('/run_simulation',
                                  data=json.dumps({}),
                                  content_type='application/json')
      self.assert_status(response, 500)

    # Test with invalid main.cpp file
    if os.path.exists("./src/test_main.cpp"):
      with temporarily_rename_file("./src/main.cpp", "./src.main.cpp.temp"):
        with temporarily_rename_file("./src/test_main.cpp", "./src/main.cpp"):
          compile_result = compile_simulation(debug=True)
          self.assertFalse(compile_result)

          response = self.client.post('/run_simulation',
                                    data=json.dumps({}),
                                    content_type='application/json')
          self.assert_status(response, 500)

  def test_compilation_success(self):
    compile_result = compile_simulation(debug=True)
    self.assertTrue(compile_result)