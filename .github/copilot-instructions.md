# Copilot instructions for the “我们的心愿墙” repo

Notes for AI coding agents. Keep concise, follow existing patterns automatically when you edit.

---

## Big picture
- Monorepo with Flask backend under [backend/](backend) and Vue 3 + Vite + Pinia + Tailwind + Vant frontend under [frontend/](frontend).
- REST API lives in [backend/app.py](backend/app.py); frontend calls `/api/*` via [frontend/src/api/index.js](frontend/src/api/index.js). MySQL persistence with SQLAlchemy models in [backend/models.py](backend/models.py).
- Mobile-first UI; layouts assume small screens. Keep Tailwind `sm`/`md` usage consistent.

## Key files
- Backend: [backend/app.py](backend/app.py) routes and validation; [backend/models.py](backend/models.py) models `Wish`, `Comment`, `Like`, `CommentLike`, `RateLimit`; [backend/config.py](backend/config.py) DB/env config and rate/AI flags; [backend/services/text_filter.py](backend/services/text_filter.py) content limits; [backend/services/ai_service.py](backend/services/ai_service.py) reply generation placeholder; [backend/init_db.py](backend/init_db.py) table bootstrap + demo data.
- Frontend: [frontend/src/App.vue](frontend/src/App.vue) first-visit identity modal; [frontend/src/stores/user.js](frontend/src/stores/user.js) localStorage identity (`id` is stable user_uid, color stored client-side); [frontend/src/components/WishForm.vue](frontend/src/components/WishForm.vue) posts wishes; [frontend/src/components/WishCard.vue](frontend/src/components/WishCard.vue) renders wishes, optimistic likes/comments/delete; [frontend/src/components/charts/ChartsBoard.vue](frontend/src/components/charts/ChartsBoard.vue) ECharts pie+wordcloud; [frontend/vite.config.js](frontend/vite.config.js) dev proxy to Flask.

## Backend patterns
- Routes validate required fields, short-circuit 400s, then commit inside try/except with rollback on error. Errors return JSON `{error: '...'}` and are logged via `app.logger.error`.
- Rate limit via [backend/app.py](backend/app.py#L32-L69) + [backend/models.py](backend/models.py#L99-L118); default 1 request per 5s for posting (configurable in [backend/config.py](backend/config.py)).
- AI reply: wish creation writes placeholder `ai_response` and spawns background thread to update later; keep response shape stable for polling in frontend.
- Deletion safety: wish delete clears `Like`, `CommentLike`, `Comment` rows manually before removing `Wish` to avoid FK issues (see [backend/app.py](backend/app.py#L184-L257)). No migration tooling—schema changes require updating models and rerunning [backend/init_db.py](backend/init_db.py) for dev; call out manual migration needs for prod.
- Content rules: valid categories are `红色传承/乡村建设/产业发展/生态环保`; wish content max length from `MAX_CONTENT_LENGTH` (500 by default); comment length capped at 200 in [backend/app.py](backend/app.py#L120-L172).

## Frontend patterns
- Identity: `userStore` generates/persists `user_info` in localStorage. Use `userInfo.id` as `user_uid` for API calls; name/color can change client-side.
- API usage centralized in [frontend/src/api/index.js](frontend/src/api/index.js) with axios instance (base `VITE_API_BASE_URL` or `http://localhost:5000`; Vite dev proxy handles `/api`). Add/change endpoints here first.
- Optimistic flows: likes/comments in [frontend/src/components/WishCard.vue](frontend/src/components/WishCard.vue) update local state and localStorage (`liked_wishes`, `liked_comments`) before API; include rollback or state sync on error messages like “已经点赞/还未点赞”.
- Wish form uses user store identity, attaches category/content, and normalizes returned wish fields; keep color enrichment client-side.
- Charts use static data fallback; wire real `/api/stats` data through [frontend/src/api/index.js](frontend/src/api/index.js) when needed.

## Run/debug
- Backend dev: `cd backend && pip install -r requirements.txt && python init_db.py && python app.py` (server on http://localhost:5000). Configure DB via env or [backend/config.py](backend/config.py); create DB `ourwish_wall` utf8mb4 first.
- Frontend dev: `cd frontend && npm install && npm run dev` (Vite on http://localhost:5173 with `/api` proxy). Build with `npm run build`.

## Integration notes
- MySQL via PyMySQL; DB URL from `DATABASE_URL` or discrete env vars in [backend/config.py](backend/config.py). Ensure utf8mb4.
- ECharts + echarts-wordcloud for charts; Vant 4 for mobile components.
- AI service flags in [backend/config.py](backend/config.py) (`AI_SERVICE_ENABLED`, `AI_MODEL` etc.); defaults to local mock.

## Safety/gotchas
- Do not assume cascade deletes on likes/comments—preserve manual cleanup logic or add relationships deliberately.
- Keep mobile-first spacing/typography; avoid desktop-only tweaks without `sm`/`md` guards.
- Respect content/category validation and rate limits when modifying payloads or UI flows.
- Mention lack of migration tooling when altering DB schema; prod needs manual migrations.

If anything here is unclear or you need more examples, ask to expand a section.
