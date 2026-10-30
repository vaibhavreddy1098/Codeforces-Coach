from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List
import math

from ml_engine import analyze_user_profile
from chat_engine import fetch_practice_problem, get_socratic_hint, debug_user_code, semantic_problem_search
from models import SessionLocal, User, ProblemHistory, init_db
from auth import hash_password, verify_password, create_session, get_current_user, clear_session
from sqlalchemy import func as sa_func
from config import CF_PROFILE_HANDLE, CF_PROFILE_NAME, CF_PROFILE_URL

app = FastAPI(title="CF Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Defer DB initialization to avoid startup errors
_db_initialized = False

@app.on_event("startup")
def startup_event():
    global _db_initialized
    try:
        init_db()
        _db_initialized = True
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization warning: {e}")
        # Continue anyway - tables might already exist or DB may be initialized on first use


# ── Request models ───────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    cf_handle: str
    password: str

class LoginRequest(BaseModel):
    cf_handle: str
    password: str

class ProfileRequest(BaseModel):
    handle: Optional[str] = None

class ToggleCompleteRequest(BaseModel):
    is_completed: bool

class HintRequest(BaseModel):
    problem_id: str

class DebugRequest(BaseModel):
    problem_id: str
    code: str

class SearchRequest(BaseModel):
    query: str


def _current_user(request: Request) -> dict | None:
    user = get_current_user(request)
    if user and user.get("handle", "").casefold() == CF_PROFILE_HANDLE.casefold():
        return user
    return None


@app.get("/api/config")
def app_config():
    return {
        "cf_handle": CF_PROFILE_HANDLE,
        "profile_name": CF_PROFILE_NAME,
        "profile_url": CF_PROFILE_URL,
    }


# ── Auth endpoints ───────────────────────────────────────────────────

@app.post("/api/register")
def register(req: RegisterRequest, response: Response):
    cf_handle = req.cf_handle.strip()
    password = req.password.strip()

    if not cf_handle or not password:
        raise HTTPException(status_code=400, detail="Handle and password are required.")
    if cf_handle.casefold() != CF_PROFILE_HANDLE.casefold():
        raise HTTPException(
            status_code=403,
            detail=f"This instance is configured for the Codeforces profile '{CF_PROFILE_HANDLE}'.",
        )
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")
    cf_handle = CF_PROFILE_HANDLE

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.cf_handle == cf_handle).first()
        if existing:
            raise HTTPException(status_code=409, detail="This Codeforces handle is already registered.")

        user = User(cf_handle=cf_handle, password_hash=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)

        create_session(response, user.id, user.cf_handle)
        return {"message": "Registration successful!", "cf_handle": user.cf_handle}
    finally:
        db.close()


@app.post("/api/login")
def login(req: LoginRequest, response: Response):
    cf_handle = req.cf_handle.strip()
    password = req.password.strip()

    if not cf_handle or not password:
        raise HTTPException(status_code=400, detail="Handle and password are required.")
    if cf_handle.casefold() != CF_PROFILE_HANDLE.casefold():
        raise HTTPException(
            status_code=403,
            detail=f"This instance is configured for the Codeforces profile '{CF_PROFILE_HANDLE}'.",
        )

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.cf_handle == CF_PROFILE_HANDLE).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid handle or password.")

        create_session(response, user.id, user.cf_handle)
        return {"message": "Login successful!", "cf_handle": user.cf_handle}
    finally:
        db.close()


@app.post("/api/logout")
def logout(response: Response):
    clear_session(response)
    return {"message": "Logged out."}


@app.get("/api/me")
def me(request: Request):
    user = _current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return {"cf_handle": user["handle"]}


# ── Core endpoints (now session-aware) ───────────────────────────────

def _resolve_handle(req: ProfileRequest, request: Request) -> str:
    """Resolve requests only to the configured Codeforces profile."""
    user = _current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    if req.handle and req.handle.strip():
        if req.handle.strip().casefold() != CF_PROFILE_HANDLE.casefold():
            raise HTTPException(
                status_code=403,
                detail=f"This instance is configured for the Codeforces profile '{CF_PROFILE_HANDLE}'.",
            )
    return CF_PROFILE_HANDLE


def _get_user_id(request: Request) -> int:
    """Return the user ID from session or raise."""
    user = _current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return user["uid"]


@app.post("/api/analyze")
def analyze_profile(req: ProfileRequest, request: Request):
    handle = _resolve_handle(req, request)
    result = analyze_user_profile(handle)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/api/get_problem")
