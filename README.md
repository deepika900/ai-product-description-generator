# AI-Powered Product Description Generator

Generates SEO-friendly fashion product descriptions from a few inputs (name, category, features, keywords, tone) using the OpenAI API. Flask REST backend, React frontend.

## Tech stack
- **Backend:** Python, Flask, Flask-CORS, OpenAI Python SDK
- **Frontend:** React 18, Vite
- **Tests:** pytest (OpenAI is mocked, so tests run offline and free)

## How it works
1. The React form sends product details to `POST /api/generate`.
2. Flask validates the input and asks the model for a JSON reply (title, ~60-90 word description, bullet points).
3. The system prompt tells the model to use only the facts supplied, so it doesn't invent materials or claims.
4. The response includes `elapsed_ms`, so you can measure real generation time.

## API
| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/health` | Health check |
| POST | `/api/generate` | Body: `name` (required), `category`, `features`, `keywords`, `tone` (`professional`, `playful`, `luxury`, `casual`) |

## Getting started
Requires Python 3.10+, Node 18+ and an OpenAI API key.

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add your OPENAI_API_KEY
python app.py               # http://localhost:5001

# Frontend (new terminal)
cd client
npm install
npm run dev                 # http://localhost:5173
```

## Tests
```bash
cd backend && pytest
```

## Notes
- Never commit `.env`; it is in `.gitignore`.
- Always review generated copy before publishing it.
