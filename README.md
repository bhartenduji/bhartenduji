# QUIZ_CREATOR by YOUR_ORG

A focused API-only tool to create, validate, search, version, import/export, and assemble quizzes.

## Tech Stack
- Python 3.11+
- FastAPI + Pydantic
- Uvicorn (dev server)
- SQLite via SQLAlchemy
- API-only (no Jinja UI). Printable HTML export for quizzes is provided.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open API docs: `http://localhost:8000/docs`

## Project Structure
```
app/
  main.py
  db.py
  models.py
  schemas.py
  services/
    validation.py
    versioning.py
    assembly.py
    import_export.py
    assist.py
  routers/
    questions.py
    quizzes.py
    import_export.py
    assist.py
sample_data/
  sample_questions.csv
  sample_questions.json
.vscode/
  launch.json
  tasks.json
```

## Environment
- SQLite database file: `./quiz_creator.db`

## VS Code: Run/Debug
- Use the preconfigured `tasks` to install dependencies
- Launch with the `Run Uvicorn (Reload)` launch config

## API Sketch
- POST /api/questions
- GET /api/questions/{id}
- PUT /api/questions/{id}
- DELETE /api/questions/{id}
- GET /api/questions (filters: query, type, tags, difficultyMin, difficultyMax, subject, bloomLevel, page, size)
- POST /api/questions/import (CSV/JSON)
- GET /api/questions/export?format=csv|json
- GET /api/questions/{id}/versions
- POST /api/questions/{id}/restore?version=
- POST /api/quizzes
- GET /api/quizzes/{id}
- POST /api/quizzes/{id}/generate
- GET /api/quizzes/{id}/export?format=html|json
- POST /api/assist/diagnose

## Testing
```bash
pytest -q
```

## Notes
- API returns robust validation errors (HTTP 400 with details)
- Versioning is automatic on update
- Quiz assembly supports rules (types, difficulty distribution, tag/subject filters, shuffle)
