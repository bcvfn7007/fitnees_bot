import sqlite3
import time

conn = sqlite3.connect("fitness.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    access_until INTEGER
)
""")
conn.commit()

TRIAL_DAYS = 2
SUB_DAYS = 30


def give_trial(user_id: int):
    now = int(time.time())
    trial_until = now + TRIAL_DAYS * 86400

    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id, access_until)
    VALUES (?, ?)
    """, (user_id, trial_until))
    conn.commit()


def give_subscription(user_id: int):
    now = int(time.time())

    cursor.execute(
        "SELECT access_until FROM users WHERE user_id=?",
        (user_id,)
    )
    row = cursor.fetchone()

    if row and row[0] > now:
        new_until = row[0] + SUB_DAYS * 86400
    else:
        new_until = now + SUB_DAYS * 86400

    cursor.execute("""
    INSERT OR REPLACE INTO users (user_id, access_until)
    VALUES (?, ?)
    """, (user_id, new_until))
    conn.commit()


def has_access(user_id: int) -> bool:
    cursor.execute(
        "SELECT access_until FROM users WHERE user_id=?",
        (user_id,)
    )
    row = cursor.fetchone()
    return bool(row and row[0] > int(time.time()))
