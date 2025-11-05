from fastapi import FastAPI, HTTPException, Header, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import csv, time, os, io
# Configure matplotlib to use 'Agg' backend (no GUI required)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
# Set style once at import
plt.style.use('seaborn-v0_8')
sns.set_style("whitegrid")
from pathlib import Path
import os, io, time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# utils and analytics
from app.utils import create_access_token, decode_access_token, read_csv_rows, write_csv_rows
from app import analytics

# Paths
BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
USERS_CSV = DATA_DIR / "users.csv"
SURVEYS_CSV = DATA_DIR / "surveys.csv"
ALERTS_CSV = DATA_DIR / "alerts.csv"

# App
app = FastAPI(title="EmoTrack API")
# Allow local frontend origins explicitly so browsers accept Access-Control-Allow-Credentials when used.
FRONTEND_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]
app.add_middleware(CORSMiddleware, allow_origins=FRONTEND_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# In-memory websocket connections
connections = set()

# Pydantic models
class Register(BaseModel):
    username: str
    email: str
    password: str
    role: str | None = None

class Login(BaseModel):
    username: str
    password: str

class SurveyCreate(BaseModel):
    mood: int
    mood_score: int | None = None
    sleep_hours: float | None = None
    appetite: int | None = None
    concentration: int | None = None
    notes: str | None = None


# Helper to extract user
def get_user_from_token(authorization: str | None):
    if not authorization:
        return None
    token = None
    if isinstance(authorization, str) and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    else:
        token = authorization
    payload = decode_access_token(token)
    if not payload:
        return None
    try:
        user_id = int(payload.get("user_id", 0))
    except Exception:
        user_id = 0
    return {"user_id": user_id, "username": payload.get("username", "anonymous"), "role": payload.get('role','user')}

@app.get("/user-plot")
def user_plot(token: str | None = None, Authorization: str | None = Header(None), kind: str = "evolution"):
    """Return a PNG image with user's plots. Accepts Authorization header or token query param.
    Query param 'kind' can be: evolution (default), hist, sleep, summary."""
    # Prefer Authorization header, otherwise use token query param
    auth_value = Authorization if Authorization else (f"Bearer {token}" if token else None)
    user = get_user_from_token(auth_value)
    if not user or not user.get('username'):
        raise HTTPException(status_code=401, detail="No autenticado")
    username = user['username']

    # Ensure surveys file exists
    if not SURVEYS_CSV.exists():
        raise HTTPException(status_code=404, detail="No hay datos de encuestas")

    try:
        df = pd.read_csv(SURVEYS_CSV, parse_dates=['created_at'])
    except Exception:
        raise HTTPException(status_code=500, detail="Error leyendo datos de encuestas")

    # Filter for the user
    df_user = df[df['username'] == username].copy()
    if df_user.empty:
        # Return an image with a friendly message
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.text(0.5, 0.5, f"Sin datos para {username}", ha='center', va='center', fontsize=14)
        ax.axis('off')
    else:
        # Prepare data
        df_user['mood'] = pd.to_numeric(df_user['mood'], errors='coerce')
        if 'sleep_hours' in df_user.columns:
            df_user['sleep_hours'] = pd.to_numeric(df_user['sleep_hours'], errors='coerce')
        if 'appetite' in df_user.columns:
            df_user['appetite'] = pd.to_numeric(df_user['appetite'], errors='coerce')
        if 'concentration' in df_user.columns:
            df_user['concentration'] = pd.to_numeric(df_user['concentration'], errors='coerce')
        
        df_user = df_user.dropna(subset=['mood'])
        df_user['created_at'] = pd.to_datetime(df_user['created_at'])
        df_user = df_user.set_index('created_at')
        
        # Select plot type
        k = kind.lower() if kind else 'evolution'
        
        if k == 'hist':
            fig, ax = plt.subplots(figsize=(7,3))
            sns.histplot(df_user['mood'], bins=10, kde=True, color='#2563eb', ax=ax)
            ax.set_title(f'Distribución de ánimo — {username}')
            ax.set_xlabel('Ánimo (1-10)')
            ax.set_ylabel('Frecuencia')
            
        elif k == 'sleep':
            fig, axs = plt.subplots(1,2, figsize=(10,3))
            sns.boxplot(x=df_user['sleep_hours'], color='#059669', ax=axs[0])
            axs[0].set_title('Boxplot de sueño')
            axs[0].set_xlabel('Horas')
            sns.histplot(df_user['sleep_hours'], bins=8, color='#059669', ax=axs[1])
            axs[1].set_title('Histograma de sueño')
            axs[1].set_xlabel('Horas')
            fig.suptitle(f'Análisis de sueño — {username}')
            
        elif k == 'summary':
            # Make summary consistent height with other plots
            metrics = {
                'Ánimo': df_user['mood'].mean(),
                'Sueño': df_user['sleep_hours'].mean() if 'sleep_hours' in df_user else None,
                'Apetito': df_user['appetite'].mean() if 'appetite' in df_user else None,
                'Concentración': df_user['concentration'].mean() if 'concentration' in df_user else None
            }
            # Filter out None values
            labels = [k for k,v in metrics.items() if v is not None]
            values = [v for v in metrics.values() if v is not None]
            colors = ['#2563eb','#059669','#10b981','#f59e0b'][:len(values)]

            # Use same height as other user plots (3 inches) for visual consistency
            fig, ax = plt.subplots(figsize=(8,3))
            if values:
                ax.bar(labels, values, color=colors)
                ax.set_ylim(0, 10)
                ax.set_title(f'Resumen de métricas — {username}')
                # place labels just above bars but ensure they stay inside the axis
                for i, v in enumerate(values):
                    y = min(v + 0.2, 9.8)
                    ax.text(i, y, f'{v:.1f}', ha='center', va='bottom', fontsize=9)
            else:
                ax.text(0.5, 0.5, 'No hay métricas disponibles', ha='center', va='center')
                ax.axis('off')
            
        else:  # evolution (default)
            daily = df_user['mood'].resample('D').mean()
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.plot(daily.index, daily.values, marker='o', color='#2563eb', label='Ánimo diario')
            if len(daily) >= 3:
                rolling = daily.rolling(window=3, min_periods=1).mean()
                ax.plot(rolling.index, rolling.values, linestyle='--', color='#f59e0b', label='Media móvil (3d)')
            ax.set_title(f'Evolución de ánimo — {username}')
            ax.set_ylabel('Ánimo (1-10)')
            ax.set_xlabel('Fecha')
            ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d-%m'))
            ax.legend()
            fig.autofmt_xdate(rotation=30)

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png', dpi=120)
    plt.close(fig)
    buf.seek(0)
    return Response(content=buf.read(), media_type='image/png')

@app.post("/register")
def register(payload: Register):
    """Handle user registration. Creates a new user in users.csv and returns a JWT token."""
    # Validate username and email are unique
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    rows = read_csv_rows(USERS_CSV)
    
    # Check for duplicates
    for row in rows:
        if row["username"].lower() == payload.username.lower():
            raise HTTPException(status_code=400, detail="Username already taken")
        if row["email"].lower() == payload.email.lower():
            raise HTTPException(status_code=400, detail="Email already registered")

    # Prepare new user data
    next_id = max([int(row["id"]) for row in rows]) + 1 if rows else 1
    role = payload.role if payload.role else ('admin' if payload.username.lower() in ['admin','administrator','root'] else 'user')
    
    # Create user record
    new_user = {
        "id": next_id,
        "username": payload.username,
        "email": payload.email,
        "hashed_password": payload.password,  # In production, hash this!
        "role": role,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    rows.append(new_user)
    
    # Save to CSV
    write_csv_rows(USERS_CSV, rows, ["id","username","email","hashed_password","role","created_at"])
    
    # Generate token and return
    token = create_access_token({
        "user_id": next_id,
        "username": payload.username,
        "role": role
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": next_id, "username": payload.username, "role": role}
    }

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
    # Validate authentication
    user = get_user_from_token(Authorization)
    if not user or not user.get('username'):
        raise HTTPException(status_code=401, detail="No autenticado")

    # Create data directory if not exists
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    
    # Read existing surveys
    rows = []
    if SURVEYS_CSV.exists():
        rows = read_csv_rows(SURVEYS_CSV)
    
    # Create new survey entry
    next_id = max([int(r["id"]) for r in rows]) + 1 if rows else 1
    user_id = user["user_id"]
    username = user["username"]
    mood_score = s.mood_score if s.mood_score is not None else min(100, max(0, s.mood*10))
    
    # Validate required fields
    if not s.mood or s.mood < 1 or s.mood > 10:
        raise HTTPException(status_code=400, detail="Invalid mood value")
    
    # Create survey record - Handle 0 values properly
    row = {
        "id": next_id,
        "user_id": user_id,
        "username": username,
        "mood": s.mood,
        "mood_score": mood_score,
        "sleep_hours": s.sleep_hours if s.sleep_hours is not None else "",
        "appetite": s.appetite if s.appetite is not None else "",
        "concentration": s.concentration if s.concentration is not None else "",
        "notes": s.notes or "",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    rows.append(row)
    
    # Save to CSV
    fieldnames = ["id","user_id","username","mood","mood_score","sleep_hours","appetite","concentration","notes","created_at"]
    write_csv_rows(SURVEYS_CSV, rows, fieldnames)
    
    # Recalculate risk analysis after new survey
    try:
        analytics.compute_risk()
        print(f"Risk analysis updated after survey from {username}")
    except Exception as e:
        print(f"Error updating risk analysis: {e}")
    
    return {"status":"ok", "data":row}


@app.get("/me")
def me(Authorization: str | None = Header(None)):
    """Return current user based on token or 401."""
    from app.utils import decode_access_token
    if not Authorization or not Authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Not authenticated')
    token = Authorization.split(' ',1)[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail='Invalid token')
    return { 'user_id': payload.get('user_id'), 'username': payload.get('username') }


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket, token: str):
    try:
        user = get_user_from_token(token)
        if not user:
            await websocket.close(code=1008)
            return
        await websocket.accept()
        # enviar alertas...
    except Exception as e:
        print("Error WS:", e)
        await websocket.close()


@app.post("/analytics/compute-risk")
async def compute_risk_endpoint(Authorization: str | None = Header(None)):
    res = analytics.compute_risk()
    # Broadcast a simple notification to connected websocket clients
    import json as _json
    msg = {'type':'compute_risk','summary': res.get('counts',{}), 'n_users': res.get('n_users',0)}
    for ws in list(connections):
        try:
            # send as text
            await ws.send_text(_json.dumps(msg))
        except Exception:
            connections.discard(ws)
    return res


@app.get("/dashboard-data")
def dashboard_data():
    """
    Returns JSON with:
      - alerts_summary: counts per risk level
      - alerts_table: list of alerts records
      - timeseries: daily average mood_score (global)
      - user_avg: average score per user
    """
    # Ensure latest alerts are computed
    res = analytics.compute_risk()
    # Prepare timeseries from surveys.csv
    import pandas as pd
    surveys_csv = DATA_DIR / "surveys.csv"
    timeseries = []
    if surveys_csv.exists():
        try:
            df = pd.read_csv(surveys_csv, parse_dates=['created_at'])
            df['mood_score'] = pd.to_numeric(df['mood_score'], errors='coerce')
            ts = df.set_index('created_at').resample('D')['mood_score'].mean().ffill().reset_index()
            timeseries = ts.assign(created_at=ts['created_at'].dt.strftime('%Y-%m-%d')).to_dict(orient='records')
        except Exception:
            timeseries = []
    # read alerts records
    alerts = []
    alerts_csv = DATA_DIR / "alerts.csv"
    if alerts_csv.exists():
        import csv
        with alerts_csv.open(encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                alerts.append(r)
    # user averages
    user_avg = res.get('alerts', []) if isinstance(res, dict) else []
    return {'alerts_summary': res.get('counts', {}), 'alerts_table': alerts, 'timeseries': timeseries, 'user_avg': user_avg}


@app.get("/stats")
def get_stats(Authorization: str | None = Header(None)):
    """Return per-user stats when Authorization is provided and valid.
    If no Authorization is provided, return global aggregated stats used by the public dashboard.
    """
    user = get_user_from_token(Authorization)

    if not SURVEYS_CSV.exists():
        return {"average_mood": 0, "total_entries": 0, "history": [], "alerts": []}

    rows = read_csv_rows(SURVEYS_CSV)
    if not rows:
        return {"average_mood": 0, "total_entries": 0, "history": [], "alerts": []}

    # If user provided and valid, return per-user stats
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
            # analytics may fail; don't break stats
            pass
        return {"average_mood": average, "total_entries": n, "history": last_5, "alerts": alerts}

    # Global aggregate for unauthenticated dashboard
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


@app.get("/data/alerts.csv")
def get_alerts_csv():
    if not ALERTS_CSV.exists():
        raise HTTPException(status_code=404, detail="alerts.csv not found")
    return ALERTS_CSV.read_text(encoding="utf-8")


@app.get("/data/analysis.json")
def get_analysis_json():
    p = DATA_DIR / "analysis.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="analysis.json not found")
    return p.read_text(encoding="utf-8")


@app.get("/recommendations")
def get_user_recommendations(Authorization: str | None = Header(None)):
    """Get personalized recommendations for the current user based on their risk level"""
    user = get_user_from_token(Authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido o no encontrado")
    
    username = user['username']
    
    # Get user's risk level from alerts.csv
    alerts = []
    if ALERTS_CSV.exists():
        with ALERTS_CSV.open(encoding='utf-8') as f:
            import csv
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('username') == username:
                    alerts.append(row)
    
    # Get user's current risk level
    user_risk = "BAJO"  # default
    if alerts:
        # Get the most recent alert for this user
        user_risk = alerts[-1].get('risk_level', 'BAJO')
    
    # Get recommendation for this risk level
    recommendation = analytics.get_recommendation_for_risk(user_risk)
    
    return {
        "username": username,
        "risk_level": user_risk,
        "recommendation": recommendation,
        "general_tips": [
            "Mantén un horario de sueño regular",
            "Realiza ejercicio físico moderado",
            "Practica técnicas de relajación",
            "Mantén una alimentación balanceada"
        ]
    }


@app.get("/user-alerts")
def get_user_alerts(Authorization: str | None = Header(None)):
    """Get alerts for the current user"""
    user = get_user_from_token(Authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido o no encontrado")
    
    username = user['username']
    
    # Get user's alerts from alerts.csv
    user_alerts = []
    if ALERTS_CSV.exists():
        with ALERTS_CSV.open(encoding='utf-8') as f:
            import csv
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('username') == username:
                    user_alerts.append({
                        "risk_level": row.get('risk_level', 'BAJO'),
                        "avg_score": float(row.get('avg_score', 0)),
                        "trend_negative": row.get('trend_negative', 'False') == 'True',
                        "message": f"Tu nivel de riesgo es {row.get('risk_level', 'BAJO')} con un puntaje promedio de {row.get('avg_score', 0)}"
                    })
    
    return {
        "username": username,
        "alerts": user_alerts
    }


@app.get("/all-alerts")
def get_all_alerts(Authorization: str | None = Header(None)):
    """Get all alerts from the database (requires authentication)"""
    user = get_user_from_token(Authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido o no encontrado")
    
    # Get all alerts from alerts.csv
    all_alerts = []
    if ALERTS_CSV.exists():
        with ALERTS_CSV.open(encoding='utf-8') as f:
            import csv
            reader = csv.DictReader(f)
            for row in reader:
                all_alerts.append({
                    "user_id": row.get('user_id', ''),
                    "username": row.get('username', ''),
                    "risk_level": row.get('risk_level', 'BAJO'),
                    "avg_score": float(row.get('avg_score', 0)),
                    "trend_negative": row.get('trend_negative', 'False') == 'True'
                })
    
    return {
        "total_alerts": len(all_alerts),
        "alerts": all_alerts
    }
