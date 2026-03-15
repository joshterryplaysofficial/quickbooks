"""SQLite database for token storage and audit logging."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "quickbooks.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            access_token TEXT NOT NULL,
            refresh_token TEXT NOT NULL,
            realm_id TEXT NOT NULL,
            access_token_expiry TEXT NOT NULL,
            refresh_token_expiry TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            action TEXT NOT NULL,
            entity_type TEXT,
            entity_id TEXT,
            details TEXT
        );
    """)
    conn.commit()
    conn.close()


def save_tokens(
    access_token: str,
    refresh_token: str,
    realm_id: str,
    access_token_expiry: str,
    refresh_token_expiry: str,
):
    """Save or update OAuth tokens."""
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO tokens (id, access_token, refresh_token, realm_id,
                           access_token_expiry, refresh_token_expiry, updated_at)
        VALUES (1, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            access_token = excluded.access_token,
            refresh_token = excluded.refresh_token,
            realm_id = excluded.realm_id,
            access_token_expiry = excluded.access_token_expiry,
            refresh_token_expiry = excluded.refresh_token_expiry,
            updated_at = excluded.updated_at
        """,
        (access_token, refresh_token, realm_id,
         access_token_expiry, refresh_token_expiry, now),
    )
    conn.commit()
    conn.close()


def load_tokens() -> dict | None:
    """Load stored tokens. Returns dict or None if no tokens stored."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM tokens WHERE id = 1").fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def log_action(
    tool_name: str,
    action: str,
    entity_type: str = None,
    entity_id: str = None,
    details: str = None,
):
    """Log an action to the audit trail."""
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO audit_log (timestamp, tool_name, action, entity_type, entity_id, details)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (now, tool_name, action, entity_type, entity_id, details),
    )
    conn.commit()
    conn.close()


def get_audit_log(limit: int = 50) -> list[dict]:
    """Get recent audit log entries."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
    # Verify tables exist
    conn = _get_conn()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    print("Tables:", [t["name"] for t in tables])
    conn.close()
