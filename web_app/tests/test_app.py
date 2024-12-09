import os
import pytest
from unittest.mock import patch, MagicMock
from flask import session
from app import create_app

@pytest.fixture
def app():
    with patch.dict(
        os.environ,
        {"MONGO_URI": "mongodb://localhost:27017/test_db"}
    ):
        app = create_app()
        app.config.update(
            TESTING=True,
            SECRET_KEY="test_secret_key",
        )
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_db():
    with patch("app.MongoClient") as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        yield mock_db

def test_home_redirects_to_login_if_not_logged_in(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_home_redirects_to_dashboard_if_logged_in(client):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/")
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]

def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200

def test_login_post_success(client, mock_db):
    mock_db.resume_db.users.find_one.return_value = {"email": "test@example.com", "password": "password123"}
    response = client.post("/login", data={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]

def test_login_post_failure(client, mock_db):
    mock_db.resume_db.users.find_one.return_value = None
    response = client.post("/login", data={"email": "wrong@example.com", "password": "wrongpass"})
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200

def test_register_post_success(client, mock_db):
    mock_db.resume_db.users.find_one.return_value = None
    response = client.post("/register", data={"email": "new@example.com", "password": "password123"})
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_register_post_failure(client, mock_db):
    mock_db.resume_db.users.find_one.return_value = {"email": "existing@example.com"}
    response = client.post("/register", data={"email": "existing@example.com", "password": "password123"})
    assert response.status_code == 200
    assert b"Email already registered" in response.data

def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_dashboard_logged_in(client, mock_db):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    mock_db.resume_db.resumes.find.return_value = []
    response = client.get("/dashboard")
    assert response.status_code == 200

def test_save_resume_success(client, mock_db):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.post(
        "/save_resume",
        json={"name": "Test Resume", "pdf": "data:application/pdf;base64,SGVsbG8gd29ybGQ="},
    )
    assert response.status_code == 200
    assert b"Resume saved successfully" in response.data

def test_save_resume_missing_pdf(client):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.post(
        "/save_resume",
        json={"name": "Test Resume"}
    )
    assert response.status_code == 400
    assert b"PDF data is missing" in response.data

def test_logout(client):
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    with client.session_transaction() as sess:
        assert "email" not in sess
