"""
analytics.py - Data processing, risk detection and visualizations.
Generates data/alerts.csv and returns summaries for the API.
"""

import pandas as pd
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
SURVEYS_CSV = DATA_DIR / "surveys.csv"
ALERTS_CSV = DATA_DIR / "alerts.csv"

NEGATIVE_KEYWORDS = ["mal","triste","estres","depres","ansiedad","angusti","suicid","suicida","no puedo"]

WEIGHTS = {"mood_score":0.40,"sleep_hours":0.25,"appetite":0.20,"concentration":0.15}

def notes_penalty(notes):
    if not isinstance(notes,str):
        return 0.0
    text = notes.lower()
    for kw in NEGATIVE_KEYWORDS:
        if kw in text:
            return 0.12
    return 0.0

def normalize_sleep(hours):
    try:
        h = float(hours)
    except Exception:
        return 50.0
    ideal = 7.5
    diff = abs(h-ideal)
    score = max(0, 100 - diff*15)
    return min(100, max(0, score))

def scale_0_10_to_0_100(v):
    try:
        return max(0, min(100, (float(v)/10.0)*100))
    except Exception:
        return 50.0

def compute_composite(row):
    mood = row.get("mood_score", None)
    if pd.notna(mood) and mood != "":
        try:
            mood_v = float(mood)
        except:
            mood_v = scale_0_10_to_0_100(row.get("mood",5))
    else:
        mood_v = scale_0_10_to_0_100(row.get("mood",5))
    sleep = normalize_sleep(row.get("sleep_hours",7))
    appetite = scale_0_10_to_0_100(row.get("appetite",5))
    concentration = scale_0_10_to_0_100(row.get("concentration",5))
    base = WEIGHTS["mood_score"]*mood_v + WEIGHTS["sleep_hours"]*sleep + WEIGHTS["appetite"]*appetite + WEIGHTS["concentration"]*concentration
    penalty = notes_penalty(row.get("notes",""))
    final = base * (1 - penalty)
    return round(final,2)

def trend_negative_for_user(df_user):
    if df_user.shape[0] < 3:
        return False
    vals = df_user.sort_values("created_at",ascending=False)["mood_score"].head(3).tolist()
    if len(vals) < 3:
        return False
    try:
        return vals[0] < vals[1] < vals[2]
    except:
        return False

def compute_risk():
    # Load surveys
    if not SURVEYS_CSV.exists():
        return {"message":"no surveys", "n_users":0}
    df = pd.read_csv(SURVEYS_CSV, parse_dates=["created_at"])
    if df.empty:
        return {"message":"no data", "n_users":0}
    # ensure columns
    for c in ["mood_score","sleep_hours","appetite","concentration","notes"]:
        if c not in df.columns:
            df[c] = None
    # compute composite per row
    df["composite"] = df.apply(compute_composite, axis=1)
    # average per user
    user_avg = df.groupby(["user_id","username"])["composite"].mean().reset_index().rename(columns={"composite":"avg_score"})
    # trend flags
    trend_flags = []
    for uid in user_avg["user_id"]:
        df_user = df[df["user_id"]==uid]
        trend_flags.append(trend_negative_for_user(df_user))
    user_avg["trend_negative"] = trend_flags
    # label mapping
    def label(score,trend):
        if trend: return "ALTO"
        if score >= 80: return "BAJO"
        if score >= 60: return "MODERADO"
        return "ALTO"
    user_avg["risk_level"] = user_avg.apply(lambda r: label(r["avg_score"], r["trend_negative"]), axis=1)
    # write alerts.csv
    user_avg.to_csv(ALERTS_CSV, index=False)
    counts = user_avg["risk_level"].value_counts().to_dict()
    import csv
    # ensure recommendations.csv exists
    rec_file = DATA_DIR / 'recommendations.csv'
    if not rec_file.exists():
        with rec_file.open('w', encoding='utf-8') as rf:
            rf.write('risk_level,recommendation\nALTO,Contactar a un profesional de salud mental\nMODERADO,Monitoreo semanal y ejercicios de relajación\nBAJO,Mantener hábitos saludables\n')
    return {"counts":counts, "n_users": len(user_avg), "alerts": user_avg.to_dict(orient="records")}


def get_recommendation_for_risk(risk_level):
    rec_file = DATA_DIR / 'recommendations.csv'
    if not rec_file.exists():
        return ''
    import csv
    with rec_file.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r['risk_level'].strip().upper() == risk_level.strip().upper():
                return r['recommendation']
    return ''
