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
.github/
  copilot-instructions.md              ← Symlink to CLAUDE.md (Copilot auto-reads this)
  prompts/
    backend.prompt.md                  ← Backend guidance (attach in Copilot Chat)
    frontend.prompt.md                 ← Frontend guidance (attach in Copilot Chat)
```

---

## Claude Code Agents

Claude Code automatically picks up agents from `.claude/agents/`. It selects the right agent based on the task description — no manual invocation needed.

| Agent | File | Activates for |
|-------|------|--------------|
| Backend Specialist | `.claude/agents/backend.md` | `backend/src/`, `backend/prisma/` |
| Frontend Specialist | `.claude/agents/frontend.md` | `frontend/src/` |

**Verify agents are loaded**: run `/agents` in Claude Code.

### What each agent handles

**Backend Specialist** (`backend.md`):
- Express route creation & middleware
- Prisma ORM queries & database interactions
- Zod input validation & sanitization
- JWT authentication & authorization guards
- Error handling & HTTP status codes
- N+1 query prevention
- Chat/embeddings & semantic search patterns

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

Copilot automatically reads `.github/copilot-instructions.md` (symlinked to `CLAUDE.md`) for project-wide context.

For specialist guidance, attach prompt files manually in Copilot Chat:

```
#file:.github/prompts/backend.prompt.md  → Backend expertise
#file:.github/prompts/frontend.prompt.md → Frontend expertise
```

---

## Creating the Copilot Symlink (if you ever need to recreate it)

```bash
# Run from the project root
ln -s ../CLAUDE.md .github/copilot-instructions.md
```

The target path (`../CLAUDE.md`) is relative to where the link lives (`.github/`), not to where you run the command.

---

## Keeping Instructions Updated

All instructions live in three places. Here's what to update when:

| Change | Update |
|--------|--------|
| New project-wide convention | `CLAUDE.md` (Copilot picks it up via symlink) |
| New backend pattern/red flag | `.claude/agents/backend.md` + `.github/prompts/backend.prompt.md` |
| New frontend pattern/red flag | `.claude/agents/frontend.md` + `.github/prompts/frontend.prompt.md` |

---

## Reference Files

- `backend/src/middleware/auth.js` — JWT verification & guards
- `backend/src/validation/product.js` — Zod schemas
- `backend/prisma/schema.prisma` — Database models & indexes
- `backend/src/routes/admin.js` — Protected endpoint patterns
- `backend/src/routes/catalog.js` — Public endpoint patterns
- `frontend/src/stores/auth.js` — Auth state management
- `frontend/src/api/client.js` — API client & axios config
- `frontend/src/router.js` — Routes & auth guards
- `frontend/src/components/ProductCard.vue` — Component example
