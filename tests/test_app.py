import pytest
import os
import json
import sys
import base64
from unittest.mock import MagicMock, patch
from io import BytesIO
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

@pytest.fixture
def client():
    """Flask test client setup."""
    app.config["TESTING"] = True
    client = app.test_client()
    yield client

def test_homepage(client):
    """Test that the homepage loads successfully."""
    response = client.get("/")
    assert response.status_code == 200

def generate_test_image():
    """Create a fake image file for testing."""
    img = Image.new("RGB", (100, 100), color="red")
    img_io = BytesIO()
    img.save(img_io, "JPEG")
    img_io.seek(0)
    return img_io

@patch("google.generativeai.GenerativeModel.generate_content")
def test_analyze_meme_success(mock_generate_content, client):
    """Test successful meme analysis with a valid image."""
    
    mock_response = MagicMock()
    mock_response.text = "This meme is funny because it uses irony."
    mock_generate_content.return_value = mock_response

    test_image = generate_test_image()

    data = {
        "meme": (test_image, "test_meme.jpg")
    }
    
    response = client.post("/analyze_meme", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "explanation" in data
    assert data["explanation"] == "This meme is funny because it uses irony."

def test_analyze_meme_no_image(client):
    """Test error when no image is uploaded."""
    response = client.post("/analyze_meme", content_type="multipart/form-data")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

def test_analyze_meme_empty_file(client):
    """Test error when an empty file is uploaded."""
    empty_file = BytesIO()
    data = {
        "meme": (empty_file, "empty.jpg")
    }

    response = client.post("/analyze_meme", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

@patch("google.generativeai.GenerativeModel.generate_content")
def test_analyze_meme_api_failure(mock_generate_content, client):
    """Test when the AI API fails."""
    mock_generate_content.side_effect = Exception("Mocked API failure")

    test_image = generate_test_image()

    data = {
        "meme": (test_image, "test_meme.jpg")
    }

    response = client.post("/analyze_meme", data=data, content_type="multipart/form-data")
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
