import unittest
from flask import Flask
from resume import resume_bp
from io import BytesIO
from unittest.mock import patch
import base64

class ResumeTestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(resume_bp)
        self.app = app.test_client()
        self.app.testing = True
