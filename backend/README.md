FastAPI backend
================

Endpoints
- `GET /` health check
- `POST /api/screenshot` upload screenshot as multipart form-data (`file`)
- `GET /api/screenshots` list saved screenshots

Run
1) Install dependencies using uv:

   uv sync

2) Start server:

   uv run python -m app.main.py

Files save to `@backend/data/screenshots`.

