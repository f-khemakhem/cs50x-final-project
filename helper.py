import sqlite3
from functools import wraps
from flask import session, redirect, flash
import secrets


class Database:
    def execute(self, query, *args):
        conn = sqlite3.connect("project.db")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            cur = conn.execute(query, args)

            # 1. SELECT: traja3 liste dicts
            if query.lstrip().upper().startswith("SELECT"):
                return [dict(row) for row in cur.fetchall()]

            # 2. Ay 7aja okhra: sajjel el taghyir
            conn.commit()

            # 3. INSERT: traja3 id mta3 el ligne el jdida
            if query.lstrip().upper().startswith("INSERT"):
                return cur.lastrowid

            # 4. UPDATE / DELETE: traja3 3dad el lignes elli tbaddlou
            return cur.rowcount
        finally:
            conn.close()


db = Database()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function

def doctor_can_access(patient_id):
    rows = db.execute(
    "SELECT 1 FROM doctor_patient WHERE doctor_id = ? AND patient_id = ?",
    session["user_id"], patient_id,
    )
    return len(rows) == 1

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("role") != role:
                flash("Access denied")
                return redirect("/doctor" if session.get("role") == "doctor" else "/patient")
            return f(*args, **kwargs)
        return decorated_function
    return decorator



CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def generate_share_code():
    while True:
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))
        if not db.execute("SELECT 1 FROM patients WHERE share_code = ?", code):
            return code