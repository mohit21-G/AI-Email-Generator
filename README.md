# AI Email Generator REST API 📧

A production-ready, high-performance REST API built with FastAPI, wrapping the Cohere AI language model for automated professional email generation.

---

## Project Overview

The AI Email Generator API packages an existing AI model integration into a modular, production-hardened REST API with authentication, rate limiting, request validation, structured logging, health checks, and Docker support.

---

## Architecture

```text
Client (Web / Streamlit / Mobile)
        │
        ▼
HTTPS / Reverse Proxy / Load Balancer
        │
        ▼
FastAPI REST API Container (:8000)
        │
        ├── API Key Authentication (X-API-Key)
        ├── Rate Limiting (slowapi)
        ├── Pydantic Request Validation
        │
        ▼
EmailService Layer
        │
        ▼
utils.getLLMResponse() (Preserved AI Model)
        │
        ▼
Cohere API (command-a-03-2025 Model)
        │
        ▼
Standardized JSON Response
```

---

## Environment Variables

| Variable Name | Required | Default Value | Description |
| :--- | :---: | :--- | :--- |
| `COHERE_API_KEY` | **Yes** | `""` | Cohere API authentication key |
| `API_KEY` | **Yes** | `email-gen-secret-key-2026` | Secret key required in `X-API-Key` HTTP header |
| `API_URL` | No | `http://localhost:8000/api/v1` | Base API URL used by frontend clients |
| `API_PREFIX` | No | `/api/v1` | URL prefix for API endpoints |
| `PROJECT_NAME` | No | `AI Email Generator API` | Title displayed in OpenAPI docs |
| `HOST` | No | `0.0.0.0` | Host address to bind Uvicorn |
| `PORT` | No | `8000` | Port number to bind Uvicorn |
| `ALLOWED_ORIGINS` | No | `http://localhost:8501,http://127.0.0.1:8501,http://localhost:8000` | Comma-separated CORS allowed origins |
| `RATE_LIMIT` | No | `10 per minute` | Configurable request rate limit |

---

## Local Setup

### 1. Installation & Execution
```bash
# Clone the repository and navigate to directory
cd Email_genrater-main

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend server
uvicorn main:app --reload --port 8000

# In a separate terminal, start Streamlit frontend
streamlit run app.py
```

---

## Docker

### Build Image
```bash
docker build -t ai-email-generator-api .
```

### Run Container
```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name ai_email_api \
  ai-email-generator-api
```

---

## Docker Compose

```bash
# Start backend in detached mode
docker compose up -d --build

# Stop container
docker compose down
```

---

## Production Deployment

The API is deployment-ready for cloud container platforms (such as Render, Fly.io, AWS App Runner, or Kubernetes).

### Render Cloud Deployment
1. Connect your repository to Render.
2. Select **Web Service** using Docker runtime (uses `render.yaml`).
3. Set the Environment Variables (`COHERE_API_KEY`, `API_KEY`, `ALLOWED_ORIGINS`) in the Render Dashboard.
4. Render will automatically issue SSL/TLS certificates and serve traffic via HTTPS:
   ```text
   https://api.yourdomain.com
   ```

---

## API Authentication

All protected endpoints require an `X-API-Key` HTTP header:

```http
X-API-Key: YOUR_API_KEY
```

Requests without a valid key will return `HTTP 401 Unauthorized`.

---

## API Endpoints

| Method | Endpoint | Auth | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/health` | No | Container liveness check |
| `GET` | `/ready` | No | Readiness probe (checks environment config) |
| `GET` | `/docs` | No | Interactive Swagger UI documentation |
| `GET` | `/redoc` | No | ReDoc API specification |
| `POST` | `/api/v1/email/generate` | **Yes** | Generate professional AI email |

---

## Error Codes

| Status Code | Code String | Description |
| :---: | :--- | :--- |
| `401` | `UNAUTHORIZED` | Missing or invalid `X-API-Key` HTTP header |
| `422` | `VALIDATION_ERROR` | Invalid or empty request payload fields |
| `429` | `TOO_MANY_REQUESTS` | Rate limit exceeded |
| `500` | `INTERNAL_SERVER_ERROR` | Unexpected backend error |
| `503` | `SERVICE_UNAVAILABLE` | Service not ready / missing configuration |

---

## CURL Example

### Local Execution
```bash
curl -X POST "http://localhost:8000/api/v1/email/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: email-gen-secret-key-2026" \
  -d '{
    "topic": "Project status update",
    "sender": "Mohit",
    "recipient": "Team Lead",
    "style": "Formal"
  }'
```

### Production HTTPS Execution
```bash
curl -X POST "https://api.yourdomain.com/api/v1/email/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_PRODUCTION_API_KEY" \
  -d '{
    "topic": "Project status update",
    "sender": "Mohit",
    "recipient": "Team Lead",
    "style": "Formal"
  }'
```

### Example API Response (`HTTP 200 OK`)
```json
{
  "success": true,
  "message": "Email generated successfully",
  "data": {
    "email_text": "Subject: Project Status Update\n\nDear Team Lead,\n...",
    "topic": "Project status update",
    "sender": "Mohit",
    "recipient": "Team Lead",
    "style": "Formal",
    "generated_at": "2026-08-25T18:00:00.000000+00:00"
  },
  "error": null
}
```

---

## Security Notes

1. `.env` is listed in `.gitignore` and is never committed to Git.
2. Secrets are injected at runtime via environment variables or cloud key vaults.
3. API keys, full prompts, and generated content are never written to server logs.
4. Containers run as a non-privileged `appuser`.
