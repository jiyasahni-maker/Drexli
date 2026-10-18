import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "drexli.db"

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, organization TEXT, opportunity_type TEXT, deadline TEXT,
            application_url TEXT, evidence_status TEXT, fit_score INTEGER,
            status TEXT DEFAULT 'Saved', details_json TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")

def save_opportunity(opportunity, verification, fit):
    with _connect() as conn:
        conn.execute("""INSERT INTO opportunities
            (title, organization, opportunity_type, deadline, application_url, evidence_status, fit_score, status, details_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Saved', ?)""",
            (opportunity.get("title"), opportunity.get("organization"), opportunity.get("type"), opportunity.get("deadline"), opportunity.get("application_url"), verification.get("status"), fit.get("score"), json.dumps({"opportunity": opportunity, "verification": verification, "fit": fit})))

def list_opportunities():
    with _connect() as conn:
        rows = conn.execute("SELECT id, title, organization, opportunity_type, deadline, application_url, evidence_status, fit_score, status FROM opportunities ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]

def update_status(item_id, status):
    allowed = {"Saved", "Planning to apply", "Applied", "Rejected", "Accepted", "Expired"}
    if status not in allowed:
        raise ValueError("Unsupported status")
    with _connect() as conn:
        conn.execute("UPDATE opportunities SET status = ? WHERE id = ?", (status, item_id))
