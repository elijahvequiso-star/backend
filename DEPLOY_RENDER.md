# Render Deployment Guide

This backend is set up to deploy as a Python web service on Render.

## Project Layout

- Repo root: `vequiso_build_hub_backend`
- Django service root: `title`
- WSGI app: `title.wsgi:application`

## Required Render Settings

If you create the service manually in the dashboard, use:

- Runtime: `Python 3`
- Root Directory: `title`
- Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- Pre-Deploy Command: `python manage.py migrate --noinput`
- Start Command: `gunicorn title.wsgi:application`
- Health Check Path: `/health/`

If you use Blueprint deploys, Render reads these settings from `render.yaml`.
The included blueprint also creates a Render Postgres database and injects its connection string into `DATABASE_URL`.

## Required Environment Variables

Set these in Render:

- `PYTHON_VERSION=3.12.10`
- `DJANGO_SETTINGS_MODULE=title.settings`
- `DEBUG=false`
- `USE_POSTGRES=true`
- `DATABASE_URL=<your Render Postgres internal database URL>`
- `SECRET_KEY=<long random secret>`
- `ALLOWED_HOSTS=.onrender.com`

Optional:

- `CORS_ALLOW_ALL_ORIGINS=false`
- `CORS_ALLOWED_ORIGINS=https://your-frontend-domain.onrender.com`
- `CSRF_TRUSTED_ORIGINS=https://your-backend-name.onrender.com,https://your-frontend-domain.onrender.com`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`

## Database Choice

For Render deployment, use PostgreSQL.

This project supports:

- PostgreSQL in production through `DATABASE_URL`
- MySQL locally through the existing `DB_*` environment variables

## First Deploy Checklist

1. Push this backend repo to GitHub.
2. Either deploy with `render.yaml`, or manually create a new PostgreSQL database and a new Web Service.
3. Create a new Web Service from the backend repo if you are not using Blueprint deploy.
4. Make sure the service uses the Python runtime.
5. Set `Root Directory` to `title` if you are not using Blueprint deploy.
6. Add the required environment variables.
7. Deploy.

## Common Failures

### `requirements.txt` not found

Render is building the repo root instead of the `title` directory.

Fix:

- Set `Root Directory` to `title`
- Or deploy with the included `render.yaml`

### `pg_config executable not found`

This usually happens when `psycopg2` or an unsupported Python version triggers a source build.

Fix:

- Use Python `3.12.10`
- Use the provided `psycopg[binary]` dependency

### `Could not find a version that satisfies the requirement jazzmin`

The correct package name is `django-jazzmin`, not `jazzmin`.

### DNS / network failures during `pip install`

If logs show errors like `getaddrinfo failed`, the machine could not resolve package hostnames.

## Health Endpoint

The service exposes:

- `/health/`