def get_problem(req: ProfileRequest, request: Request):
    handle = _resolve_handle(req, request)
    user_id = _get_user_id(request)

    result = analyze_user_profile(handle)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    response = fetch_practice_problem(result)
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])

    problem_details = response.get("problem_details")

    # Auto-save to history
    if problem_details:
        db = SessionLocal()
        try:
            tags_str = problem_details.get("tags", "")
            if isinstance(tags_str, list):
                tags_str = ", ".join(tags_str)

            entry = ProblemHistory(
                user_id=user_id,
                problem_id=problem_details.get("problem_id", ""),
                problem_name=problem_details.get("name", "Unknown"),
                contest_id=int(problem_details.get("contest_id", 0)),
                problem_index=problem_details.get("index", "A"),
                rating=problem_details.get("rating"),
                tags=tags_str,
                coach_message=response.get("message", ""),
                is_completed=False,
            )
            db.add(entry)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Could not save the recommended problem to your history: {e}",
            ) from e
        finally:
            db.close()

    return {
        "message": response["message"],
        "profile": result,
        "problem_details": problem_details,
    }

@app.post("/api/hint")
def api_hint(req: HintRequest, request: Request):
    user = _current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    res = get_socratic_hint(req.problem_id)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return {"message": res["message"]}

@app.post("/api/debug_code")
def api_debug_code(req: DebugRequest, request: Request):
    user = _current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    res = debug_user_code(req.problem_id, req.code)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return {"message": res["message"]}

@app.post("/api/search_problems")
def api_search_problems(req: SearchRequest, request: Request):
    user = _current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    res = semantic_problem_search(req.query)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res


# ── History endpoints ────────────────────────────────────────────────

@app.get("/api/history")
def get_history(request: Request):
    user_id = _get_user_id(request)
    db = SessionLocal()
    try:
        items = (
            db.query(ProblemHistory)
            .filter(ProblemHistory.user_id == user_id)
            .order_by(ProblemHistory.created_at.desc())
            .all()
        )
        return [
            {
                "id": item.id,
                "problem_id": item.problem_id,
                "problem_name": item.problem_name,
                "contest_id": item.contest_id,
                "problem_index": item.problem_index,
                "rating": item.rating,
                "tags": item.tags,
                "coach_message": item.coach_message,
                "is_completed": item.is_completed,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in items
        ]
    finally:
        db.close()


@app.patch("/api/history/{item_id}")
def toggle_history(item_id: int, req: ToggleCompleteRequest, request: Request):
    user_id = _get_user_id(request)
    db = SessionLocal()
    try:
        item = (
            db.query(ProblemHistory)
            .filter(ProblemHistory.id == item_id, ProblemHistory.user_id == user_id)
            .first()
        )
        if not item:
            raise HTTPException(status_code=404, detail="History item not found.")
        item.is_completed = req.is_completed
        db.commit()
        return {"id": item.id, "is_completed": item.is_completed}
    finally:
        db.close()


@app.delete("/api/history/{item_id}")
def delete_history(item_id: int, request: Request):
    user_id = _get_user_id(request)
    db = SessionLocal()
    try:
        item = (
            db.query(ProblemHistory)
            .filter(ProblemHistory.id == item_id, ProblemHistory.user_id == user_id)
            .first()
        )
        if not item:
            raise HTTPException(status_code=404, detail="History item not found.")
        db.delete(item)
        db.commit()
        return {"message": "Deleted."}
    finally:
        db.close()


# ── Leaderboard endpoint ────────────────────────────────────────────

@app.get("/api/leaderboard")
def get_leaderboard(request: Request, search: Optional[str] = None):
    """
    Ranking formula: avg_rating_of_completed_problems * log2(n + 1)
    where n = number of completed AI-recommended problems.
    """
    _get_user_id(request)
    db = SessionLocal()
    try:
        leaderboard = []
        profile_user = (
            db.query(User)
            .filter(User.cf_handle == CF_PROFILE_HANDLE)
            .first()
        )
        if profile_user:
            stats = (
                db.query(
                    sa_func.avg(ProblemHistory.rating),
                    sa_func.count(ProblemHistory.id),
                )
                .filter(
                    ProblemHistory.user_id == profile_user.id,
                    ProblemHistory.is_completed.is_(True),
                    ProblemHistory.rating.isnot(None),
                )
                .first()
            )
            avg_r = float(stats[0] or 0)
            n = int(stats[1] or 0)
            score = avg_r * math.log2(n + 1) if n > 0 else 0
            leaderboard.append({
                "user_id": profile_user.id,
                "cf_handle": CF_PROFILE_HANDLE,
                "avg_rating": round(avg_r, 1),
                "total_solves": n,
                "score": round(score, 1),
                "rank": 1,
            })

        if search and search.strip():
            q = search.strip().lower()
            leaderboard = [e for e in leaderboard if q in e["cf_handle"].lower()]

        current_user = _current_user(request)
        my_rank = 1 if current_user and profile_user else None

        return {
            "leaderboard": leaderboard,
            "total_users": 1 if profile_user else 0,
            "my_rank": my_rank,
            "my_handle": current_user["handle"] if current_user else None,
        }
    finally:
        db.close()


# ── Static files (must be last) ─────────────────────────────────────

static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
