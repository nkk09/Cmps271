# AfterClass — Developer Setup Guide

This guide walks you through running the full AfterClass app locally from scratch. No prior experience assumed.

---

## What you'll need to install first

Before anything else, make sure the following are installed on your machine:

- **Python 3.11+** — [python.org/downloads](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/) (comes with `npm`)
- **PostgreSQL 14+** — [postgresql.org/download](https://www.postgresql.org/download/)
- **Git** — [git-scm.com](https://git-scm.com/)

To verify you have them, open a terminal and run:

```bash
python --version
node --version
psql --version
```

---

## Project structure

```
AfterClass/
├── backend/          ← FastAPI Python backend
│   ├── app/
│   ├── alembic/      ← database migration files
│   ├── .env.example  ← template for your environment variables
│   └── requirements.txt
└── frontend/         ← React/Vite frontend
    ├── src/
    └── package.json
```

---

## Step 1 — Set up the database

AfterClass uses **PostgreSQL**. You need to create a database before running the app.

Open a terminal and start the PostgreSQL shell:

```bash
psql -U postgres
```

Then create the database and a dedicated user (replace the password with something of your choice):

```sql
CREATE DATABASE afterclass;
CREATE USER afterclass_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE afterclass TO afterclass_user;
\q
```

Keep the database name, user, and password handy — you'll need them in the next step.

---

## Step 2 — Configure environment variables (backend)

Environment variables are settings that the backend reads at startup — things like database credentials, secret keys, and email config. You never commit these to Git.

1. Navigate to the `backend/` folder:

```bash
cd backend
```

2. Copy the example file to create your own `.env`:

```bash
# Mac / Linux
cp .env.example .env

# Windows
copy .env.example .env
```

3. Open `.env` in any text editor and fill in the values. Here's what each one means:

```env
# ── Database ──────────────────────────────────────────────────────────────
# Replace user, password, and database name with what you created in Step 1.
# Format: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
DATABASE_URL=postgresql+asyncpg://afterclass_user:yourpassword@localhost:5432/afterclass

# ── JWT (login tokens) ────────────────────────────────────────────────────
# A long random secret used to sign login tokens. Generate one with:
#   python -c "import secrets; print(secrets.token_hex(32))"
# Paste the output here.
JWT_SECRET=paste-a-long-random-string-here

# ── Session secret ────────────────────────────────────────────────────────
# Another random secret. Generate the same way as above.
SESSION_SECRET=paste-another-long-random-string-here

# ── Field encryption (protects emails stored in the database) ─────────────
# FIELD_ENCRYPTION_KEY must be exactly 32 random bytes, base64-encoded.
# Generate with:
#   python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"
FIELD_ENCRYPTION_KEY=paste-output-here

# FIELD_HMAC_KEY is a long random string (at least 32 characters).
# Generate with:
#   python -c "import secrets; print(secrets.token_hex(32))"
FIELD_HMAC_KEY=paste-output-here

# ── Email / OTP ───────────────────────────────────────────────────────────
# AfterClass sends OTP codes by email using Mailjet.
# Sign up free at https://app.mailjet.com → go to Account → API Keys.
SMTP_HOST=in-v3.mailjet.com
SMTP_PORT=587
SMTP_USER=your_mailjet_api_key
SMTP_PASS=your_mailjet_secret_key
SMTP_FROM=the_email_address_you_verified_in_mailjet

# ── OAuth (optional, leave blank unless you're using Microsoft Entra) ──────
ENTRA_TENANT_ID=
ENTRA_CLIENT_ID=
ENTRA_CLIENT_SECRET=
ENTRA_REDIRECT_URI=http://localhost:8000/auth/callback
ENTRA_AUTHORITY=

# ── Environment ───────────────────────────────────────────────────────────
# Keep this as "dev" while running locally.
ENV=dev
```

> **Tip:** To generate all your secret keys in one go, run these four commands in your terminal and paste each output into the matching variable:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"   # → JWT_SECRET
> python -c "import secrets; print(secrets.token_hex(32))"   # → SESSION_SECRET
> python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"  # → FIELD_ENCRYPTION_KEY
> python -c "import secrets; print(secrets.token_hex(32))"   # → FIELD_HMAC_KEY
> ```

---

## Step 3 — Set up the Python virtual environment

A virtual environment keeps the project's Python packages isolated from the rest of your system. You only do this once per machine.

Make sure you're in the `backend/` folder, then run:

```bash
# Create the virtual environment (creates a folder called "venv")
python -m venv venv

# Activate it
# Mac / Linux:
source venv/bin/activate

# Windows (Command Prompt):
venv\Scripts\activate.bat

# Windows (PowerShell):
venv\Scripts\Activate.ps1
```

Your terminal prompt should now show `(venv)` at the start — that means the virtual environment is active.

> Every time you open a new terminal to work on the backend, you need to activate the venv again with the `source venv/bin/activate` command.

---

## Step 4 — Install Python dependencies

With the venv active, install all required packages:

```bash
pip install -r requirements.txt
```

This reads `requirements.txt` and installs everything the backend needs. It may take a minute.

---

## Step 5 — Run database migrations

Alembic is the tool that creates (and updates) all the database tables for you. From the `backend/` folder with the venv active, run:

```bash
alembic upgrade head
```

This applies all migrations in order, creating every table the app needs. You should see output listing each migration as it runs.

If you ever pull new changes from Git that include new migrations, just run `alembic upgrade head` again to bring the database up to date.

---

## Step 6 — Start the backend server

Still in the `backend/` folder with the venv active:

```bash
uvicorn app.main:app --reload
```

- `--reload` means the server automatically restarts when you save a file — useful during development.
- The backend will be running at **http://localhost:8000**
- You can explore the auto-generated API docs at **http://localhost:8000/docs**

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

---

## Step 7 — Set up and start the frontend

Open a **new terminal window** (leave the backend running in the first one).

Navigate to the `frontend/` folder:

```bash
cd frontend
```

Install JavaScript dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will be running at **http://localhost:5173** — open that in your browser.

> The frontend already points to `http://localhost:8000` as the backend URL by default (see `src/api.js`). If your backend runs on a different port, create a `frontend/.env` file with:
> ```
> VITE_BACKEND_URL=http://localhost:YOUR_PORT
> ```

---

## Quick reference — daily workflow

Once set up, starting the app each day is just:

**Terminal 1 — backend:**
```bash
cd backend
source venv/bin/activate      # (Windows: venv\Scripts\activate.bat)
uvicorn app.main:app --reload
```

**Terminal 2 — frontend:**
```bash
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## Troubleshooting

**`ModuleNotFoundError` when starting the backend**
Make sure your virtual environment is activated — you should see `(venv)` in your terminal prompt. If not, run `source venv/bin/activate` from the `backend/` folder.

**`could not connect to server` (database error)**
Check that PostgreSQL is running. On Mac: `brew services start postgresql`. On Windows: open Services and start `postgresql-x64-XX`.

**`FIELD_ENCRYPTION_KEY is not set` error**
You haven't filled in all the required values in your `.env` file. Make sure `FIELD_ENCRYPTION_KEY` and `FIELD_HMAC_KEY` are both set.

**`alembic upgrade head` fails with a connection error**
Your `DATABASE_URL` in `.env` is incorrect. Double-check the username, password, host, and database name.

**Frontend shows a blank page or network errors**
Make sure the backend is running at `http://localhost:8000`. Check the browser's developer console (F12 → Console) for error messages.

**Port already in use**
Something else is using port 8000 or 5173. Either stop the other process, or start the servers on different ports:
```bash
uvicorn app.main:app --reload --port 8001
# and update VITE_BACKEND_URL in frontend/.env accordingly
```

---

## Useful URLs while running locally

| URL | What it is |
|-----|-----------|
| http://localhost:5173 | The app (frontend) |
| http://localhost:8000/docs | Interactive API documentation (Swagger UI) |
| http://localhost:8000/redoc | Alternative API docs (ReDoc) |
| http://localhost:8000/health | Quick check that the backend is alive |

---

## Microsoft Entra ID setup (primary login method)

AfterClass uses Microsoft Entra ID (formerly Azure AD) for authentication. Here's how to register the app.

### 1 — Register the app in Azure Portal

1. Go to [portal.azure.com](https://portal.azure.com) and sign in with an account that has access to your AUB tenant.
2. Search for **"App registrations"** → click **New registration**.
3. Fill in:
   - **Name:** `AfterClass` (or anything you like)
   - **Supported account types:** *Accounts in this organizational directory only* (your AUB tenant)
   - **Redirect URI:** choose **Web**, enter `http://localhost:8000/api/v1/auth/callback`
4. Click **Register**.

### 2 — Collect your credentials

On the app's overview page, copy:
- **Application (client) ID** → this is your `ENTRA_CLIENT_ID`
- **Directory (tenant) ID** → this is your `ENTRA_TENANT_ID`

Then create a client secret:
1. Left sidebar → **Certificates & secrets** → **New client secret**
2. Set an expiry → click **Add**
3. Copy the **Value** immediately (it won't be shown again) → this is your `ENTRA_CLIENT_SECRET`

### 3 — Fill in your `.env`

```env
ENTRA_TENANT_ID=paste-your-tenant-id
ENTRA_CLIENT_ID=paste-your-client-id
ENTRA_CLIENT_SECRET=paste-your-client-secret
ENTRA_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback
ENABLE_OAUTH=true
FRONTEND_URL=http://localhost:5173
```

### 4 — Tell the frontend to show the Microsoft button

Create `frontend/.env` (next to `package.json`):

```env
VITE_ENABLE_OAUTH=true
VITE_BACKEND_URL=http://localhost:8000
```

### 5 — Restart both servers

The login page will now show a **Sign in with Microsoft** button instead of the OTP form.

### How the login flow works

```
User clicks "Sign in with Microsoft"
  → Frontend calls GET /api/v1/auth/login
  → Backend generates PKCE challenge + state, redirects to Microsoft
  → User logs in on Microsoft's page
  → Microsoft redirects to GET /api/v1/auth/callback?code=...&state=...
  → Backend validates state, exchanges code for ID token
  → Backend creates/finds the user, issues a JWT
  → Backend redirects to http://localhost:5173/auth/callback?token=<jwt>
  → Frontend stores the token, cleans the URL, loads the app
```

Role is determined automatically from the email domain:
- `@mail.aub.edu` → **student**
- `@aub.edu.lb` → **professor**
- Any other domain → rejected with 403