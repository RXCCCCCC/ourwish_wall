# GitHub Copilot Instructions — ourwish_wall

These concise instructions help AI coding agents be productive in this repository.

Summary
- Project: "数字传承 · 红色德兴" 心愿墙 (Flask backend + Vue 3 frontend).
- Backend: `backend/` — Flask app (app.py), SQLAlchemy models (models.py), services (services/).
- Frontend: `frontend/` — Vite + Vue3 + Pinia, API client at `frontend/src/api/index.js`.

Quick goals for agents
- Preserve the app factory in `backend/app.py` (create_app) and keep route signatures unchanged.
- Database models live in `backend/models.py`; migrations are NOT present — prefer `init_db.py` for setup.
- AI behavior is mocked in `backend/services/ai_service.py`; only change to real LLMs after toggling flags in `backend/config.py`.

Concrete developer workflows (commands)
- Backend dev:
  - Install: `cd backend && pip install -r requirements.txt`
  - Init DB (dev): `python init_db.py`
  - Run dev server: `python app.py` (or set `FLASK_ENV=production` and use `gunicorn` per `backend/README.md`).
- Frontend dev:
  - Install: `cd frontend && npm install`
  - Run dev server: `npm run dev`
  - Build: `npm run build`

Environment / config notes
- Backend config: `backend/config.py` controls DB connection (`DATABASE_URL` or DB_* vars), `RATE_LIMIT_*`, `MAX_CONTENT_LENGTH`, and AI toggles (`AI_SERVICE_ENABLED`, `AI_API_KEY`, `AI_API_ENDPOINT`).
- Frontend API base: `frontend/src/api/index.js` reads `VITE_API_BASE_URL` (default `http://localhost:5000`).

Project-specific patterns and gotchas
- Rate limiting: implemented via `RateLimit` model (table `rate_limits`) and enforced in `app.create_wish()`; tests or changes to limits should consider data cleanup (see `backend/README.md`).
- Content validation: `services/text_filter.py` is the canonical sensitive-word check. It is intentionally minimal — update this file (not routes) when extending filtering.
- AI integration: `services/ai_service.py` is a rulebook-based mock. To enable a real LLM:
  1) Set `AI_SERVICE_ENABLED=True` and populate `AI_API_KEY`/`AI_API_ENDPOINT` in env or `backend/config.py`.
  2) Implement the LLM call in `ai_service.py` and fall back to the rule library on failure.
- Data shaping: model `to_dict()` methods (in `backend/models.py`) format `created_at` (YYYY年MM月DD日). Frontend expects this format.
- Categories: valid heart categories are enforced in `app.create_wish()` — update both backend and frontend if you add new categories.

Integration points
- API routes: defined in `backend/app.py` (e.g., `GET /api/wishes`, `POST /api/wishes`, `/api/stats`). Use `frontend/src/api/index.js` for examples of client calls.
- DB migrations: none present. Use `init_db.py` for table creation in dev; for production, add migration tooling (Flask-Migrate/Alembic) instead of modifying `init_db.py`.

Testing and debugging
- No automated tests included. For quick manual checks:
  - Use curl or Postman against `http://localhost:5000/api/health` and `GET /api/wishes`.
  - Enable SQL logging by setting `SQLALCHEMY_ECHO = True` in `backend/config.py` during debugging.

When modifying code, prefer small, targeted edits
- Change behavior in `services/*` for business logic, `models.py` for schema, and `app.py` only for route-level orchestration.
- Avoid removing the guardrails: rate limit checks, `TextFilter.validate_content`, and model constraints (e.g., unique like constraint).

Where to look for examples
- API client: `frontend/src/api/index.js` — shows axios interceptors and error handling.
- Route patterns and pagination example: `backend/app.py` (get_wishes) handles pagination and category filtering.
- AI mock and how-to: `backend/services/ai_service.py` (commented LLM example and fallback behavior).

If uncertain, ask the maintainer
- File to edit for DB changes: [backend/models.py](backend/models.py)
- File to change for AI integration: [backend/services/ai_service.py](backend/services/ai_service.py)
- File to change for sensitive words: [backend/services/text_filter.py](backend/services/text_filter.py)

Feedback
- If any section is unclear or you want more examples (route-level tests, request/response examples, or migration guidance), tell me which part to expand.
