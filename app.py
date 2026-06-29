from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from response_engine import ResponseEngine
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "your-secret-key-change-this-in-production"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
symptom_path = os.path.join(os.path.dirname(__file__), "symptom.json")
engine = ResponseEngine(kb_path=kb_path, symptom_path=symptom_path)

DB_PATH = os.path.join(os.path.dirname(__file__), "chat_history.db")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'role', 'user') != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

class User(UserMixin):
    def __init__(self, user_id, username, email, role='user'):
        self.id = user_id
        self.username = username
        self.email = email
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, role FROM users WHERE id = ?", (user_id,))
    user_data = cur.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[3] if len(user_data) > 3 else 'user')
    return None

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create users table if needed
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    users_exists = cur.fetchone() is not None

    if not users_exists:
        cur.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            gender TEXT,
            age INTEGER,
            created_at TEXT,
            role TEXT DEFAULT 'user'
        )
        """)
    else:
        cur.execute("PRAGMA table_info(users)")
        users_cols = [row[1] for row in cur.fetchall()]
        if 'role' not in users_cols:
            cur.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")

    # Ensure default admin exists
    cur.execute("SELECT id FROM users WHERE role = 'admin' OR username = 'admin'")
    if not cur.fetchone():
        admin_password = generate_password_hash('D703132')
        cur.execute("INSERT INTO users (username, email, password, gender, age, created_at, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ('admin', 'admin@localhost', admin_password, '', None, datetime.utcnow().isoformat(), 'admin'))

    # Create or migrate interactions table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interactions'")
    interactions_exists = cur.fetchone() is not None

    if interactions_exists:
        cur.execute("PRAGMA table_info(interactions)")
        columns = [row[1] for row in cur.fetchall()]
        if 'user_id' not in columns:
            cur.execute("ALTER TABLE interactions RENAME TO interactions_old")
            cur.execute("""
            CREATE TABLE interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_text TEXT,
                bot_text TEXT,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            cur.execute("INSERT INTO interactions (user_id, user_text, bot_text, timestamp) SELECT 0, user_text, bot_text, timestamp FROM interactions_old")
            cur.execute("DROP TABLE interactions_old")
    else:
        cur.execute("""
        CREATE TABLE interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_text TEXT,
            bot_text TEXT,
            timestamp TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

    conn.commit()
    conn.close()

def save_interaction(user_id, user_text, bot_text):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO interactions (user_id, user_text, bot_text, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, user_text, bot_text, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html", username=current_user.username, role=getattr(current_user, 'role', 'user'))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        
        if not email or not password:
            return jsonify({"success": False, "message": "Email and password required"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, password, role FROM users WHERE email = ?", (email,))
        user_data = cur.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data[3], password):
            user = User(user_data[0], user_data[1], user_data[2], user_data[4] if user_data[4] else 'user')
            login_user(user)
            return jsonify({"success": True, "message": "Login successful", "redirect": url_for("index")})
        else:
            return jsonify({"success": False, "message": "Invalid email or password"}), 401
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        confirm_password = data.get("confirm_password", "").strip()
        gender = data.get("gender", "").strip()
        age = data.get("age")
        
        # Validation
        if not all([username, email, password, confirm_password]):
            return jsonify({"success": False, "message": "All fields required"}), 400
        
        if password != confirm_password:
            return jsonify({"success": False, "message": "Passwords do not match"}), 400
        
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400
        
        try:
            age = int(age) if age else None
        except ValueError:
            return jsonify({"success": False, "message": "Invalid age"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check if user already exists
        cur.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email, username))
        if cur.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "Email or username already exists"}), 400
        
        # Create new user
        hashed_password = generate_password_hash(password)
        try:
            cur.execute("""
            INSERT INTO users (username, email, password, gender, age, created_at, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, email, hashed_password, gender, age, datetime.utcnow().isoformat(), 'user'))
            conn.commit()
            user_id = cur.lastrowid
            conn.close()
            
            user = User(user_id, username, email, 'user')
            login_user(user)
            return jsonify({"success": True, "message": "Registration successful", "redirect": url_for("index")})
        except Exception as e:
            conn.close()
            return jsonify({"success": False, "message": str(e)}), 500

    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/chat", methods=["POST"])
