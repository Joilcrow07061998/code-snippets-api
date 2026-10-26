# Code Snippets API

A small API for saving code and sharing it by a UUID link. Built with FastAPI, async SQLAlchemy, PostgreSQL and JWT.

## What it does

- register with an email and password
- log in and receive a JWT access token
- create, list, edit and delete your snippets
- share a snippet with a link that works without login
- keep edits and deletes limited to the owner
- validate input, log useful events and return a generic response for unexpected errors

## Run locally

You need Python 3.11+ and Docker.

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies and prepare the environment:

   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   ```

   Set `SECRET_KEY` in `.env` to a long random value before using the app outside local development.

3. Start PostgreSQL and apply the migration:

   ```bash
   docker compose up -d db
   alembic upgrade head
   ```

4. Start the API:

   ```bash
   uvicorn main:app --reload
   ```

Open `http://127.0.0.1:8000/docs` to try the endpoints. The database connection string in `.env.example` matches the included Docker Compose service.

## Main endpoints

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `POST` | `/api/v1/auth/register` | no | Create an account |
| `POST` | `/api/v1/auth/token` | no | Get a JWT token (form fields: `username` = email, `password`) |
| `POST` | `/api/v1/snippets` | yes | Create a snippet |
| `GET` | `/api/v1/snippets` | yes | List your snippets |
| `GET` | `/api/v1/snippets/shared/{share_id}` | no | Read a shared snippet |
| `PATCH` | `/api/v1/snippets/{id}` | yes, owner only | Edit a snippet |
| `DELETE` | `/api/v1/snippets/{id}` | yes, owner only | Delete a snippet |
| `GET` | `/health` | no | Health check |

For protected endpoints, click **Authorize** in Swagger and enter the access token. The shared URL is the `/api/v1/snippets/shared/{share_id}` path with the UUID returned when a snippet is created.

## Tests

Tests use an in-memory SQLite database, so PostgreSQL does not need to be running:

```bash
pytest
```

## Project layout

- `src/api` — routes and authentication dependencies
- `src/core` — settings, password/JWT helpers, logging and error handling
- `src/db` — async SQLAlchemy engine and base model
- `src/models` — database models
- `src/schemas` — request and response validation
- `src/services` — place for business logic as the project grows
- `alembic` — database migrations
- `tests` — API tests
