import sqlite3
import pandas as pd

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = sqlite3.connect('ru_active.db')
    return conn

def create_tables():
    """Create tables in the SQLite database."""
    conn = create_connection()
    c = conn.cursor()
    
    # Create Users Table with username column
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            height REAL,
            weight REAL,
            age INTEGER,
            activity_level TEXT,
            goal TEXT
        )
    ''')
    
    # Create Workouts Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            exercise TEXT,
            weight REAL,
            reps INTEGER,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create Credentials Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')

    # Create Badges Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT
        )
    ''')

    # Create User Badges Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            user_id INTEGER,
            badge_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (badge_id) REFERENCES badges (id)
        )
    ''')

    # Create Friends Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            user_id INTEGER,
            friend_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (friend_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username, password):
    """Add a new user to the credentials table."""
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO credentials (username, password) VALUES (?, ?)', (username, password))
        c.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def verify_user(username, password):
    """Verify user credentials."""
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM credentials WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def get_user_profile(username):
    """Get user profile data."""
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT id, height, weight, age, activity_level, goal FROM users WHERE username = ?', (username,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        return {
            'id': user_data[0],  # Include the user ID
            'height': user_data[1],
            'weight': user_data[2],
            'age': user_data[3],
            'activity_level': user_data[4],
            'goal': user_data[5]
        }
    return None

def update_user_profile(username, height, weight, age, activity_level, goal):
    """Update user profile data."""
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE users
        SET height = ?, weight = ?, age = ?, activity_level = ?, goal = ?
        WHERE username = ?
    ''', (height, weight, age, activity_level, goal, username))
    conn.commit()
    conn.close()

def add_workout_progress(username, exercise, weight, reps, date):
    """Add workout progress for a user."""
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_id = c.fetchone()[0]
    c.execute('INSERT INTO workouts (user_id, exercise, weight, reps, date) VALUES (?, ?, ?, ?, ?)',
              (user_id, exercise, weight, reps, date))
    conn.commit()
    conn.close()

def get_user_progress(username):
    """Get workout progress for a user."""
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_id = c.fetchone()[0]
    c.execute('SELECT exercise, weight, reps, date FROM workouts WHERE user_id = ?', (user_id,))
    progress_data = c.fetchall()
    conn.close()
    if progress_data:
        return pd.DataFrame(progress_data, columns=['exercise', 'weight', 'reps', 'date'])
    return None

def award_badge(user_id, badge_name):
    """Award a badge to a user."""
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM badges WHERE name = ?', (badge_name,))
    badge_id = c.fetchone()
    if badge_id:
        c.execute('INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)', (user_id, badge_id[0]))
        conn.commit()
    conn.close()

def check_and_award_badges(user_id):
    """Check user achievements and award badges."""
    conn = create_connection()
    c = conn.cursor()
    # Example: Award a badge for completing 10 workouts
    c.execute('SELECT COUNT(*) FROM workouts WHERE user_id = ?', (user_id,))
    workout_count = c.fetchone()[0]
    if workout_count >= 10:
        award_badge(user_id, "10 Workouts Completed")
    conn.close()

def add_friend(user_id, friend_username):
    """Add a friend for a user."""
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (friend_username,))
    friend_id = c.fetchone()
    if friend_id:
        try:
            c.execute('INSERT INTO friends (user_id, friend_id) VALUES (?, ?)', (user_id, friend_id[0]))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    conn.close()
    return False

def get_friends_workout_counts(user_id):
    """Get workout counts for a user's friends."""
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        SELECT u.username, COUNT(w.id) as workout_count
        FROM friends f
        JOIN users u ON f.friend_id = u.id
        LEFT JOIN workouts w ON u.id = w.user_id
        WHERE f.user_id = ?
        GROUP BY u.username
    ''', (user_id,))
    friends_workout_counts = c.fetchall()
    conn.close()
    return friends_workout_counts

def get_user_badges(user_id):
    """Get badges for a user."""
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        SELECT b.name, b.description
        FROM user_badges ub
        JOIN badges b ON ub.badge_id = b.id
        WHERE ub.user_id = ?
    ''', (user_id,))
    badges = c.fetchall()
    conn.close()
    return [{'name': badge[0], 'description': badge[1]} for badge in badges]

def get_leaderboard(user_id):
    """Get leaderboard data for the user and their friends."""
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        SELECT u.username, COUNT(w.id) as workout_count
        FROM users u
        LEFT JOIN workouts w ON u.id = w.user_id
        WHERE u.id = ? OR u.id IN (SELECT friend_id FROM friends WHERE user_id = ?)
        AND w.date >= date('now', '-7 days')
        GROUP BY u.username
        ORDER BY workout_count DESC
    ''', (user_id, user_id))
    leaderboard_data = c.fetchall()
    conn.close()
    return pd.DataFrame(leaderboard_data, columns=['Username', 'Workouts This Week'])

def get_friends(user_id):
    """Get a list of friends for a user."""
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        SELECT u.username
        FROM friends f
        JOIN users u ON f.friend_id = u.id
        WHERE f.user_id = ?
    ''', (user_id,))
    friends = c.fetchall()
    conn.close()
    return [friend[0] for friend in friends]