from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import os
import csv

# Local data folder (project_root/data)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
SURVEYS_CSV = os.path.join(DATA_DIR, "surveys.csv")


def _ensure_csv(path: str, headers: List[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)


def _get_next_id(path: str) -> int:
    if not os.path.exists(path):
        return 1
    try:
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            max_id = 0
            for row in reader:
                try:
                    val = int(row.get("id", 0))
                    if val > max_id:
                        max_id = val
                except Exception:
                    continue
            return max_id + 1
    except Exception:
        return 1


@dataclass
class User:
    id: int
    username: str
    email: str
    hashed_password: str
    created_at: datetime


class UserDatabase:
    """CSV-backed user storage. No in-memory state is kept between operations."""

    def __init__(self):
        _ensure_csv(USERS_CSV, ["id", "username", "email", "hashed_password", "created_at"]) 

    def create_user(self, username: str, email: str, hashed_password: str) -> User:
        user_id = _get_next_id(USERS_CSV)
        created_at = datetime.now()
        try:
            with open(USERS_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([user_id, username, email, hashed_password, created_at.isoformat()])
        except Exception:
            # If persistence fails, raise to notify caller
            raise
        return User(id=user_id, username=username, email=email, hashed_password=hashed_password, created_at=created_at)

    def _iter_users(self):
        if not os.path.exists(USERS_CSV):
            return
        with open(USERS_CSV, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    uid = int(row.get("id", 0))
                    created_at = datetime.fromisoformat(row.get("created_at")) if row.get("created_at") else datetime.now()
                    yield User(id=uid, username=row.get("username"), email=row.get("email"), hashed_password=row.get("hashed_password"), created_at=created_at)
                except Exception:
                    continue

    def get_user_by_username(self, username: str) -> Optional[User]:
        for u in self._iter_users():
            if u.username == username:
                return u
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        for u in self._iter_users():
            if u.email == email:
                return u
        return None

    def user_exists(self, username: str, email: str) -> bool:
        return self.get_user_by_username(username) is not None or self.get_user_by_email(email) is not None

    def update_user(self, user_id: int, username: Optional[str] = None, email: Optional[str] = None, hashed_password: Optional[str] = None) -> Optional[User]:
        """Update a user in the CSV. Returns updated User or None if not found."""
        if not os.path.exists(USERS_CSV):
            return None
        updated = None
        rows = []
        try:
            with open(USERS_CSV, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        uid = int(row.get("id", 0))
                    except Exception:
                        rows.append(row)
                        continue
                    if uid == user_id:
                        # modify
                        if username is not None:
                            row["username"] = username
                        if email is not None:
                            row["email"] = email
                        if hashed_password is not None:
                            row["hashed_password"] = hashed_password
                        row["created_at"] = row.get("created_at") or datetime.now().isoformat()
                        updated = User(id=uid, username=row["username"], email=row["email"], hashed_password=row["hashed_password"], created_at=datetime.fromisoformat(row["created_at"]))
                    rows.append(row)
        except Exception:
            return None

        # write back
        try:
            with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["id", "username", "email", "hashed_password", "created_at"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in rows:
                    writer.writerow({k: r.get(k, "") for k in fieldnames})
        except Exception:
            return None

        return updated

    def delete_user(self, user_id: int) -> bool:
        """Delete a user by id. Returns True if deleted."""
        if not os.path.exists(USERS_CSV):
            return False
        deleted = False
        rows = []
        try:
            with open(USERS_CSV, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        uid = int(row.get("id", 0))
                    except Exception:
                        rows.append(row)
                        continue
                    if uid == user_id:
                        deleted = True
                        continue
                    rows.append(row)
        except Exception:
            return False

        try:
            with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["id", "username", "email", "hashed_password", "created_at"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in rows:
                    writer.writerow({k: r.get(k, "") for k in fieldnames})
        except Exception:
            return False

        return deleted


# Instancia global de la base de datos (CSV-backed)
user_db = UserDatabase()


@dataclass
class Survey:
    id: int
    user_id: int
    username: str
    mood: int
    notes: Optional[str]
    created_at: datetime


class SurveyDatabase:
    """CSV-backed survey storage. No in-memory state is kept between operations."""

    def __init__(self):
        _ensure_csv(SURVEYS_CSV, ["id", "user_id", "username", "mood", "notes", "created_at"])

    def create_survey(self, user_id: int, username: str, mood: int, notes: Optional[str]) -> Survey:
        survey_id = _get_next_id(SURVEYS_CSV)
        created_at = datetime.now()
        try:
            with open(SURVEYS_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([survey_id, user_id, username, mood, notes or "", created_at.isoformat()])
        except Exception:
            raise
        return Survey(id=survey_id, user_id=user_id, username=username, mood=mood, notes=notes, created_at=created_at)

    def list_surveys(self) -> List[Survey]:
        items: List[Survey] = []
        if not os.path.exists(SURVEYS_CSV):
            return items
        with open(SURVEYS_CSV, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    sid = int(row.get("id", 0))
                    user_id = int(row.get("user_id", 0))
                    mood = int(row.get("mood", 0))
                    notes = row.get("notes") or None
                    created_at = datetime.fromisoformat(row.get("created_at")) if row.get("created_at") else datetime.now()
                    items.append(Survey(id=sid, user_id=user_id, username=row.get("username"), mood=mood, notes=notes, created_at=created_at))
                except Exception:
                    continue
        return items

    def get_survey(self, survey_id: int) -> Optional[Survey]:
        if not os.path.exists(SURVEYS_CSV):
            return None
        with open(SURVEYS_CSV, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    sid = int(row.get("id", 0))
                    if sid == survey_id:
                        user_id = int(row.get("user_id", 0))
                        mood = int(row.get("mood", 0))
                        notes = row.get("notes") or None
                        created_at = datetime.fromisoformat(row.get("created_at")) if row.get("created_at") else datetime.now()
                        return Survey(id=sid, user_id=user_id, username=row.get("username"), mood=mood, notes=notes, created_at=created_at)
                except Exception:
                    continue
        return None

    def update_survey(self, survey_id: int, mood: Optional[int] = None, notes: Optional[str] = None) -> Optional[Survey]:
        if not os.path.exists(SURVEYS_CSV):
            return None
        updated = None
        rows = []
        try:
            with open(SURVEYS_CSV, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        sid = int(row.get("id", 0))
                    except Exception:
                        rows.append(row)
                        continue
                    if sid == survey_id:
                        if mood is not None:
                            row["mood"] = str(mood)
                        if notes is not None:
                            row["notes"] = notes
                        updated = Survey(id=sid, user_id=int(row.get("user_id", 0)), username=row.get("username"), mood=int(row.get("mood", 0)), notes=row.get("notes") or None, created_at=datetime.fromisoformat(row.get("created_at")) if row.get("created_at") else datetime.now())
                    rows.append(row)
        except Exception:
            return None

        try:
            with open(SURVEYS_CSV, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["id", "user_id", "username", "mood", "notes", "created_at"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in rows:
                    writer.writerow({k: r.get(k, "") for k in fieldnames})
        except Exception:
            return None

        return updated

    def delete_survey(self, survey_id: int) -> bool:
        if not os.path.exists(SURVEYS_CSV):
            return False
        deleted = False
        rows = []
        try:
            with open(SURVEYS_CSV, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        sid = int(row.get("id", 0))
                    except Exception:
                        rows.append(row)
                        continue
                    if sid == survey_id:
                        deleted = True
                        continue
                    rows.append(row)
        except Exception:
            return False

        try:
            with open(SURVEYS_CSV, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["id", "user_id", "username", "mood", "notes", "created_at"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in rows:
                    writer.writerow({k: r.get(k, "") for k in fieldnames})
        except Exception:
            return False

        return deleted


# Instancia global de encuestas (CSV-backed)
survey_db = SurveyDatabase()