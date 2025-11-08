# KubenAI — Local AI Chat Gateway (UI + API)

A small, modular AI chat assistant stack that separates the frontend UI (KubenAI-ui) from a backend API gateway (KubenAI-API). The API gateway provides a single unified interface to multiple AI providers (DigitalOcean Inference API and Azure OpenAI). The UI talks to the API and exposes a friendly chat interface in your browser.

This repository contains everything you need to run both services locally using Docker. It is written to be easy to run for developers with no prior knowledge of the project.

## Contents

- `KubenAI-API/` — FastAPI backend (exposes `/api/chat`, `/api/completion`, `/health`, and `/docs`).
- `KubenAI-ui/` — Frontend UI (Streamlit or similar) connecting to the backend API.
- `docker-compose.yml` — Top-level compose file that builds and runs both services on a shared network.

---

## Quick overview — what this does

- Start a containerized backend API that forwards chat/completion requests to your chosen AI provider (DigitalOcean or Azure).
- Start a containerized UI that provides a web chat experience and communicates with the backend via HTTP.
- Everything runs in Docker and is networked together so the UI can call the API using the internal service name `api`.

---

## Prerequisites

- Docker Desktop or Docker Engine installed and running (Linux/macOS/Windows).
- Docker Compose v2 (the `docker compose` CLI command). If your system uses legacy `docker-compose`, swap commands accordingly.
- A DigitalOcean Inference API endpoint, API key, and model name OR Azure OpenAI credentials if you prefer Azure.
  - For DigitalOcean you should have:
    - Inference endpoint (e.g. `https://inference.do-ai.run/v1`)
    - API key (recommended format: `Bearer <your-key>`)
    - Model name (e.g. `openai-gpt-oss-120b`)

---

## Secure your credentials

- Do NOT commit secrets (API keys) into source control. Use `.env` files (which are included in `.gitignore`) or a secret manager for production.
- The example files are named `.env.example`. Copy them to `.env` and update the values locally.

---

## Configuration — Environment Setup

This project uses a single `.env` file at the root level to configure both services. The root `.env` contains all necessary settings for both the API and UI components.

### Local Development Setup

1. Copy the example environment file to create your local config:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your actual values:

   - `AI_PROVIDER`: Set to either 'azure' or 'digitalocean'
   - For DigitalOcean:
     - `DIGITALOCEAN_INFERENCE_ENDPOINT`: Your DO inference endpoint
     - `DIGITALOCEAN_API_KEY`: Your DO API key (format: "Bearer your-key-here")
     - `DIGITALOCEAN_MODEL`: The model to use (e.g., "openai-gpt-oss-120b")
   - For Azure OpenAI:
     - Add your Azure OpenAI credentials (see .env.example for format)

3. The environment will be automatically passed to both services via Docker Compose.

Note: Never commit the `.env` file to source control — it's listed in `.gitignore` to prevent accidental commits.

Example (API):

KubenAI-API/.env (create by copying `.env.example` and editing):

```
AI_PROVIDER=digitalocean
DIGITALOCEAN_INFERENCE_ENDPOINT=https://inference.do-ai.run/v1
DIGITALOCEAN_API_KEY=Bearer YOUR_DIGITALOCEAN_KEY_HERE
DIGITALOCEAN_MODEL=openai-gpt-oss-120b

# Optional API bind configuration
API_HOST=0.0.0.0
API_PORT=8000

DEFAULT_SYSTEM_PROMPT=You are a helpful AI assistant.
```

Example (UI):

KubenAI-ui/.env (create by copying `.env.example` and editing):

```
CHAT_API_TYPE=digitalocean
USE_LOCAL_API=true
LOCAL_CHAT_API_BASE_URL=http://api:8000
LOCAL_CHAT_API_ENDPOINT=/api/chat

# DigitalOcean config (for the UI if it needs to call DO directly)
DIGITALOCEAN_INFERENCE_ENDPOINT=https://inference.do-ai.run/v1
DIGITALOCEAN_API_KEY=Bearer YOUR_DIGITALOCEAN_KEY_HERE
DIGITALOCEAN_MODEL=openai-gpt-oss-120b
```

Notes:

- The top-level `docker-compose.yml` included with this repo reads env files for each service. By default the compose file points to the example files. If you copy `.env.example` -> `.env`, edit the compose file to point to the new `.env` paths or simply overwrite the `.env.example` (not recommended for source control safety).
- Recommended flow: copy `.env.example` -> `.env` for both services and then, in the project root, edit `docker-compose.yml` env_file paths to reference `./KubenAI-API/.env` and `./KubenAI-ui/.env`.

Example sed command (macOS / zsh) to switch both services' env_file entries to `.env`:

```bash
# from project root (/path/to/K8s_AI)
sed -i '' 's|./KubenAI-API/.env.example|./KubenAI-API/.env|g' docker-compose.yml
sed -i '' 's|./KubenAI-ui/.env.example|./KubenAI-ui/.env|g' docker-compose.yml
```