def chat():
    if not current_user.is_authenticated:
        return jsonify({"reply": "Please log in to use chat."}), 401

    data = request.get_json() or {}
    user_text = data.get("message", "")
    lang = data.get("lang", "en")
    bot_text = engine.get_response(user_text, lang=lang)
    save_interaction(current_user.id, user_text, bot_text)
    return jsonify({"reply": bot_text})

@app.route("/history", methods=["GET"])
@login_required
def history():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if getattr(current_user, 'role', 'user') == 'admin':
        cur.execute("""
        SELECT users.username, interactions.user_text, interactions.bot_text, interactions.timestamp
        FROM interactions
        JOIN users ON interactions.user_id = users.id
        ORDER BY interactions.id DESC
        LIMIT 200
        """)
        rows = cur.fetchall()
        conn.close()
        result = [{"username": r[0], "user": r[1], "bot": r[2], "time": r[3]} for r in rows]
    else:
        cur.execute("SELECT user_text, bot_text, timestamp FROM interactions WHERE user_id = ? ORDER BY id DESC LIMIT 50", (current_user.id,))
        rows = cur.fetchall()
        conn.close()
        result = [{"user": r[0], "bot": r[1], "time": r[2]} for r in rows]

    return jsonify(result)


@app.route("/diagnose", methods=["POST"])
@login_required
def diagnose():
    """Explicit symptom diagnosis endpoint.

    Accepts JSON with either:
      - {"message": "..."} (free text)
      - {"symptoms": ["itching", "skin rash"]}

    Returns scored diseases.
    """
    data = request.get_json() or {}
    message = data.get("message")
    symptoms = data.get("symptoms")
    lang = data.get("lang", "en")

    if symptoms:
        msg = " ".join(symptoms)
    elif message:
        msg = message
    else:
        return jsonify({"error": "Provide 'message' or 'symptoms' in JSON."}), 400

    diagnoses = engine.diagnose_symptoms(msg)
    return jsonify({"diagnoses": diagnoses, "lang": lang})


@app.route("/history-page")
@login_required
def history_page():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if getattr(current_user, 'role', 'user') == 'admin':
        cur.execute("""
            SELECT users.username, interactions.user_text, interactions.bot_text, interactions.timestamp
            FROM interactions
            JOIN users ON interactions.user_id = users.id
            ORDER BY interactions.id DESC
            LIMIT 200
        """)
        rows = cur.fetchall()
        conn.close()
        # for admin we provide user name too
        return render_template("history.html", chats=rows, username=current_user.username, is_admin=True)

    cur.execute("""
        SELECT user_text, bot_text, timestamp
        FROM interactions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 50
    """, (current_user.id,))
    rows = cur.fetchall()
    conn.close()

    return render_template("history.html", chats=rows, username=current_user.username, is_admin=False)


