from flask import Flask, render_template, request, redirect, url_for, jsonify
from music_module import music_bp  # Import the Music Player Blueprint
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.register_blueprint(music_bp)  # Register the music player module

DB_NAME = 'calories.db'

# ---------------- DATABASE SETUP ----------------
def init_db():
    """Initialize the SQLite database if it doesn't exist."""
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
 
        # Table for calorie entries
        c.execute('''
            CREATE TABLE entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal TEXT NOT NULL,
                calories INTEGER NOT NULL,
                meal_type TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')

        # Table for daily goals
        c.execute('''
            CREATE TABLE goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal INTEGER NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

# Initialize DB on app startup
init_db()


# ---------------- HOME PAGE ----------------
@app.route('/home')
def home():
    """Landing page with module selection."""
    return render_template('home.html')


# ---------------- MAIN PAGE (Calorie Counter) ----------------
@app.route('/', methods=['GET', 'POST'])
def index():
    """Main Calorie Counter Page."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Add new food entry
    if request.method == 'POST':
        meal = request.form['meal']
        calories = int(request.form['calories'])
        meal_type = request.form['meal_type']
        entry_date = request.form.get('entry_date') or datetime.now().strftime('%Y-%m-%d')

        c.execute('INSERT INTO entries (meal, calories, meal_type, date) VALUES (?, ?, ?, ?)',
                  (meal, calories, meal_type, entry_date))
        conn.commit()

    # Selected date (default = today)
    selected_date = request.args.get('date') or datetime.now().strftime('%Y-%m-%d')
    c.execute('SELECT * FROM entries WHERE date=?', (selected_date,))
    entries = c.fetchall()

    # Total calories today
    c.execute('SELECT SUM(calories) FROM entries WHERE date=?', (selected_date,))
    total_today = c.fetchone()[0] or 0

    # Goal progress
    c.execute('SELECT goal FROM goals ORDER BY id DESC LIMIT 1')
    goal_row = c.fetchone()
    goal = goal_row[0] if goal_row else 0
    goal_progress = round((total_today / goal) * 100, 2) if goal else 0

    # Daily summary for chart
    c.execute('SELECT date, SUM(calories) FROM entries GROUP BY date ORDER BY date DESC')
    daily_summary = c.fetchall()

    conn.close()

    return render_template('index.html',
                           entries=entries,
                           total_today=total_today,
                           goal=goal,
                           goal_progress=goal_progress,
                           daily_summary=daily_summary,
                           selected_date=selected_date)


# ---------------- SET GOAL ----------------
@app.route('/set_goal', methods=['POST'])
def set_goal():
    """Save a new daily calorie goal."""
    goal = int(request.form['goal'])
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO goals (goal) VALUES (?)', (goal,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# ---------------- EDIT ENTRY ----------------
@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    """Edit an existing meal entry."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == 'POST':
        meal = request.form['meal']
        calories = int(request.form['calories'])
        meal_type = request.form['meal_type']
        entry_date = request.form['entry_date']

        c.execute('UPDATE entries SET meal=?, calories=?, meal_type=?, date=? WHERE id=?',
                  (meal, calories, meal_type, entry_date, entry_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        c.execute('SELECT * FROM entries WHERE id=?', (entry_id,))
        entry = c.fetchone()
        conn.close()
        return render_template('edit.html', entry=entry)


# ---------------- DELETE ENTRY ----------------
@app.route('/delete/<int:entry_id>')
def delete_entry(entry_id):
    """Delete a specific meal entry."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM entries WHERE id=?', (entry_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# ---------------- CHART DATA ----------------
@app.route('/chart-data')
def chart_data():
    """Return JSON data for calorie chart for 7 consecutive days."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    start_date_str = request.args.get('start_date')
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = datetime.now().date()

    end_date = start_date + timedelta(days=6)

    c.execute('''
        SELECT date, SUM(calories)
        FROM entries
        WHERE date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
    ''', (start_date, end_date))
    rows = c.fetchall()
    conn.close()

    # Prepare JSON data
    dates = [(start_date + timedelta(days=i)) for i in range(7)]
    date_labels = [d.strftime('%d %b') for d in dates]
    data_dict = {row[0]: row[1] for row in rows}
    calories_values = [data_dict.get(d.strftime('%Y-%m-%d'), 0) for d in dates]

    return jsonify({'dates': date_labels, 'calories': calories_values})


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    print("\n✅ Flask app running with:")
    print("   ➤ Calorie Counter at http://127.0.0.1:5000/")
    print("   ➤ Music Player at http://127.0.0.1:5000/music")
    print("   ➤ Home Page at http://127.0.0.1:5000/home\n")

    app.run(debug=True)
