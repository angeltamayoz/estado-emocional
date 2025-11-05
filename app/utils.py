"""
Utilities for EmoTrack
- CSV helpers
- token helpers (JWT)
"""

from pathlib import Path
import csv, time, os
from jose import jwt
from datetime import datetime, timedelta

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
USERS_CSV = DATA_DIR / "users.csv"

# JWT config (change SECRET_KEY for production)
SECRET_KEY = "change_this_secret_for_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def read_csv_rows(path):
    rows = []
    if not Path(path).exists():
        return rows
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def write_csv_rows(path, rows, fieldnames):
    os.makedirs(Path(path).parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    # Use UNIX timestamp for exp to be compatible with JWT libraries that
    # expect a numeric 'exp' claim. Store as int seconds since epoch.
    to_encode.update({"exp": int(expire.timestamp())})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception as e:
        return None
