# Tests for help endpoint

from flask_testing import TestCase
from backend import app
import pytest

class TestHelpEndpoint(TestCase):
  """Tests for help endpoint"""
  
  def create_app(self):
    app.config['TESTING'] = True
    return app
  
  def test_help_endpoint_success(self):
    response = self.client.get('/help')
    self.assert200(response)