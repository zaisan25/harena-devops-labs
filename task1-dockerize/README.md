# Dockerization of Application

This project is a Python 3.11 Streamlit app packaged with Docker Compose.

## Purpose

The app shows a live operations dashboard with:

- CPU, memory, and disk usage
- readiness and liveness checks
- recent structured logs
- an on-demand refresh action

## Stack

- Python
- pip
- Streamlit
- psutil
- Docker
- Docker Compose

## Project Structure

- `ui/` — Streamlit dashboard UI
- `core/` — metrics, config, health, and command execution helpers
- `infra/` — structured logging
- `logs/` — runtime log output inside the container

## Run with Docker

Build and start the app:

```bash
docker compose up --build
```

Open:

```text
http://localhost:8501
```

## Runtime Configuration

Environment variables used by the container:

- `LOG_LEVEL` — log level for structured logging (`INFO`, `DEBUG`, `WARNING`, `ERROR`)
- `REFRESH_RATE` — auto-refresh interval in seconds, default `5`

## Logging

Logs are written as JSON to `/app/logs/app.json.log`.

The Compose file mounts the `logs_volume` named volume at `/app/logs`, so logs persist across container recreates.

## Healthcheck

Docker Compose checks the Streamlit health endpoint at `/_stcore/health`.

## Notes

- The image sets `PYTHONPATH=/app` so imports like `core.metrics` work correctly.
- The dashboard uses custom SVG icons instead of emoji.
- The UI refreshes automatically and also supports a manual refresh button.
