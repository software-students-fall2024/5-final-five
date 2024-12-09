import os
import pytest
from unittest.mock import patch, MagicMock
from flask import session
from app import create_app

@pytest.fixture
def app():
    use_real_db = os.getenv("USE_REAL_DB", "false") == "true"
    
    with patch.dict(
        os.environ,
        {"MONGO_URI": "mongodb://localhost:27017/test_db" if use_real_db else "mongodb://localhost:27017/test_db"}
    ):
        app = create_app()
        app.config.update(
            TESTING=True,
            SECRET_KEY="test_secret_key",
        )
        yield app

# Fixture to provide a test client
@pytest.fixture
def client(app):
    return app.test_client()

# Fixture to mock MongoDB if USE_REAL_DB is not set to true
@pytest.fixture
def mock_db():
    if os.getenv("USE_REAL_DB", "false") == "true":
        return None  # Return None to indicate we should use the real MongoDB connection
    
    with patch("app.MongoClient") as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        yield mock_db

# Test if the home route redirects to the login page when not logged in
def test_home_redirects_to_login_if_not_logged_in(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

# Test if the home route redirects to the dashboard if logged in
def test_home_redirects_to_dashboard_if_logged_in(client):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/")
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]

# Test the login page route
def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200

# Test the login functionality with mock database
def test_login_post_success(client, mock_db):
    mock_db.resume_db.users.find_one.return_value = {"email": "test@example.com", "password": "password123"}
    response = client.post("/login", data={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 200

# Test the login failure functionality with mock database
def test_login_post_failure(client, mock_db):
    mock_db.resume_db.users.find_one.return_value = None
    response = client.post("/login", data={"email": "wrong@example.com", "password": "wrongpass"})
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

# Test the registration page route
def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200

# Test successful user registration with mock DB
def test_register_post_success(client, mock_db):
    mock_db.resume_db.users.find_one.return_value = None
    response = client.post("/register", data={"email": "new@example.com", "password": "password123"})
    assert response.status_code == 200

# Test registration failure with mock DB when email already exists
def test_register_post_failure(client, mock_db):
    mock_db.resume_db.users.find_one.return_value = {"email": "existing@example.com"}
    response = client.post("/register", data={"email": "existing@example.com", "password": "password123"})
    assert response.status_code == 200
    assert b"Email already registered" in response.data

# Test if accessing the dashboard requires login
def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

# Test the dashboard page when logged in with mock DB
def test_dashboard_logged_in(client, mock_db):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    mock_db.resume_db.resumes.find.return_value = []
    response = client.get("/dashboard")
    assert response.status_code == 200

# Test saving a resume with mock DB
def test_save_resume_success(client, mock_db):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.post(
        "/save_resume",
        json={"name": "Test Resume", "pdf": "data:application/pdf;base64,SGVsbG8gd29ybGQ="},
    )
    assert response.status_code == 200
    assert b"Resume saved successfully" in response.data

# Test saving a resume when the PDF is missing
def test_save_resume_missing_pdf(client):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.post(
        "/save_resume",
        json={"name": "Test Resume"}
    )
    assert response.status_code == 400
    assert b"PDF data is missing" in response.data

# Test the logout functionality
def test_logout(client):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    with client.session_transaction() as sess:
        assert "email" not in sess
