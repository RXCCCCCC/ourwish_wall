# Copilot instructions for the “我们的心愿墙” repo

These notes are targeted at AI coding agents (Copilot-style) that will be making edits in this repository. They highlight the project structure, important conventions, run/build workflows, and concrete examples of patterns you should follow when making changes.

Keep instructions short and direct — follow them automatically when you change code.

---

## Big picture (what this repo is)
- Monorepo with two main parts:
  - `backend/` — Flask 2.3 app using SQLAlchemy (PyMySQL) and MySQL. Main files: `app.py`, `models.py`, `config.py`, `init_db.py`, `services/`.
  - `frontend/` — Vue 3 + Vite + Pinia + Tailwind CSS. Main entry: `frontend/src/main.js`, views and components under `frontend/src/`.
- Data flow: frontend talks to backend REST API under `/api/*` (e.g. `POST /api/wishes`, `POST /api/wishes/:id/like`, `DELETE /api/wishes/:id`). Backend persists to MySQL via SQLAlchemy models in `models.py`.
- Mobile-first: UI and layout choices intentionally favour small screens — when editing styles prefer `sm`/`md` breakpoints and mobile aesthetics.

## Where to look first (key files)
- Backend
  - `backend/app.py` — primary routes and most server logic. Read this for request flows and validation patterns.
  - `backend/models.py` — SQLAlchemy models: `Wish`, `Comment`, `Like`, `RateLimit`. Note: `Wish.comments` uses `cascade='all, delete-orphan'`, but `Like` has no relationship defined.
  - `backend/init_db.py` — database table creation and sample data insertion. Useful for local testing.
  - `backend/config.py` — DB and runtime configuration; change DB credentials here or via environment variables.
  - `backend/services/` — helper modules: `ai_service.py` (AI reply generation) and `text_filter.py` (content validation).
- Frontend
  - `frontend/src/App.vue` — application shell and the first-visit identity modal (user login/nickname flow).
  - `frontend/src/stores/user.js` — Pinia store controlling the user identity, `login(nickname)`, `setName`, `setColor` and localStorage persistence.
  - `frontend/src/api/index.js` — central place for axios API calls (use this for network changes).
  - `frontend/src/components/*` — UI components. Notable ones:
    - `NavBar.vue` — top navigation and personal-settings modal (nickname & color picker).
    - `WishForm.vue` — creates new wishes and attaches `userStore` data (color, name) to payloads.
    - `WishCard.vue` — rendering wishes; initials/color logic lives here.
    - `charts/ChartsBoard.vue` — ECharts usage (pie + wordcloud) — mobile-friendly options are important.

## Project-specific patterns & conventions
- Backend pattern:
  - Routes in `app.py` generally validate inputs, then `db.session.add()` and `db.session.commit()` inside a try/except; on exception call `db.session.rollback()` and return 500.
  - Rate-limiting is IP-based using `RateLimit` model and committed immediately.
  - When deleting related rows, the code sometimes deletes related `Comment`/`Like` rows explicitly before deleting `Wish` to avoid foreign key errors. There are no Alembic migrations in this repo — schema changes are done by editing `models.py` and re-running `init_db.py` for local dev.
- Frontend pattern:
  - Mobile-first responsive Tailwind classes used everywhere. Use `space-y-*`, `gap-*` and `sm:`/`md:` utilities consistently.
  - User identity is local-first (Pinia + localStorage). `userStore.userInfo` persists the chosen `name` and `color`; colors are client-side only unless backend is extended.
  - UI shows optimistic updates (e.g. like toggles) but code should wait for backend confirmation. If you change optimistic flows, ensure you still handle rollback on API failure.
- Error handling: prefer returning JSON `{error: '...'} ` with appropriate status codes. Backend logs important exceptions via `app.logger.error()`.

## Running & debugging (practical commands)
- Backend (development):
  1. Edit `backend/config.py` or set environment variables for DB credentials.
  2. Ensure MySQL DB exists: `CREATE DATABASE ourwish_wall CHARACTER SET utf8mb4;`
  3. Install deps and init DB:
     ```bash
     cd backend
     pip install -r requirements.txt
     python init_db.py   # creates tables and inserts demo data
     python app.py       # runs dev server at http://localhost:5000
     ```
  4. Use logs printed by Flask or `app.logger.error()` messages for runtime failures.
- Frontend (development):
  ```bash
  cd frontend
  npm install
  npm run dev   # Vite dev server (default http://localhost:5173)
  npm run build # produce production bundle
  ```

## Editing guidance (how you should change code)
- Backend data changes:
  - Always use `db.session.commit()` to persist; wrap in try/except and call `db.session.rollback()` on exceptions.
  - Prefer using model relationships. If you need to change schema, document that there is no migration system — developers re-run `init_db.py` for local testing. For production you must create SQL migrations manually (not provided here).
  - When deleting a `Wish`, be mindful of `Like` records: either create a relationship with cascade delete in `models.py` or ensure `DELETE` logic removes `Like` rows before deleting the `Wish` (see `app.py` delete route example).
- Frontend UI changes:
  - Keep mobile-first. When changing components like `NavBar.vue` or `HeroSection.vue`, test under small widths and ensure Tailwind utilities (`sm:`, `md:`) produce expected layouts.
  - User identity is stored in `localStorage` via `userStore`; update both `userStore` and localStorage when changing name/color.
- API changes:
  - Update `frontend/src/api/index.js` central API helper when adding endpoints or changing shapes. Keep request/response shapes consistent with `app.py` routes.

## Integration points & external dependencies
- MySQL via PyMySQL. Connection configured in `backend/config.py` (DB_HOST/DB_USER/DB_PASSWORD/DB_NAME). Ensure charset utf8mb4.
- ECharts (plus `echarts-wordcloud`) used in frontend charts. Adjust chart options in `ChartsBoard.vue` for mobile-friendly rendering.
- Vant UI is used for mobile components. Import patterns are in `frontend/src/main.js`.
- AI response generation code is in `backend/services/ai_service.py` (mock or placeholder). Changes here may require API-key or external services.

## Concrete examples to cite while editing
- Deleting a wish safely: `backend/app.py` `DELETE /api/wishes/<id>` currently deletes `likes` and `comments` then `wish` and commits. If you add `Like` relationship, update `models.py` and remove manual deletes.
- User local identity: `frontend/src/stores/user.js` provides `login(nickname)`, `setName(name)`, and `setColor(color)` and persists to `localStorage`.
- New wish payload: `WishForm.vue` sends `user_uid`, `nickname`, `category`, `content`; the backend expects these fields and validates them.

## Code style & PR tips
- Keep changes minimal and focused: update only files relevant to the task.
- Follow existing patterns: backend route validation + commit pattern; frontend Tailwind + Pinia usage.
- Add brief comments for non-obvious fixes (eg. "workaround for missing FK cascade: deleting Like before Wish").

## Safety & gotchas (things an AI might mistakenly do)
- Do NOT assume migrations exist — editing `models.py` alone does not change production DB. Mention migration steps in PRs.
- Watch for optimistic frontend updates that are not rolled back on API failure.
- The repo uses mobile-first styling; avoid desktop-only layout changes unless you also add responsive rules.

---

If any section above looks incomplete or you want me to expand a specific part (example flows, more files, or a short checklist for making backend changes), tell me which area to expand and I will update this file.
