# AI Marketplace — Full Project (Auth + Model Upload/Approval)

Single Flask project. SQLite database, session auth (Flask-Login), and a
creator-upload -> admin-approval -> marketplace pipeline for AI models.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

First run automatically:
- Creates `marketplace.db` and all tables (`users`, `models`)
- Seeds one admin account (see below)
- Creates `static/uploads/models/` for logo uploads

Open **http://127.0.0.1:5000**

## Admin credentials (temporary, seeded on first run)

```
Email:    admin@marketplace.com
Password: Admin@123
```

## What's inside

```
app.py                  - entry point, config, blueprint registration, admin seeding
extensions.py            - shared db / login_manager
models.py                - User table + Model table (creator uploads)
decorators.py            - role_required() - backend-enforced role access
auth.py                  - registration/login/logout for all 3 roles, dashboards
model_data.py            - PREDEFINED static demo models (never touched by uploads)
marketplace_service.py   - combines model_data.py + APPROVED db models into one list
model_routes.py          - upload form, admin review/approve/reject, model details page

templates/
  base_auth.html, role_select.html          - shared auth layout + landing page
  user_register/login.html                  - user auth
  creator_register/login.html                - creator auth
  admin_login.html                           - no admin_register.html - by design
  home.html                                  - THE marketplace page (also used for
                                                the creator's dashboard, with 2 extra
                                                sections shown only when is_creator=True)
  creator_upload.html                        - "Upload New AI Model" form
  admin_dashboard.html                        - pending approvals list
  admin_model_view.html                       - full review page (Approve/Reject)
  model_details.html                          - what a user sees clicking a card

static/css/home.css, auth.css, shared.css    - one shared color system across every page
static/js/home.js                            - client-side search filter only
static/uploads/models/                       - creator-uploaded logos land here
```

## How the pieces connect

- **User logs in** → `/user/dashboard` → renders `home.html` with
  `get_marketplace_models()` (static + approved db models combined).
- **Creator logs in** → `/creator/dashboard` → renders the SAME `home.html`,
  plus an "Upload New AI Model" button and a table of their own models
  with status (Pending/Approved/Rejected).
- **Creator uploads** → `/creator/upload` → validates input, saves the logo
  to `static/uploads/models/` with a random safe filename, inserts a `Model`
  row with `status="PENDING"`, redirects back to the creator dashboard.
- **Admin logs in** → `/admin/dashboard` → sees all PENDING models, can
  View / Approve / Reject each one.
- **Approve** flips `status` to `APPROVED` → it now shows up automatically
  next time anyone loads the marketplace (no extra step needed).
- **Anyone clicks a card** → `/model/<id>` → `model_details.html`, showing
  full model info + a Creator Profile block underneath.

Static and database models use the SAME card markup and the SAME details
template — the id is just prefixed (`static-1` vs `db-7`) so the app knows
which source to query, but visually there's no difference.

## Testing the full flow

1. Register a creator at `/register/creator`, log in.
2. Click "Upload New AI Model", submit a model → see it listed as **PENDING**
   in "Your Uploaded Models" on your own dashboard.
3. Log in as admin (`/login/admin`) → see it under "Pending Model Approvals".
4. Click **Approve**.
5. Register/log in as a normal user → the model now appears in the marketplace grid.
6. Click it → full details page + creator profile at the bottom.
7. Restart `python app.py` → the model is still there (SQLite persists to disk).

## Notes / honesty about scope

- This project has **no recommendation engine** — none existed before this
  task, so none was built or modified. `model_data.py` keeps `price_tier`,
  `technical_level`, `quality`, `speed` fields for future compatibility if
  you build one later.
- No image is stored in the database — only the filename, per the spec.
- Rejected models are kept in the database (not deleted) so creators can see their status.
