# bu-search

Django-based search engine proof of concept with real-time results using HTMX.

## Overview
bu-search is a lightweight Django project designed as a proof of concept for a search engine. It features a simple, responsive front-end with real-time search functionality powered by HTMX and a PostgreSQL backend. The project is containerized with Docker for easy setup and deployment.

## Features
- Real-time search with HTMX for dynamic, no-refresh updates.
- Bootstrap 5 for a clean, responsive UI.
- PostgreSQL database integration.
- Daphne ASGI server for async capabilities.
- Pre-commit hooks for code quality (Black, isort, autoflake).
- Dockerized setup with `docker-compose` for development.

## Setup
1. Clone the repository:
   ```bash
   git clone gh/gcca/bu-search.git
   cd bu-search
   ```

2. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Access the app at `http://localhost:8000/poc/search/`.

## Usage
- Enter a search query in the input field.
- Results update in real-time below the input (currently echoes query + page number after a 1-second delay).

## Project Structure
- `bu_search/`: Core Django project files (settings, URLs, ASGI/WSGI).
- `bum_poc/`: Search app with views, URLs, and templates.
- `Dockerfile`: Python 3.13-slim base, installs dependencies, runs Daphne.
- `docker-compose.yml`: Configures web (port 8000) and db (PostgreSQL) services.
- `.env`: Environment variables (DEBUG, DATABASE_URL).
- `.pre-commit-config.yaml`: Linting/formatting hooks.

## Development
- Install dev dependencies:
  ```bash
  pip install -r requirements-dev.txt
  ```
- Run pre-commit:
  ```bash
  pre-commit install
  pre-commit run --all-files
  ```

## Notes
- Debug mode is enabled by default (`DEBUG=True` in `.env`).
- Static files are managed by Whitenoise.
- CSRF trusted origins configured for `*.gcca.dev`.
- Extend `bum_poc/views.py` and `models.py` for full search functionality.

## License
This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See the [LICENSE](LICENSE) file for details.
