import sqlite3
from contextlib import closing
import pytest
import db

@pytest.fixture
def p(tmp_path):
    path = str(tmp_path / "t.db"); db.init_db(path); return path

def test_idem(p): assert db.get_or_create_user(1, "a", p) == db.get_or_create_user(1, "a", p)
def test_upd(p):
    db.get_or_create_user(1, "a", p); db.get_or_create_user(1, "b", p)
    with closing(sqlite3.connect(p)) as c: assert c.execute("SELECT username FROM users WHERE telegram_id=1").fetchone()[0] == "b"
def test_board(p):
    u = db.get_or_create_user(1, "a", p); db.insert_game(u, 10, 5000, True, p); db.insert_game(u, 20, 3000, True, p)
    b = db.get_leaderboard(10, p); assert b[0]["best_time"] == 3000 and b[0]["wins"] == 2
def test_stats(p):
    u = db.get_or_create_user(1, "a", p); db.insert_game(u, 10, 5000, True, p); db.insert_game(u, 20, 3000, False, p)
    s = db.get_user_stats(1, p); assert s["total_games"] == 2 and s["wins"] == 1
def test_wins_less(p):
    u = db.get_or_create_user(1, "a", p)
    db.insert_game(u, 10, 5000, True, p); db.insert_game(u, 20, 3000, False, p); db.insert_game(u, 30, 4000, False, p)
    s = db.get_user_stats(1, p); assert s["total_games"] == 3 and s["wins"] == 1
def test_inject(p):
    db.get_or_create_user(1, "'; DROP TABLE users;--", p)
    with closing(sqlite3.connect(p)) as c: assert len(c.execute("SELECT * FROM users").fetchall()) == 1
