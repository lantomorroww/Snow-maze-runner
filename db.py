"""SQLite-хранилище. Сырой SQL, ?-плейсхолдеры, closing."""
import os
import sqlite3
from contextlib import closing

DEFAULT_DB_PATH = os.environ.get("DB_PATH", "snow_maze.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY, telegram_id INTEGER UNIQUE NOT NULL,
  username TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS games (
  id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id),
  moves INTEGER NOT NULL, time_ms INTEGER NOT NULL, won INTEGER NOT NULL DEFAULT 0,
  played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_games_user ON games(user_id);
CREATE INDEX IF NOT EXISTS idx_games_won ON games(won, time_ms);
"""


def _connect(p=None):
    c = sqlite3.connect(p or DEFAULT_DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db(p=None):
    with closing(_connect(p)) as c, c:
        c.executescript(SCHEMA)


def get_or_create_user(tid, username=None, p=None):
    with closing(_connect(p)) as c, c:
        c.execute("INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)", (tid, username))
        if username:
            c.execute("UPDATE users SET username=? WHERE telegram_id=?", (username, tid))
        return c.execute("SELECT id FROM users WHERE telegram_id=?", (tid,)).fetchone()["id"]


def insert_game(uid, moves, time_ms, won, p=None):
    with closing(_connect(p)) as c, c:
        c.execute("INSERT INTO games (user_id, moves, time_ms, won) VALUES (?,?,?,?)",
                  (uid, moves, time_ms, 1 if won else 0))


def get_leaderboard(limit=10, p=None):
    with closing(_connect(p)) as c, c:
        rows = c.execute("""
            SELECT u.username, MIN(g.time_ms) AS best_time, COUNT(*) AS wins
            FROM games g JOIN users u ON u.id=g.user_id WHERE g.won=1
            GROUP BY u.id ORDER BY best_time ASC LIMIT ?""", (limit,)).fetchall()
        return [dict(r) for r in rows]


def get_user_stats(tid, p=None):
    with closing(_connect(p)) as c, c:
        r = c.execute("""
            SELECT COUNT(g.id) AS total_games, COALESCE(SUM(g.won),0) AS wins,
                   COALESCE(AVG(g.moves),0) AS avg_moves,
                   COALESCE(MIN(CASE WHEN g.won=1 THEN g.time_ms END),0) AS best_time_ms
            FROM games g JOIN users u ON u.id=g.user_id WHERE u.telegram_id=?""",
            (tid,)).fetchone()
        return dict(r) if r else {}
