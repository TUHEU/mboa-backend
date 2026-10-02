# Nyetam FastAPI backend

The first backend slice provides secure tourist registration, login, JWT access tokens, role-ready users, the authenticated current-user endpoint, and an authenticated driving-route endpoint (`POST /api/v1/routes/compute`, Bearer token required).

Google Sign-In is supported through `POST /api/v1/auth/google`. The API verifies Google ID-token signature, issuer, audience, expiry, and verified email before issuing a Nyetam JWT.

## Local setup

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.venv\Scripts\python -m uvicorn app.main:app --reload
```

Run these commands from the `backend` directory. Swagger documentation is available at `http://127.0.0.1:8000/docs`.

## Database

Local development defaults to SQLite. For production geospatial support, set `DATABASE_URL` to a PostgreSQL database with PostGIS enabled, for example:

```text
postgresql+psycopg://user:password@host:5432/nyetam
```

Schema migrations should be introduced with Alembic before production deployment.

## Google OAuth

Create a Web OAuth client in Google Cloud Console and set its client ID in `.env`:

```text
GOOGLE_CLIENT_ID=your-web-client-id.apps.googleusercontent.com
```

The backend audience must match the `GOOGLE_SERVER_CLIENT_ID` used by the Flutter Android/iOS builds and the `GOOGLE_CLIENT_ID` used by Flutter web.