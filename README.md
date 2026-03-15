# AIgument-backend

Tech stack: Python + FastAPI + Anthropic AI

## Setup

### 1. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
```
If you get "running scripts is disabled", do -

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

**macOS / Linux:**
```sh
cd backend
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```sh
pip install -r requirements.txt
```

### 3. Environment variables (`.env` in project root)

Add a `.env` file in the **project root** (parent of `backend/`) with:

```
ANTHROPIC_API_KEY=your-api-key-here
CORS_ORIGINS=http://localhost:3000
```

Optional: **CORS_ORIGINS** — Comma-separated allowed frontend origins (default: `http://localhost:3000`). For production, set e.g. `https://yourdomain.com`.

The app loads these via `python-dotenv`. Do not commit `.env`.

## Run

From the project root:

```sh
fastapi dev main.py
```