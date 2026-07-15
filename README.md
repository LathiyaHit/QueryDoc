# QueryDoc: Real-Time Voice & Text RAG Assistant

A personalized AI-powered voice assistant with ultra-low latency, built using FastAPI, Flask, Qdrant, Deepgram, and Groq. It supports Retrieval-Augmented Generation (RAG) through both text and voice interfaces.

## 🌟 Features

- **Voice & Text Interface**: Interact with the assistant using real-time voice (WebSocket) or standard text requests.
- **RAG Pipeline**: Upload documents (PDFs, text) to perform intelligent, context-aware querying.
- **Ultra-Low Latency**: Optimized voice processing pipeline using Deepgram and Groq.
- **Vector Search**: High-performance semantic search powered by Qdrant.
- **Background Tasks**: Celery and Redis for asynchronous document processing and worker tasks.
- **Observability**: OpenTelemetry and Jaeger integrated for comprehensive tracing and monitoring.

## 🏗 Tech Stack

- **Backend API**: FastAPI, Python 3.11
- **Frontend**: Flask, HTML/JS
- **Voice Pipeline**: Deepgram SDK, Groq, PyTorch, torchaudio
- **Vector Database**: Qdrant
- **Relational Database**: PostgreSQL
- **Cache & Message Broker**: Redis
- **Task Queue**: Celery
- **Containerization**: Docker & Docker Compose

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- Python 3.11+ (if running locally without Docker)
- Make (optional, but recommended for ease of use)

### 1. Configuration

Ensure you have a `.env` file in the root directory. You can configure your necessary API keys and environment variables (e.g., Deepgram API key, Groq API key, Database credentials) here.

### 2. Running the Backend Infrastructure

To start the infrastructure (Redis, Postgres, Qdrant, Jaeger) and the API in development mode, simply run:

```bash
make dev
```

**Note on Documents:** The application requires a default document to answer questions out-of-the-box. While `make dev` is running, open a new terminal and run the following command to populate Qdrant with the default PDF:

```bash
make ingest
```
*(This command starts the background Docker containers and runs the FastAPI server locally on port 8000).*

If you want to build and run all services entirely via Docker:
```bash
make build
docker-compose up
```

### 3. Running the Frontend

In a separate terminal, start the Flask frontend application:

```bash
make frontend
```
The frontend will be available at `http://localhost:5001` (or the port specified by your `FLASK_PORT` env variable).

### 4. Running the Worker

The Celery worker processes background tasks such as document indexing. If running locally (not via docker-compose), you can start it using:
```bash
celery -A workers.main.celery_app worker --loglevel=info
```

## 📡 API Endpoints

Once the backend is running, you can access the interactive API documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Routers:
- `GET /health` - API health check
- `/api/v1/voice/*` - WebSocket and REST endpoints for voice interaction
- `/api/v1/documents/*` - Endpoints for document upload and RAG management
- `/api/v1/users/*` - User management

## 🛠 Development Commands

The `Makefile` includes several helpful commands:

- `make dev`: Start infrastructure containers and FastAPI in reload mode.
- `make frontend`: Start the Flask frontend.
- `make test`: Run all tests with coverage.
- `make test-unit`: Run only unit tests.
- `make test-integration`: Run integration tests.
- `make migrate`: Apply database migrations using Alembic.
- `make migrate-new msg="your_message"`: Autogenerate a new database migration.
- `make lint`: Run Ruff and Black to check code formatting.
- `make format`: Auto-format code with Black and Ruff.
- `make clean`: Clean up Python cache and compiled files.

## 📂 Project Structure

- `/frontend` - Flask web interface for voice/text interactions.
- `/services/api` - FastAPI core application and REST/WebSocket endpoints.
- `/services/api/app` - Core business logic, voice processing pipelines, and ML models.
- `/workers` - Celery worker definitions for background jobs.
- `/tests` - Unit and integration tests.