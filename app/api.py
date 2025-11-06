# api.py - HTTP endpoints only. Heavy logic moved to models/utils/analytics.
from fastapi import FastAPI, HTTPException, Header, WebSocket
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import time

# Local utilities and modules
from app.utils import create_access_token, decode_access_token, read_csv_rows, write_csv_rows, get_user_from_token
from app import analytics, models
from app.models import Register, Login, SurveyCreate
import pandas as pd

# Paths
BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
USERS_CSV = DATA_DIR / "users.csv"
SURVEYS_CSV = DATA_DIR / "surveys.csv"
ALERTS_CSV = DATA_DIR / "alerts.csv"

# App
app = FastAPI(title="EmoTrack API")
FRONTEND_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]
app.add_middleware(CORSMiddleware, allow_origins=FRONTEND_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# In-memory websocket connections set
connections = set()


@app.get("/user-plot")
def user_plot(token: str | None = None, Authorization: str | None = Header(None), kind: str = "evolution"):
    """Return a PNG image with user's plots. Delegates plotting to app.analytics.generate_user_plot."""
    auth_value = Authorization if Authorization else (f"Bearer {token}" if token else None)
    user = get_user_from_token(auth_value)
    if not user or not user.get('username'):
        raise HTTPException(status_code=401, detail="No autenticado")
    username = user['username']

    try:
        img_bytes = analytics.generate_user_plot(username, kind=kind)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando gráfica: {e}")

    return Response(content=img_bytes, media_type='image/png')


@app.post("/register")
def register(payload: Register):
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    rows = read_csv_rows(USERS_CSV)
    for row in rows:
        if row["username"].lower() == payload.username.lower():
            raise HTTPException(status_code=400, detail="Username already taken")
        if row["email"].lower() == payload.email.lower():
            raise HTTPException(status_code=400, detail="Email already registered")

    next_id = max([int(row["id"]) for row in rows]) + 1 if rows else 1
    role = payload.role if payload.role else ('admin' if payload.username.lower() in ['admin','administrator','root'] else 'user')
    new_user = {
        "id": next_id,
        "username": payload.username,
        "email": payload.email,
        "hashed_password": payload.password,
        "role": role,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    rows.append(new_user)
    write_csv_rows(USERS_CSV, rows, ["id","username","email","hashed_password","role","created_at"])
    token = create_access_token({"user_id": next_id, "username": payload.username, "role": role})
    return {"access_token": token, "token_type": "bearer", "user": {"id": next_id, "username": payload.username, "role": role}}


@app.post("/login")
def login(payload: Login):
    rows = read_csv_rows(USERS_CSV)
    for r in rows:
        if r["username"] == payload.username and r["hashed_password"] == payload.password:
            token = create_access_token({"user_id": int(r["id"]), "username": r["username"], "role": r.get('role','user')})
            return {"access_token": token, "token_type":"bearer", "user_id": r["id"], "username": r["username"], "role": r.get('role','user')}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/surveys")
def create_survey(s: SurveyCreate, Authorization: str | None = Header(None)):
    user = get_user_from_token(Authorization)
    if not user or not user.get('username'):
        raise HTTPException(status_code=401, detail="No autenticado")
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    rows = read_csv_rows(SURVEYS_CSV) if SURVEYS_CSV.exists() else []
    next_id = max([int(r["id"]) for r in rows]) + 1 if rows else 1
    user_id = user["user_id"]
    username = user["username"]
    mood_score = s.mood_score if s.mood_score is not None else min(100, max(0, s.mood*10))
    if not s.mood or s.mood < 1 or s.mood > 10:
        raise HTTPException(status_code=400, detail="Invalid mood value")
    row = {"id": next_id, "user_id": user_id, "username": username, "mood": s.mood, "mood_score": mood_score, "sleep_hours": s.sleep_hours if s.sleep_hours is not None else "", "appetite": s.appetite if s.appetite is not None else "", "concentration": s.concentration if s.concentration is not None else "", "notes": s.notes or "", "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    rows.append(row)
    fieldnames = ["id","user_id","username","mood","mood_score","sleep_hours","appetite","concentration","notes","created_at"]
    write_csv_rows(SURVEYS_CSV, rows, fieldnames)
    # Keep analytics.compute_risk call optional but silent (it may exist)
    try:
        analytics.compute_risk()
    except Exception:
        pass
    return {"status":"ok", "data":row}


@app.get("/me")
def me(Authorization: str | None = Header(None)):
    if not Authorization or not Authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Not authenticated')
    token = Authorization.split(' ',1)[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail='Invalid token')
    return { 'user_id': payload.get('user_id'), 'username': payload.get('username') }

@app.get("/stats")
def get_stats(Authorization: str | None = Header(None)):
    user = get_user_from_token(Authorization)
    if not SURVEYS_CSV.exists():
        return {"average_mood": 0, "total_entries": 0, "history": [], "alerts": []}
    rows = read_csv_rows(SURVEYS_CSV)
    if not rows:
        return {"average_mood": 0, "total_entries": 0, "history": [], "alerts": []}
    if user and user.get('username'):
        user_rows = [r for r in rows if r.get('username') == user['username']]
        n = len(user_rows)
        if n == 0:
            return {"average_mood": 0, "total_entries": 0, "history": [], "alerts": []}
        total_mood = sum(float(r.get('mood', 0)) for r in user_rows)
        average = round(total_mood / n, 2)
        last_5 = sorted(user_rows, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        alerts = []
        try:
            if analytics.check_alerts(last_5):
                alerts.append({"type": "mood", "message": "Posible estado de riesgo detectado"})
        except Exception:
            pass
        return {"average_mood": average, "total_entries": n, "history": last_5, "alerts": alerts}
    import pandas as _pd
    df = _pd.DataFrame(rows)
    df['mood'] = _pd.to_numeric(df.get('mood', _pd.Series()), errors='coerce')
    total = int(len(df.dropna(subset=['mood'])))
    avg = float(df['mood'].mean()) if total > 0 else 0
    try:
        df['created_at'] = _pd.to_datetime(df['created_at'])
        ts = df.set_index('created_at').resample('D')['mood'].mean().ffill().reset_index()
        history = ts.assign(date=ts['created_at'].dt.strftime('%Y-%m-%d')).rename(columns={'mood':'mood'}).loc[:, ['date','mood']].to_dict(orient='records')
    except Exception:
        history = []
    return { 'average_mood': round(avg,2), 'total_entries': total, 'history': history, 'alerts': [] }


@app.get("/recommendations")
def get_user_recommendations(Authorization: str | None = Header(None)):
    user = get_user_from_token(Authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido o no encontrado")
    username = user['username']
    alerts = []
    if ALERTS_CSV.exists():
        with ALERTS_CSV.open(encoding='utf-8') as f:
            import csv
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('username') == username:
                    alerts.append(row)
    user_risk = "BAJO"
    if alerts:
        user_risk = alerts[-1].get('risk_level', 'BAJO')
    recommendation = analytics.get_recommendation_for_risk(user_risk)
    return {"username": username, "risk_level": user_risk, "recommendation": recommendation, "general_tips": ["Mantén un horario de sueño regular", "Realiza ejercicio físico moderado", "Practica técnicas de relajación", "Mantén una alimentación balanceada"]}


@app.get("/all-alerts")
def get_all_alerts(Authorization: str | None = Header(None)):
    user = get_user_from_token(Authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido o no encontrado")
    all_alerts = []
    if ALERTS_CSV.exists():
        with ALERTS_CSV.open(encoding='utf-8') as f:
            import csv
            reader = csv.DictReader(f)
            for row in reader:
                all_alerts.append({"user_id": row.get('user_id', ''), "username": row.get('username', ''), "risk_level": row.get('risk_level', 'BAJO'), "avg_score": float(row.get('avg_score', 0)), "trend_negative": row.get('trend_negative', 'False') == 'True'})
    return {"total_alerts": len(all_alerts), "alerts": all_alerts}
