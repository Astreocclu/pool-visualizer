# CLAUDE.md - Project Rules for Claude Code

> **Server Info:** User connects from host PC to server `testhome` (192.168.1.254) as user `astre`

---

## Project Overview
**testhome-visualizer** - Multi-tenant AI visualization app for home improvement products.

| Service | Port |
|---------|------|
| Backend (Django) | 8000 |
| Frontend (React) | 3000 |
| Database | PostgreSQL (contractors_dev) |

### Active Tenants
- **pools** - Pool enclosure visualizations (default)
- **screens** - Security screen visualizations
- **windows** - Window replacement visualizations
- **roofs** - Roofing visualizations

## Working Style
- When I share a problem, analyze it first and wait for my reply before making changes
- Break large tasks into 3-5 subtasks and confirm the plan before starting
- Ask clarifying questions if requirements are ambiguous
- One feature at a time, fully complete before moving on

## Git Workflow
- Run `git status` and show me the output before any git operations
- Suggest commits but wait for my approval before running them
- Draft PR descriptions but I will create the PR
- Tell me when to commit, don't do it automatically
- Always work on feature branches, never commit directly to master
- One branch per feature (they already exist, use them)

### Branch Structure
```
master (stable)
├── screen-visualizer
├── feature/price-quote
├── feature/pdf-generator
├── feature/audit
├── feature/payments
└── feature/monday-integration
```

## Session Start
1. Read PLAN.md, TODO.md, and SESSION-NOTES.md
2. Check `git status` and `git branch`
3. Tell me where we left off (reference SESSION-NOTES.md)
4. Ask what I want to focus on today
5. Update SESSION-NOTES.md with today's date and branch

## During Session
**Log as you go** - Update SESSION-NOTES.md incrementally:
- After completing a significant task, add it to "What We Did"
- When something breaks, immediately note it in "What's Broken / Blocked"
- When you discover something important, document it
- Don't wait until end of session to update notes

## Session End
1. Remind me to commit if there are uncommitted changes
2. Update TODO.md with progress
3. Finalize SESSION-NOTES.md:
   - Complete "What We Did" list
   - Update "What's Working" / "What's Broken"
   - Fill in "Next Session Should"
   - Move to "Previous Sessions" if starting fresh next time
4. Tell me the next logical task

## Commands

### Backend (Django)
```bash
source venv/bin/activate
python3 manage.py runserver 8000   # dev server on port 8000
python3 manage.py test             # run tests
python3 manage.py makemigrations   # create migrations
python3 manage.py migrate          # apply migrations
celery -A config worker -l info    # celery worker
```

### Frontend (React)
```bash
cd frontend
npm start        # dev server on port 3000
npm run build    # production build
npm run test     # run tests
```

## Code Style

### Python/Django
- Use type hints
- Docstrings for public functions
- Keep views thin, logic in services
- Use Django REST Framework serializers

### React
- Functional components with hooks
- Zustand for global state
- Keep components small and focused
- Use Lucide icons (already installed)

## Tech Stack Reference
- **Backend:** Django 4.0, DRF, PostgreSQL, Redis, Celery
- **Frontend:** React 19.1, React Router 7, Zustand
- **AI:** Google Gemini via google-generativeai
- **PDF:** ReportLab
- **Payments:** Stripe
- **Storage:** AWS S3

## Project-Specific Notes
- Multi-tenant AI visualization platform for home improvement products
- Each tenant has its own config (product options) and prompts (AI instructions)
- Tenant configs are in `api/tenants/{tenant_name}/`
- Reference Image System allows contractors to upload product photos for AI compositing
- AI pipeline: Cleanup → Feature Insertion → Quality Check
- Uses Google Gemini Nano Banana Pro for image editing

---

## Troubleshooting

### White Screen During Image Generation (Fixed 2026-01-08)

**Symptoms:** After submitting the visualization form, users see a blank white screen instead of the ProcessingScreen animation. Affects all browsers, multiple users.

**Root Cause:** In `frontend/src/pages/ResultDetailPage.js`, the `fetchRequestDetails` function had a `finally` block that ALWAYS set `isLoading(false)` regardless of whether the fetch succeeded or failed. This caused a race condition:

1. User submits form, navigates to `/results/{id}`
2. `ResultDetailPage` mounts with `isLoading=true`, `request=null`
3. First render shows skeleton (correct)
4. If first API fetch fails (network hiccup, etc.):
   - `request` stays `null`
   - `error` stays `null` (only set after 3 consecutive failures)
   - `isLoading` becomes `false` (from finally block)
5. Second render: `isLoading && !request` = `false`, no error page, `!request` guard returns `null` → **WHITE SCREEN**

**Fix:**
1. Removed the `finally` block that unconditionally set `isLoading(false)`
2. Now `setIsLoading(false)` only happens when:
   - Successfully fetched request data (in try block)
   - After 3 consecutive failures with error message (in catch block)
3. Changed the null guard from `return null` to render a skeleton as fallback

**Files Changed:** `frontend/src/pages/ResultDetailPage.js`

**After Fixing:**
```bash
cd frontend && npm run build
sudo systemctl restart testhome-visualizer.service
```