If you're uncomfortable running the sed command, open `docker-compose.yml` in your editor and change the `env_file` lines manually.

---

## Run everything with Docker (recommended)

From the project root (where this README and `docker-compose.yml` live):

You can either run Docker Compose directly or use the included convenience scripts.

Use the scripts (recommended for convenience):

```bash
cd /path/to/K8s_AI
./start.sh   # builds and starts the stack in detached mode
```

Or run Docker Compose directly:

1. Build and run in the background (detached):

```bash
cd /path/to/K8s_AI
docker compose up -d --build
```

Flags explained:

- `-d` / `--detach`: run containers in the background
- `--build`: build images before starting (use if code/Dockerfile changed)

2. Check service status:

```bash
docker compose ps
```

3. Follow logs (live):

```bash
docker compose logs -f api
docker compose logs -f ui
```

4. Stop and remove containers when done:

```bash
docker compose down
```

To remove volumes as well (be careful):

```bash
docker compose down -v
```

---

## Verify the services are working

- Backend API docs (Swagger): http://localhost:8000/docs
- Backend health: http://localhost:8000/health
- UI: http://localhost:8501 (Streamlit or similar UI port)

Example health check (curl):

```bash
curl http://localhost:8000/health
```

Example chat request (curl):

```bash
curl -s -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, who are you?"}
    ],
    "system_prompt": "You are a helpful assistant.",
    "temperature": 0.7,
    "max_tokens": 300
  }'

# Expected response structure: {"response": "...", "model": "...", "usage": {...}}
```

Example completion request (curl):

```bash
curl -s -X POST "http://localhost:8000/api/completion" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a 2-sentence summary of Kubernetes.",
    "system_prompt": "You are a concise assistant.",
    "temperature": 0.5,
    "max_tokens": 80
  }'
```

---

## Using DigitalOcean Inference API (what to update)

If you want to use DigitalOcean as the provider for the backend API, make sure `KubenAI-API/.env` contains:

- `AI_PROVIDER=digitalocean`
- `DIGITALOCEAN_INFERENCE_ENDPOINT` — your inference base endpoint (do NOT include `/chat/completions`)
- `DIGITALOCEAN_API_KEY` — your DigitalOcean API key, recommended with the `Bearer ` prefix
- `DIGITALOCEAN_MODEL` — the name of the model to use

Example values (DO NOT commit these values to git):

```
AI_PROVIDER=digitalocean
DIGITALOCEAN_INFERENCE_ENDPOINT=https://inference.do-ai.run/v1
DIGITALOCEAN_API_KEY=Bearer sk-do-xxxxxxxxxxxxxxxxxxxxx
DIGITALOCEAN_MODEL=openai-gpt-oss-120b
```

The backend will call the DigitalOcean endpoint at `DIGITALOCEAN_INFERENCE_ENDPOINT` + `/chat/completions`.

---

## Running only a single service

To run only the API:

```bash
docker compose up -d --build api
```

To run only the UI:

```bash
docker compose up -d --build ui
```

Note: the UI depends on the API; if you run the UI only you should set `LOCAL_CHAT_API_BASE_URL` in the UI env to point to a running API instance URL.

---

## Development: running locally without Docker

If you prefer to run the services directly (Python virtualenv) use the provided `requirements.txt` files in each subfolder. Example for the API:

```bash
cd KubenAI-API
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit .env with your keys
python start.py
# or: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

And for the UI, follow the instructions in `KubenAI-ui/README.md` or run its `src/main.py` as directed in that folder.

---

## Production considerations

- Secrets: Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault, or Docker secrets) instead of plain `.env` files.
- TLS: Put a reverse proxy (Traefik, Nginx) in front of the services to serve TLS and route requests securely.
- Scaling: The backend is stateless (the conversation history is supplied by the client). You can scale API replicas behind a load balancer.
- Logging & Monitoring: Integrate centralized logging and metrics (Prometheus, Grafana, ELK/Opensearch).
- Rate limiting & authentication: Add authentication if exposing the API to untrusted networks.

---

## Troubleshooting

- If the UI cannot reach the API: ensure the Docker network is up and that the UI env `LOCAL_CHAT_API_BASE_URL` is `http://api:8000` (the service name used by docker-compose).
- If the backend fails to start: check logs (`docker compose logs -f api`) and verify your `.env` contains valid keys and endpoints.
- If responses are slow or failing: verify that your DigitalOcean/Azure credentials are valid and that the model name is supported.

---

## Security & Licensing

- This README and code are provided as-is. Remove any hard-coded secrets before publishing. Add a LICENSE file to the repo with your chosen license.

---

## Next steps / Suggestions

- Add automated tests that exercise `/api/chat` and `/api/completion` using a mocked or test AI provider.
- Add CI that builds the Docker images and runs basic smoke tests.
- Add support for environment-specific compose overrides for production (e.g., `docker-compose.prod.yml`).

---
