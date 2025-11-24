# Copilot Instructions for easy_automate

## Project Overview
- **Purpose:** Backend for web automation, built with Python, Flask, and Selenium. Exposes a REST API to manage web applications, pages, and browser sessions.
- **Key Technologies:** Flask, Flask-SQLAlchemy, Selenium, Docker (for containerized browser and app), Alembic (migrations).

## Architecture & Key Components
- `src/blueprints/`: Contains Flask blueprints for API endpoints:
  - `applications.py`: CRUD for web applications
  - `pages.py`: CRUD for pages within applications
  - `browser.py`: Browser session control (open, close, navigate, screenshot, DOM)
- node_red_node: Custom Node-RED nodes for interacting with the API
- `src/models.py`: SQLAlchemy models for applications and pages
- `src/browser_manager.py` & `src/browser_actions.py`: Selenium browser orchestration and actions
- `migrations/`: Alembic migration scripts for database schema
- `wsgi.py`: Flask app entry point

## Developer Workflows
- **Install dependencies:** `pip install -r requirements.txt`
- **Run with Docker:** `docker compose up --build -d` (recommended for stable environment)
- **Run locally:**
  1. Create `.env` (see README)
  2. Initialize DB: `flask db init` (first time), then `flask db migrate` and `flask db upgrade` as needed
  3. Start app: `flask run`
- **Testing:**
  - Tests are in `tests/` (e.g., `test_applications.py`, `test_browser.py`, `test_pages.py`)
  - Use `pytest` to run tests: `pytest tests/`
- **Migrations:**
  - Alembic config in `migrations/` and `alembic.ini`
  - Usual commands: `flask db migrate`, `flask db upgrade`

## Project-Specific Patterns & Conventions
- **Blueprints:** All API endpoints are organized as Flask blueprints in `src/blueprints/`.
- **Browser Management:**
  - Supports both local and remote (Dockerized) Selenium via `SELENIUM_MODE` in `.env`.
  - Interactive mode (`INTERACTIVE_MODE=True`) shows browser UI for debugging.
- **Database:**
  - Models are defined in `src/models.py`.
  - Alembic handles migrations; do not edit migration scripts manually.
- **API Usage:**
  - Main endpoints: `/applications`, `/pages`, `/browser` (see README for details)

## Integration Points
- **Selenium:** Controlled via `src/browser_manager.py` and `src/browser_actions.py`.
- **Docker Compose:** Orchestrates Flask app and Selenium Hub for remote browser sessions.
- **Environment Variables:** `.env` file configures Flask and Selenium modes.

## Examples
- To open a browser session via API: `POST /browser/open` (optionally with `{ "timeout": 30 }`)
- To get a screenshot: `GET /browser/<session_id>/screenshot`

---

**For AI agents:**
- Prefer using/adding blueprints for new API endpoints.
- Follow existing patterns in `src/blueprints/` and `src/models.py` for new features.
- Update migrations via Alembic CLI, not by hand.
- Reference the README for setup and workflow details.
