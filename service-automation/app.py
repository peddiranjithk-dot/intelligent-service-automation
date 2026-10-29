"""Intelligent Service Automation - simple base project (Flask + SQLite + scikit-learn)."""
import os
import sqlite3
from collections import Counter
from datetime import datetime, timezone

from flask import Flask, g, jsonify, render_template, request

from automation import process_request

app = Flask(__name__)
app.config["DB_PATH"] = os.environ.get("DB_PATH", "service_requests.db")
STATUSES = {"assigned", "in_progress", "resolved", "auto_resolved"}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DB_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    with sqlite3.connect(app.config["DB_PATH"]) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester TEXT, title TEXT NOT NULL, description TEXT DEFAULT '',
            intent TEXT, confidence REAL, team TEXT, priority TEXT, sla_hours INTEGER,
            status TEXT, auto_reply TEXT, created_at TEXT)""")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/requests")
def create_request():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify(error="title is required"), 400
    desc = (data.get("description") or "").strip()
    result = process_request(title, desc)
    db = get_db()
    cur = db.execute(
        """INSERT INTO requests (requester,title,description,intent,confidence,team,
           priority,sla_hours,status,auto_reply,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (data.get("requester", "anonymous"), title, desc, result["intent"],
         result["confidence"], result["team"], result["priority"], result["sla_hours"],
         result["status"], result["auto_reply"],
         datetime.now(timezone.utc).isoformat(timespec="seconds")))
    db.commit()
    row = db.execute("SELECT * FROM requests WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201


@app.get("/api/requests")
def list_requests():
    q, params = "SELECT * FROM requests", []
    if request.args.get("status"):
        q += " WHERE status=?"
        params.append(request.args["status"])
    q += " ORDER BY priority, created_at DESC"
    return jsonify([dict(r) for r in get_db().execute(q, params)])


@app.patch("/api/requests/<int:rid>")
def update_request(rid):
    status = (request.get_json(silent=True) or {}).get("status")
    if status not in STATUSES:
        return jsonify(error=f"status must be one of {sorted(STATUSES)}"), 400
    db = get_db()
    if not db.execute("SELECT 1 FROM requests WHERE id=?", (rid,)).fetchone():
        return jsonify(error="not found"), 404
    db.execute("UPDATE requests SET status=? WHERE id=?", (status, rid))
    db.commit()
    return jsonify(dict(db.execute("SELECT * FROM requests WHERE id=?", (rid,)).fetchone()))


@app.get("/api/stats")
def stats():
    rows = get_db().execute("SELECT * FROM requests").fetchall()
    total = len(rows)
    auto = sum(r["status"] == "auto_resolved" for r in rows)
    return jsonify(
        total=total, auto_resolved=auto,
        automation_rate=round(auto / total * 100, 1) if total else 0,
        by_intent=dict(Counter(r["intent"] for r in rows)),
        by_team=dict(Counter(r["team"] for r in rows)),
        by_priority=dict(Counter(r["priority"] for r in rows)))


init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
