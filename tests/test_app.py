import os
import sys
from pathlib import Path

# Add project root to sys.path so 'app' can be imported when running pytest directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Suppress TensorFlow logging to keep test output clean and pristine
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import pytest

from app import create_app, review_to_sequence

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


@pytest.fixture
def app():
    """Create and configure a Flask app instance for testing."""
    app_instance = create_app({"TESTING": True})
    return app_instance


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def test_home_page_returns_ok_and_renders_template(client):
    """GET / returns 200, includes 'CritiQ', and references styles.css and app.js."""
    response = client.get("/")
    assert response.status_code == 200

    html = response.get_data(as_text=True)
    assert "CritiQ" in html
    assert "/static/styles.css" in html
    assert "/static/app.js" in html


def test_health_endpoint_returns_expected_metadata(client):
    """GET /health returns 200 and expected status, model, vocab, and length info."""
    response = client.get("/health")
    assert response.status_code == 200

    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["model_loaded"] is True
    assert payload["vocab_size"] == 10000
    assert payload["max_len"] == 200


def test_review_to_sequence_shape_and_unknown_words():
    """review_to_sequence() produces shape (1, 200) and maps unknown words to index 2."""
    unknown_word = "supercalifragilisticnonexistenttoken12345"
    seq = review_to_sequence(unknown_word)

    assert seq.shape == (1, 200)
    # Padded on left with 0s, unknown token placed at the end with index 2
    assert seq[0][-1] == 2
    assert seq[0][0] == 0

    # Test combination with a known word
    combined_seq = review_to_sequence(f"great {unknown_word}")
    assert combined_seq.shape == (1, 200)
    assert combined_seq[0][-1] == 2
    assert combined_seq[0][-2] > 2


def test_predict_valid_positive_review(client):
    """POST /predict with a valid positive review returns 200 and required fields."""
    response = client.post(
        "/predict",
        json={"review": "This movie was absolutely fantastic, brilliant, and wonderful!"},
    )
    assert response.status_code == 200

    payload = response.get_json()
    assert "label" in payload
    assert "score" in payload
    assert "confidence" in payload
    assert "percent" in payload

    assert payload["label"] == "Positive"
    assert isinstance(payload["score"], float)
    assert 0.0 <= payload["score"] <= 1.0
    assert isinstance(payload["confidence"], float)
    assert 0.0 <= payload["confidence"] <= 1.0
    assert isinstance(payload["percent"], float)
    assert 0.0 <= payload["percent"] <= 100.0


def test_predict_empty_or_whitespace_review_returns_bad_request(client):
    """POST /predict with empty or whitespace-only review returns 400 Bad Request."""
    # Empty string
    response = client.post("/predict", json={"review": ""})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Please enter a movie review."

    # Whitespace only
    response = client.post("/predict", json={"review": "    \t  \n  "})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Please enter a movie review."

    # Missing or empty body
    response = client.post("/predict", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Please enter a movie review."


def test_predict_fewer_than_min_words_returns_bad_request(client):
    """POST /predict with fewer than 3 words returns 400 Bad Request."""
    response = client.post("/predict", json={"review": "Good movie"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Please enter at least 3 words."

    response = client.post("/predict", json={"review": "Awesome!"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Please enter at least 3 words."


def test_predict_exceeding_max_characters_returns_payload_too_large(client):
    """POST /predict with > 5000 characters returns 413 Payload Too Large."""
    long_review = "great " * 1000  # 6000 characters
    assert len(long_review) > 5000

    response = client.post("/predict", json={"review": long_review})
    assert response.status_code == 413
    assert "Review must not exceed 5000 characters." in response.get_json()["error"]


def test_cors_headers_present_on_responses(client):
    """Verify CORS headers (Access-Control-Allow-Origin: *) are present on responses."""
    endpoints = [
        ("GET", "/"),
        ("GET", "/health"),
        ("POST", "/predict", {"review": "A truly wonderful and moving film"}),
    ]

    for item in endpoints:
        if item[0] == "GET":
            response = client.get(item[1])
        else:
            response = client.post(item[1], json=item[2])

        assert response.headers.get("Access-Control-Allow-Origin") == "*"