@app.route("/admin/users")
@admin_required
def admin_users():
    """Admin dashboard to view all users and their details."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT u.id, u.username, u.email, u.gender, u.age, u.password, u.role, u.created_at,
               COUNT(i.id) as total_interactions
        FROM users u
        LEFT JOIN interactions i ON u.id = i.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)
    
    users = cur.fetchall()
    conn.close()
    
    users_list = []
    for user in users:
        users_list.append({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'gender': user[3],
            'age': user[4],
            'password_hash': user[5],
            'role': user[6],
            'created_at': user[7],
            'total_interactions': user[8]
        })
    
    return render_template("admin_users.html", users=users_list, admin_username=current_user.username)


@app.route("/admin/users/<int:user_id>")
@admin_required
def admin_user_detail(user_id):
    """Admin view of specific user details and interactions."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Get user details
    cur.execute("""
        SELECT id, username, email, gender, age, password, role, created_at
        FROM users
        WHERE id = ?
    """, (user_id,))
    
    user_data = cur.fetchone()
    if not user_data:
        conn.close()
        return redirect(url_for('admin_users'))
    
    # Get user interactions
    cur.execute("""
        SELECT user_text, bot_text, timestamp
        FROM interactions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 100
    """, (user_id,))
    
    interactions = cur.fetchall()
    conn.close()
    
    user_info = {
        'id': user_data[0],
        'username': user_data[1],
        'email': user_data[2],
        'gender': user_data[3],
        'age': user_data[4],
        'password_hash': user_data[5],
        'role': user_data[6],
        'created_at': user_data[7],
        'total_interactions': len(interactions)
    }
    
    interactions_list = [
        {
            'user_text': i[0],
            'bot_text': i[1],
            'timestamp': i[2]
        }
        for i in interactions
    ]
    
    return render_template("admin_user_detail.html", user=user_info, interactions=interactions_list, admin_username=current_user.username)


@app.route("/admin/users/api/list")
@admin_required
def admin_users_api():
    """API endpoint for admin to get all users list as JSON."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT u.id, u.username, u.email, u.gender, u.age, u.password, u.role, u.created_at,
               COUNT(i.id) as total_interactions
        FROM users u
        LEFT JOIN interactions i ON u.id = i.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)
    
    users = cur.fetchall()
    conn.close()
    
    users_list = []
    for user in users:
        users_list.append({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'gender': user[3],
            'age': user[4],
            'password_hash': user[5],
            'role': user[6],
            'created_at': user[7],
            'total_interactions': user[8]
        })
    
    return jsonify(users_list)


@app.route("/admin/create-admin", methods=["POST"])
@admin_required
def create_admin():
    """API endpoint to create a new admin user."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    confirm_password = data.get("confirm_password", "").strip()
    
    # Validation
    if not all([username, email, password, confirm_password]):
        return jsonify({"success": False, "message": "All fields required"}), 400
    
    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400
    
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check if user already exists
    cur.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email, username))
    if cur.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "Email or username already exists"}), 400
    
    # Create new admin
    hashed_password = generate_password_hash(password)
    try:
        cur.execute("""
        INSERT INTO users (username, email, password, gender, age, created_at, role)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, email, hashed_password, '', None, datetime.utcnow().isoformat(), 'admin'))
        conn.commit()
        admin_id = cur.lastrowid
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Admin '{username}' created successfully",
            "admin_id": admin_id
        }), 201
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/admin/change-role/<int:user_id>", methods=["POST"])
@admin_required
def change_user_role(user_id):
    """API endpoint to change a user's role (admin or user)."""
    data = request.get_json() or {}
    new_role = data.get("role", "").strip().lower()
    
    # Validation
    if new_role not in ['admin', 'user']:
        return jsonify({"success": False, "message": "Invalid role. Must be 'admin' or 'user'"}), 400
    
    # Prevent self-demotion
    if user_id == current_user.id and new_role == 'user':
        return jsonify({"success": False, "message": "Cannot demote yourself"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check if user exists
    cur.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
    user_data = cur.fetchone()
    if not user_data:
        conn.close()
        return jsonify({"success": False, "message": "User not found"}), 404
    
    # Update role
    try:
        cur.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"User '{user_data[0]}' role changed to '{new_role}'",
            "old_role": user_data[1],
            "new_role": new_role
        }), 200
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    """API endpoint to delete a user."""
    # Prevent self-deletion
    if user_id == current_user.id:
        return jsonify({"success": False, "message": "Cannot delete yourself"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check if user exists
    cur.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    user_data = cur.fetchone()
    if not user_data:
        conn.close()
        return jsonify({"success": False, "message": "User not found"}), 404
    
    # Delete user and their interactions (cascade)
    try:
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"User '{user_data[0]}' deleted successfully"
        }), 200
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
