# Healthcare Chatbot - Authentication & User Management

## Overview
This healthcare chatbot now includes a complete user authentication and management system. Users must register and login to access the chatbot, and each user can only view their own chat history.

## Key Features

### 1. **User Registration**
- Users create an account with:
  - Username (unique)
  - Email (unique)
  - Password (minimum 6 characters)
  - Gender (optional)
  - Age (optional)
- Password strength indicator
- Password confirmation validation

### 2. **User Login**
- Email-based login
- Password verification
- Session management

### 3. **User Profile Data**
- Username
- Email
- Password (hashed with Werkzeug security)
- Gender
- Age
- Account creation timestamp

### 4. **Chat History Privacy**
- Each user's chat history is stored in a database with their user_id
- Users can only view their own conversations
- History is automatically filtered by logged-in user

### 5. **User Authentication**
- All routes except `/login` and `/register` require authentication
- Users are redirected to login page if not authenticated
- Session-based authentication using Flask-Login

## Database Structure

### Users Table
```sqlite
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    gender TEXT,
    age INTEGER,
    created_at TEXT
)
```

### Interactions Table (Chat History)
```sqlite
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_text TEXT,
    bot_text TEXT,
    timestamp TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

The requirements now include:
- Flask==2.2.5
- Flask-Login==0.6.2
- Werkzeug==2.2.2

### 2. Run the Application
```bash
python app.py
```

The app will automatically initialize the database on first run.

## File Structure

### Backend Files
- **app.py** - Main Flask application with all routes and authentication logic
  - `/login` - Login route (GET/POST)
  - `/register` - Registration route (GET/POST)
  - `/logout` - Logout route
  - `/` - Main chat interface (protected)
  - `/chat` - Chat message endpoint (protected)
  - `/history` - Get user's chat history (protected)
  - `/history-page` - View chat history page (protected)
  - `/diagnose` - Diagnose symptoms (protected)

### Frontend Files
- **login.html** - Login page with email and password fields
- **register.html** - Registration form with all user information
- **index.html** - Main chat interface (updated with user info and logout)
- **history.html** - User's personal chat history (updated with privacy notice)

### Database
- **chat_history.db** - SQLite database with users and interactions

## Usage Flow

### New User Flow
1. User visits the application
2. Redirected to `/login` page
3. Clicks "Register" or goes to `/register`
4. Fills out registration form (username, email, password, gender, age)
5. Submits registration
6. Automatically logged in
7. Redirected to main chat page

### Returning User Flow
1. User visits the application
2. Redirected to `/login` page
3. Enters email and password
4. Logged in
5. Redirected to main chat page
6. Can view only their own chat history

### Chat & History
1. User types messages in chat
2. Each conversation is saved with user_id
3. User can click "History" to see their conversations
4. History page shows:
   - Total conversation count
   - All user's previous conversations
   - User/Bot messages with timestamps
5. Users can only see their own history (enforced server-side)

## Security Features

1. **Password Security**
   - Passwords are hashed using Werkzeug's `generate_password_hash()`
   - Never stored in plain text
   - Verified using `check_password_hash()`

2. **Session Management**
   - Flask-Login manages user sessions
   - Session timeout can be configured
   - Login required decorator on protected routes

3. **Database Constraints**
   - Unique username constraint
   - Unique email constraint
   - Foreign key relationships with cascade delete

4. **User Isolation**
   - Server-side filtering of chat history by user_id
   - User cannot access other users' conversations

## Configuration

### Secret Key
In `app.py`, change the secret key for production:
```python
app.secret_key = "your-secret-key-change-this-in-production"
```

### Host and Port
Edit the last line of app.py to configure:
```python
app.run(debug=True, host="0.0.0.0", port=5000)
```

## Testing Accounts

### Creating Test Accounts
1. Go to `/register`
2. Create account with:
   - Username: testuser
   - Email: test@example.com
   - Password: password123
   - Age: 25
   - Gender: Male

3. Create another account with different credentials to test history isolation

## API Endpoints

### Authentication Routes
- `POST /login` - Login user
  - Body: `{email: string, password: string}`
  - Returns: `{success: bool, message: string, redirect: string}`

- `POST /register` - Register new user
  - Body: `{username: string, email: string, password: string, confirm_password: string, gender: string, age: int}`
  - Returns: `{success: bool, message: string, redirect: string}`

- `GET /logout` - Logout user
  - Clears session and redirects to login

### Protected Routes (Require Login)
- `GET /` - Main chat page
- `POST /chat` - Send message
- `GET /history` - Get user's chat history (JSON)
- `GET /history-page` - View chat history (HTML)
- `POST /diagnose` - Get symptom diagnosis

## Troubleshooting

### Issue: Database errors
**Solution:** Delete `chat_history.db` and restart the app. It will recreate the database.

### Issue: Can't login after register
**Solution:** Ensure Flask-Login is installed: `pip install Flask-Login`

### Issue: Seeing other users' history
**Solution:** This should not happen due to server-side filtering. Check that the `@login_required` decorator is present.

### Issue: Password not working
**Solution:** Ensure password is at least 6 characters and passwords match during registration.

## Future Enhancements

1. **Email Verification** - Verify email before allowing login
2. **Password Reset** - Implement forgot password functionality
3. **User Profile Page** - Allow users to update their information
4. **Two-Factor Authentication** - Add extra security layer
5. **Admin Dashboard** - Manage users and view statistics
6. **Export History** - Allow users to export their chat history

## Support

For issues or questions, refer to the Flask and Flask-Login documentation:
- Flask: https://flask.palletsprojects.com/
- Flask-Login: https://flask-login.readthedocs.io/
