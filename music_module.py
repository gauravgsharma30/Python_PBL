from flask import Blueprint, render_template, request, redirect, url_for
from flask import jsonify
import os
import sqlite3

# Blueprint setup
music_bp = Blueprint('music', __name__, template_folder='templates', static_folder='static')

DB_NAME = "music.db"


# ---------------- DATABASE SETUP ----------------
def init_music_db():
    """Create playlist database if not already present"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Table for playlists
    c.execute('''
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Table for songs inside playlists
    c.execute('''
        CREATE TABLE IF NOT EXISTS playlist_songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER,
            song_name TEXT,
            FOREIGN KEY (playlist_id) REFERENCES playlists(id)
        )
    ''')

    conn.commit()
    conn.close()

init_music_db()


# ---------------- MUSIC PLAYER MAIN PAGE ----------------
@music_bp.route('/music')
def music_player():
    """Main music player showing all available songs."""
    songs_dir = os.path.join(music_bp.static_folder, 'songs')

    if not os.path.exists(songs_dir):
        os.makedirs(songs_dir)

    songs = [song for song in os.listdir(songs_dir) if song.endswith('.mp3')]

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM playlists')
    playlists = c.fetchall()
    conn.close()

    return render_template('music.html', songs=songs, playlists=playlists)


# ---------------- CREATE NEW PLAYLIST ----------------
@music_bp.route('/create_playlist', methods=['POST'])
def create_playlist():
    """Add a new playlist."""
    name = request.form['playlist_name'].strip()

    if not name:
        return redirect(url_for('music.music_player'))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO playlists (name) VALUES (?)', (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        # Playlist name already exists
        pass
    conn.close()

    return redirect(url_for('music.music_player'))


# ---------------- ADD SONG TO PLAYLIST ----------------
@music_bp.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    """Add selected song to chosen playlist (no duplicates)."""
    playlist_id = request.form['playlist_id']
    song_name = request.form['song_name']

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Check if already exists
    c.execute('SELECT 1 FROM playlist_songs WHERE playlist_id=? AND song_name=?', (playlist_id, song_name))
    if not c.fetchone():
        c.execute('INSERT INTO playlist_songs (playlist_id, song_name) VALUES (?, ?)', (playlist_id, song_name))
        conn.commit()

    conn.close()
    return redirect(url_for('music.music_player'))



# ---------------- VIEW PLAYLIST SONGS ----------------
@music_bp.route('/playlist/<int:playlist_id>')
def view_playlist(playlist_id):
    """View all songs in a selected playlist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('SELECT name FROM playlists WHERE id=?', (playlist_id,))
    playlist_name = c.fetchone()[0]

    c.execute('SELECT song_name FROM playlist_songs WHERE playlist_id=?', (playlist_id,))
    songs = [row[0] for row in c.fetchall()]

    conn.close()

    songs_dir = os.path.join(music_bp.static_folder, 'songs')
    all_songs = [song for song in os.listdir(songs_dir) if song.endswith('.mp3')]

    return render_template('playlists.html', playlist_name=playlist_name, songs=songs, all_songs=all_songs)
# ---------------- DELETE PLAYLIST ----------------
@music_bp.route('/delete_playlist/<int:playlist_id>', methods=['POST'])
def delete_playlist(playlist_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM playlists WHERE id=?', (playlist_id,))
    c.execute('DELETE FROM playlist_songs WHERE playlist_id=?', (playlist_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('music.music_player'))


# ---------------- REMOVE SONG FROM PLAYLIST ----------------
@music_bp.route('/remove_song', methods=['POST'])
def remove_song():
    """Remove a specific song from a playlist."""
    playlist_id = request.form['playlist_id']
    song_name = request.form['song_name']

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM playlist_songs WHERE playlist_id=? AND song_name=?', (playlist_id, song_name))
    conn.commit()
    conn.close()

    return redirect(url_for('music.music_player'))
# ---------------- FETCH SONGS IN PLAYLIST ----------------
@music_bp.route('/get_playlist_songs/<int:playlist_id>')
def get_playlist_songs(playlist_id):
    """Return songs in a playlist (for AJAX)"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT song_name FROM playlist_songs WHERE playlist_id=?', (playlist_id,))
    songs = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(songs)
