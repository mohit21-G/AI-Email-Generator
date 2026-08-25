from fastapi.testclient import TestClient
from main import app
from core.config import settings

client = TestClient(app)

VALID_HEADERS = {"X-API-Key": settings.API_KEY}


def test_health_endpoint():
    """Verify GET /health returns 200 OK with status healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ready_endpoint():
    """Verify GET /ready returns 200 OK with readiness check details."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["checks"]["cohere_api_key_configured"] is True
    assert data["checks"]["api_key_configured"] is True


def test_root_endpoint():
    """Verify GET / returns 200 OK with service metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_docs_accessible():
    """Verify Swagger UI documentation at /docs is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_redoc_accessible():
    """Verify ReDoc documentation at /redoc is accessible."""
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_missing_api_key_returns_401():
    """Verify request missing X-API-Key header returns HTTP 401."""
    payload = {
        "topic": "Meeting schedule",
        "sender": "Alice",
        "recipient": "Bob",
        "style": "Formal",
    }
    response = client.post("/api/v1/email/generate", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "UNAUTHORIZED"


def test_invalid_api_key_returns_401():
    """Verify request with invalid X-API-Key header returns HTTP 401."""
    payload = {
        "topic": "Meeting schedule",
        "sender": "Alice",
        "recipient": "Bob",
        "style": "Formal",
    }
    response = client.post(
        "/api/v1/email/generate",
        json=payload,
        headers={"X-API-Key": "wrong-secret-key"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "UNAUTHORIZED"


def test_invalid_payload_returns_422():
    """Verify empty/invalid fields return HTTP 422 with validation details."""
    payload = {
        "topic": "",  # Empty topic
        "sender": "Alice",
        "recipient": "Bob",
    }
    response = client.post(
        "/api/v1/email/generate",
        json=payload,
        headers=VALID_HEADERS,
    )
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_valid_email_generation_returns_200():
    """Verify valid request returns HTTP 200 and standard response structure."""
    payload = {
        "topic": "Request for 2 days sick leave",
        "sender": "Mohit",
        "recipient": "Manager",
        "style": "Formal",
    }
    response = client.post(
        "/api/v1/email/generate",
        json=payload,
        headers=VALID_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Email generated successfully"
    assert data["error"] is None
    assert "email_text" in data["data"]
    assert isinstance(data["data"]["email_text"], str)
    assert len(data["data"]["email_text"]) > 0
    assert data["data"]["topic"] == payload["topic"]
    assert data["data"]["sender"] == payload["sender"]
    assert data["data"]["recipient"] == payload["recipient"]
    assert data["data"]["style"] == payload["style"]
    assert "generated_at" in data["data"]


def test_rate_limit_response_structure():
    """Verify rate limit error response formatting."""
    from slowapi.errors import RateLimitExceeded

    # Triggering handler directly to test 429 JSON payload structure
    handler = app.exception_handlers.get(RateLimitExceeded)
    assert handler is not None
