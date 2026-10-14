# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite web app based on the supplied project documentation. It generates a structured 7-day fitness plan, a nutrition/recovery tip, and can revise the plan from user feedback.

## Architecture

- **Frontend:** HTML + Jinja2 + responsive CSS
- **Backend:** FastAPI
- **AI:** Google GenAI Python SDK (`google-genai`)
- **Workout/update model:** `GEMINI_PRO_MODEL` (default `gemini-2.5-pro`)
- **Nutrition model:** `GEMINI_FLASH_MODEL` (default `gemini-2.5-flash`)
- **Database:** SQLite + SQLAlchemy
- **Validation:** Pydantic
- **Admin:** Session-protected dashboard

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── schemas.py
│   ├── ai_models.py
│   ├── gemini_client.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   ├── updated_plan.py
│   └── routes.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── admin_login.html
│   └── all_users.html
├── static/css/style.css
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Windows / VS Code setup

1. Install Python 3.11+.
2. Open this folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

```powershell
py -m venv .venv
```

5. Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```cmd
.venv\Scripts\activate
```

6. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

7. Copy `.env.example` to `.env`.

For a first test, leave:

```env
DEMO_MODE=true
```

This allows the entire application to run without an API key.

For real Gemini generation, set:

```env
GEMINI_API_KEY=your_real_key
DEMO_MODE=false
```

8. Start the server:

```powershell
uvicorn app.main:app --reload
```

9. Open:

- App: http://127.0.0.1:8000
- Swagger API docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Admin login: http://127.0.0.1:8000/admin/login

## Admin

The default development credentials come from `.env`:

```text
Username: admin
Password: fitbuddy-admin
```

Change them before deployment.

## API examples

### Generate a plan

POST `/api/generate-workout`

```json
{
  "username": "Alex",
  "user_id": "alex01",
  "age": 21,
  "weight": 70,
  "goal": "muscle gain",
  "intensity": "medium"
}
```

### Get a saved plan

GET `/api/users/alex01`

### Submit feedback

POST `/api/submit-feedback`

```json
{
  "user_id": "alex01",
  "feedback": "Add more cardio and keep two recovery days."
}
```

## Testing

Run:

```powershell
pytest
```

The repository includes basic endpoint/database tests. Demo mode keeps tests independent of the Gemini service.

## Gemini model note

The supplied documentation names Gemini 1.5 Pro and Gemini Flash and uses the older `google-generativeai` package. This implementation uses Google's current `google-genai` SDK and configurable model IDs. The defaults are `gemini-2.5-pro` for plan generation/update and `gemini-2.5-flash` for quick nutrition/recovery tips.

## Safety

FitBuddy is a general wellness application, not a medical service. The prompts explicitly avoid diagnosis/treatment and advise users with medical conditions, injuries, pregnancy, or exercise restrictions to consult an appropriate healthcare professional.
