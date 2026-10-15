# Wardrobe Catalog - AI Coding Agents

This project includes specialized AI agents for Claude Code and prompt files for GitHub Copilot. Each is tailored to a specific part of the codebase.

---

## File Layout

```
CLAUDE.md                              ← Project-wide instructions (Claude Code + Copilot)
.claude/
  agents/
    backend.md                         ← Backend Specialist (Claude Code sub-agent)
    frontend.md                        ← Frontend Specialist (Claude Code sub-agent)
  commands/
    review.md                          ← /review slash command
.github/
  copilot-instructions.md              ← Optional symlink to CLAUDE.md (see below)
  agents/
    backend.agent.md                   ← Backend specialist (Copilot custom agent)
    frontend.agent.md                  ← Frontend specialist (Copilot custom agent)
  instructions/
    backend.instructions.md            ← Auto-applied to backend/**/*.py
    frontend.instructions.md           ← Auto-applied to frontend code
  skills/
    add-api-route/                     ← New FastAPI endpoint
    add-pydantic-schema/               ← New request/response schema
    alembic-migration/                 ← Model change + migration
    add-vue-component/                 ← New Vue component
    code-review/                       ← Review checklist
```

---

## Claude Code Agents

Claude Code automatically picks up agents from `.claude/agents/`. It selects the right agent based on the task description — no manual invocation needed.

| Agent | File | Activates for |
|-------|------|--------------|
| Backend Specialist | `.claude/agents/backend.md` | `backend/app/`, `backend/alembic/`, `backend/tests/` |
| Frontend Specialist | `.claude/agents/frontend.md` | `frontend/src/` |

**Verify agents are loaded**: run `/agents` in Claude Code.

### What each agent handles

**Backend Specialist** (`backend.md`):
- FastAPI routers & auth dependencies
- SQLAlchemy 2.0 async queries & eager loading
- Pydantic input/output schemas
- Alembic migrations
- JWT authentication & authorization
- Error handling & HTTP status codes
- N+1 query prevention
- Chat/embeddings & semantic search patterns
- Backend Dockerfile / compose service

**Frontend Specialist** (`frontend.md`):
- Vue 3 Composition API components
- Pinia store design & state management
- Vue Router routes & auth guards
- Axios API client patterns
- Tailwind CSS styling & responsive design
- Error handling & loading states
- Authentication/authorization in views

---

## GitHub Copilot

Copilot reads `.github/copilot-instructions.md` for project-wide context (create the symlink below so it mirrors `CLAUDE.md`).

- **Path-scoped rules**: `.github/instructions/*.instructions.md` apply automatically via their `applyTo` globs
- **Custom agents**: pick `backend-specialist` / `frontend-specialist` from `.github/agents/`
- **Skills**: `.github/skills/*/SKILL.md` are loaded when the task matches their description

---

## Creating the Copilot Symlink (if you ever need to recreate it)

```bash
# Run from the project root
ln -s ../CLAUDE.md .github/copilot-instructions.md
```

The target path (`../CLAUDE.md`) is relative to where the link lives (`.github/`), not to where you run the command.

---

## Keeping Instructions Updated

Instructions live in a few places. Here's what to update when:

| Change | Update |
|--------|--------|
| New project-wide convention | `CLAUDE.md` (Copilot picks it up via symlink) |
| New backend pattern/red flag | `.claude/agents/backend.md` + `.github/agents/backend.agent.md` + `.github/instructions/backend.instructions.md` |
| New frontend pattern/red flag | `.claude/agents/frontend.md` + `.github/agents/frontend.agent.md` + `.github/instructions/frontend.instructions.md` |
| New repeatable workflow | `.github/skills/<name>/SKILL.md` |

---

## Reference Files

- `backend/app/security.py` — JWT, bcrypt, `require_auth` / `require_admin`
- `backend/app/schemas.py` — Pydantic schemas
- `backend/app/models.py` — SQLAlchemy models & indexes
- `backend/alembic/versions/` — Migrations
- `backend/app/routers/admin.py` — Protected endpoint patterns
- `backend/app/routers/catalog.py` — Public endpoint patterns
- `docker-compose.yml` — Local stack (db, backend, frontend)
- `frontend/src/stores/auth.js` — Auth state management
- `frontend/src/api/client.js` — API client & axios config
- `frontend/src/router.js` — Routes & auth guards
- `frontend/src/components/ProductCard.vue` — Component example
