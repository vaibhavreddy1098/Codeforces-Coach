# Codeforces Coach

An AI-powered training companion for competitive programming. Codeforces Coach analyzes a learner's submission history, recommends problems to practice, supports natural-language problem search, and offers Socratic debugging guidance.

This repository is currently configured for the Codeforces profile **[vaibhavreddy](https://codeforces.com/profile/vaibhavreddy)**. Account access and leaderboard results are limited to that profile.

## What it can do

- **Analyze practice history** to estimate strengths, weaknesses, and a suitable difficulty level.
- **Recommend problems** from a local problem index, excluding problems already attempted.
- **Search by concept** with natural-language queries, tags, and rating constraints.
- **Offer debugging hints** that guide you toward a fix instead of simply giving away a solution.
- **Track practice** with saved history and completion status.

Gemini-powered query interpretation and debugging features are optional and require a Gemini API key. Problem indexing and local vector search use scikit-learn's `HashingVectorizer`, so they do not need a downloaded embedding model. When trained model files are unavailable, the app uses profile/rating-based fallbacks.

## How it works

```text
Browser UI
   |
   v
FastAPI backend ---- SQLite (accounts and practice history)
   |             \
   |              +--- Codeforces API (profile and submissions)
   |
   +--- ChromaDB + local embeddings (problem search)
   |
   +--- Optional Gemini integration (query parsing and debugging hints)
```

## Run locally

### Requirements

- Python 3.10 or later
- Internet access to fetch Codeforces problem data
- Optional: a [Google Gemini API key](https://aistudio.google.com/app/apikey)

### Install

```powershell
git clone https://github.com/vaibhavreddy1098/Codeforces-Coach.git
cd Codeforces-Coach\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Configure

Create `backend/.env` if you want to enable Gemini features:

```env
GEMINI_API_KEY=your_gemini_api_key
CHROMA_COLLECTION_NAME=cf_problems
SECRET_KEY=replace_with_a_long_random_value
```

Keep `.env` private; it is excluded from Git.

### Build the local problem index

Run each step from the `backend` directory:

```powershell
python pipeline.py --step 1
python pipeline.py --step 2
python pipeline.py --step 3
```

The steps fetch and store Codeforces problems, generate searchable descriptions, and build the ChromaDB index. Editorial ingestion is optional:

```powershell
python pipeline.py --step 4
```

The first run may take a while because it downloads data from external sources.

### Start the app

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Technology

- **API:** FastAPI, SQLAlchemy, SQLite
- **Problem retrieval:** ChromaDB, scikit-learn `HashingVectorizer`
- **Profile and ranking:** scikit-learn, optional GMM/XGBoost model artifacts
- **AI assistance:** Optional Google Gemini integration and LangGraph workflow
- **Frontend:** HTML, CSS, and vanilla JavaScript

## Data and configuration

SQLite and ChromaDB data are created locally under `backend/` and are not intended to be committed. API keys and other secrets belong in `backend/.env`, never in source control. The profile restriction is configured in `backend/config.py`; this project is not currently a multi-user service.
