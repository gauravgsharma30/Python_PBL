import sqlite3
from datetime import date

def init_db():
    conn = sqlite3.connect("calorie_data.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal TEXT NOT NULL,
            calories INTEGER NOT NULL,
            meal_type TEXT,
            entry_date DATE DEFAULT CURRENT_DATE
        )
    """)
    conn.commit()
    conn.close()

def add_entry(meal, calories, meal_type):
    conn = sqlite3.connect("calorie_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO entries (meal, calories, meal_type, entry_date) VALUES (?, ?, ?, ?)",
              (meal, calories, meal_type, date.today()))
    conn.commit()
    conn.close()

def get_entries_by_date(entry_date):
    conn = sqlite3.connect("calorie_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM entries WHERE entry_date = ? ORDER BY id DESC", (entry_date,))
    data = c.fetchall()
    conn.close()
    return data

def total_calories_by_date(entry_date):
    conn = sqlite3.connect("calorie_data.db")
    c = conn.cursor()
    c.execute("SELECT SUM(calories) FROM entries WHERE entry_date = ?", (entry_date,))
    result = c.fetchone()[0]
    conn.close()
    return result or 0

def delete_entry(entry_id):
    conn = sqlite3.connect("calorie_data.db")
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def get_entry_by_id(entry_id):
    conn = sqlite3.connect("calorie_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    result = c.fetchone()
    conn.close()
    return result

def update_entry(entry_id, meal, calories, meal_type):
    conn = sqlite3.connect("calorie_data.db")
    c = conn.cursor()
    c.execute("UPDATE entries SET meal = ?, calories = ?, meal_type = ? WHERE id = ?",
              (meal, calories, meal_type, entry_id))
    conn.commit()
    conn.close()

def get_daily_summary():
    conn = sqlite3.connect("calorie_data.db")
    c = conn.cursor()
    c.execute("SELECT entry_date, SUM(calories) FROM entries GROUP BY entry_date ORDER BY entry_date DESC")
    summary = c.fetchall()
    conn.close()
    return summary

def get_last_7_days_data():
    conn = sqlite3.connect("calorie_data.db")
    c = conn.cursor()
    c.execute("""
        SELECT entry_date, SUM(calories)
        FROM entries
        GROUP BY entry_date
        ORDER BY entry_date DESC
        LIMIT 7
    """)
    data = c.fetchall()
    conn.close()
    return data[::-1]
