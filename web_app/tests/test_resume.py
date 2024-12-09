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

    @patch("subprocess.run")
    @patch("builtins.open", return_value=BytesIO(b"mocked PDF content"))
    def test_generate_resume_missing_fields(self, mock_open, mock_subprocess):
        form_data = {
            'name': 'John Doe',
            'phone': '123-456-7890',
            'email': 'john.doe@example.com',
            'institution1': 'University A',
            'degree1': 'BSc Computer Science',
            'date1': '2020',
            'location1': 'City A',
            'company1': 'Company X',
            'role1': 'Software Engineer',
            'expLocation1': 'City B',
            'expDate1': '2021-2023',
            'responsibilities1': 'Developed software; Managed projects;',
            'projectName1': 'Project A',
            'projectTech1': 'Python, Flask',
            'projectDate1': '2022',
            'projectDetails1': 'Developed backend API; Optimized performance;',
            'languages': 'Python, Java',
            'frameworks': 'Flask, Django',
            'tools': 'Git, Docker',
            'libraries': 'NumPy, Pandas',
        }
        response = self.app.post('/generate_resume', data=form_data)
        self.assertEqual(response.status_code, 500)

    def test_missing_required_fields(self):
        form_data = {
            'email': 'john.doe@example.com',
            'institution1': 'University A',
            'degree1': 'BSc Computer Science',
            'date1': '2020',
            'location1': 'City A',
            'company1': 'Company X',
            'role1': 'Software Engineer',
            'expLocation1': 'City B',
            'expDate1': '2021-2023',
            'responsibilities1': 'Developed software; Managed projects;',
            'projectName1': 'Project A',
            'projectTech1': 'Python, Flask',
            'projectDate1': '2022',
            'projectDetails1': 'Developed backend API; Optimized performance;',
            'languages': 'Python, Java',
            'frameworks': 'Flask, Django',
            'tools': 'Git, Docker',
            'libraries': 'NumPy, Pandas',
        }
        response = self.app.post('/generate_resume', data=form_data)
        self.assertEqual(response.status_code, 400)

    @patch("subprocess.run")
    def test_generate_resume_empty_data(self, mock_subprocess):
        form_data = {
            'name': '',
            'phone': '',
            'email': '',
        }
        response = self.app.post('/generate_resume', data=form_data)
        self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()
