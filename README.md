# SynCreator

A condition simulator for Splunk Synthetic Monitoring. Create test scenarios (errors, delays, security issues) and point your synthetic tests at them.

## Quick Start

```bash
git clone https://github.com/rcastley/SynCreator
cd SynCreator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:8080 and register a new account.

The database is created automatically on first run.

## Production

```bash
# Using waitress (recommended)
waitress-serve --port=8080 --call flaskr:create_app

# Or with Docker
docker compose up -d
```

Set `SECRET_KEY` environment variable in production:

```bash
export SECRET_KEY="your-secret-key-here"
```

## API Endpoints

Once logged in, you get a unique URL for synthetic testing:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/view/{username}` | GET | Your test page (shows current condition) |
| `/api/v1/{username}/books/all` | GET | Returns all books |
| `/api/v1/{username}/books?id=0` | GET | Returns book by ID (0-2) |
| `/api/v1/{username}/books` | POST | Create book (mock - not persisted) |

## Available Conditions

- **Default** - Normal page
- **404/500 Error** - HTTP error responses
- **Content Delay** - 5 second delay
- **Timeout** - 62 second delay
- **Large/Hero Image** - Slow assets
- **Security tests** - JS injection, e-skimmer, defacement
