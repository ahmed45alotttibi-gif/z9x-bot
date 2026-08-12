import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "z9x.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            channel_id INTEGER PRIMARY KEY,
            guild_id INTEGER,
            opener_id INTEGER,
            claimed_by INTEGER,
            category TEXT,
            ticket_number INTEGER,
            status TEXT DEFAULT 'open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ticket_counter (
            guild_id INTEGER PRIMARY KEY,
            count INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS levels (
            guild_id INTEGER,
            user_id INTEGER,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 0,
            last_message_ts REAL DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            moderator_id INTEGER,
            reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            channel_id INTEGER,
            staff_id INTEGER,
            rater_id INTEGER,
            stars INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def next_ticket_number(guild_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT count FROM ticket_counter WHERE guild_id = ?", (guild_id,))
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO ticket_counter (guild_id, count) VALUES (?, 1)", (guild_id,))
        conn.commit()
        conn.close()
        return 1
    new_count = row["count"] + 1
    cur.execute("UPDATE ticket_counter SET count = ? WHERE guild_id = ?", (new_count, guild_id))
    conn.commit()
    conn.close()
    return new_count
