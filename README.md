# Codeforces Coach

Codeforces Coach is a Python-based training assistant built for competitive programmers who want guided practice on Codeforces. It combines profile analysis, semantic retrieval, ranking models, and interactive coaching to suggest the next task and explain mistakes without giving away the full solution.

## Features

- Analyze an athlete's Codeforces history and learning profile
- Group users into behavioral archetypes based on their submission patterns
- Search conceptual problem topics using semantic retrieval
- Rank candidate tasks according to difficulty, tags, and user behavior
- Offer Socratic hints for debugging and learning
- Present a lightweight web interface for problem exploration

## Tech stack

- Python
- FastAPI
- SQLAlchemy
- ChromaDB
- SentenceTransformers
- scikit-learn
- XGBoost
- Google Gemini
- HTML, CSS, and JavaScript

## Setup

1. Clone the project
2. Create a Python virtual environment
3. Install dependencies from backend/requirements.txt
4. Copy .env.example to .env and populate the required values
5. Run the API and frontend locally

## Running the app

From the backend directory:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open the local frontend in a browser to use the app.

## Notes

This project is intended for learning, experimentation, and AI-assisted training workflows. It is not a production deployment package by default.
