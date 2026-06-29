# 🚀 Quick Start Guide - Healthcare Chatbot Authentication

## Installation (5 minutes)

### Step 1: Install Required Packages
```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Flask-Login (authentication)
- Werkzeug (password hashing)

### Step 2: Run the Application
```bash
python app.py
```

You'll see:
```
WARNING in werkzeug: Use a production WSGI server to run the app
 * Running on http://127.0.0.1:5000
```

### Step 3: Open in Browser
Go to: **http://localhost:5000**

You'll be redirected to the login page.

---

## 👤 First Time User - Registration

1. **Click "Register"** or go to **http://localhost:5000/register**

2. **Fill out the form**:
   - **Username**: Choose a unique username (e.g., "john_doe")
   - **Email**: Enter your email (e.g., "john@example.com")
   - **Password**: At least 6 characters (aim for Strong ✅)
   - **Confirm Password**: Re-enter the same password
   - **Gender** (optional): Select from dropdown
   - **Age** (optional): Enter your age

3. **Watch the password strength indicator**:
   - 🔴 Weak - Less than 6 chars
   - 🟡 Fair - 6-10 chars
   - 🔵 Good - Mix of upper, lower, numbers
   - 🟢 Strong - Mix of all including special chars

4. **Click "Register"**

5. **You're automatically logged in!** ✅
   - You'll see the chat screen with your name displayed

---

## 🔑 Returning User - Login

1. **Go to login page**: http://localhost:5000/login

2. **Enter your credentials**:
   - Email: (the email you registered with)
   - Password: (your password)

3. **Click "Login"**

4. **Start chatting!** 💬

---

## 💬 Using the Chat Interface

### Sending Messages
1. Type your symptoms or question in the text box
2. Press **Enter** or click **Send**
3. Your message appears in blue
4. Bot response appears in green

### Viewing History
1. Click **"📜 History"** button (top right)
2. See all your previous conversations
3. Each conversation shows:
   - Your message (blue)
   - Bot's response (green)
   - Timestamp

### Logging Out
1. Click **"🚪 Logout"** button (top right)
2. You'll be redirected to the login page
3. Your chat history is safe and will be there when you log back in

---

## 🔒 Privacy & Security

✅ **Your History is Private**
- Only you can see your conversations
- Other users cannot see your messages
- Passwords are encrypted (never stored as plain text)

✅ **Account Security**
- Each email can only be registered once
- Each username can only be registered once
- Passwords must be at least 6 characters

---

## 📊 Test Scenarios

### Scenario 1: Basic Flow
```
1. Register → john / john@email.com / password123
2. Message: "I have a headache"
3. Bot responds with suggestions
4. Click History → see your message
5. Logout
6. Login → john@email.com / password123
7. History still there! ✅
```

### Scenario 2: User Isolation
```
User A:
1. Register as alice / alice@email.com
2. Send message "I have fever"
3. Logout

User B:
1. Register as bob / bob@email.com
2. Go to History
3. Only sees their own messages ✅
4. Bob doesn't see Alice's "fever" message
```

### Scenario 3: Password Security
```
1. Register with password "weak"
   → Error: "Password must be at least 6 characters"
2. Try login with wrong password
   → Error: "Invalid email or password"
3. Try to register with existing email
   → Error: "Email or username already exists"
```

---

## ⚙️ Configuration

### Change Secret Key (IMPORTANT for Production)

Edit `app.py` line 10:
```python
# ❌ BEFORE
app.secret_key = "your-secret-key-change-this-in-production"

# ✅ AFTER
app.secret_key = "your-unique-random-secret-key-here-make-it-long"
```

### Change Port

Edit the last line of `app.py`:
```python
# Default: port 5000
app.run(debug=True, host="0.0.0.0", port=5000)

# Custom port: 8000
app.run(debug=True, host="0.0.0.0", port=8000)
```

---

## 🆘 Troubleshooting

### "Cannot find 'main.js'" Error
**Solution**: Make sure `main.js` exists in `static/` folder
- If missing, create it based on your original code

### "ModuleNotFoundError: No module named 'flask_login'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### "Database is locked"
**Solution**: Close other instances of the app
- Only one instance can modify the database at a time

### Can't Login After Registration
**Solution**: 
1. Verify email is exactly the same as registration
2. Check password didn't have typo
3. Restart the app: `python app.py`

### Forgot Password?
**Current Solution**: Delete `chat_history.db` and restart
- ⚠️ This deletes all saved conversations!
- Future: Implement password reset functionality

### Lost Database
**To Reset:**
```bash
# Delete the database
del chat_history.db

# Restart app (it auto-creates new database)
python app.py
```

---

## 📁 File Structure

```
healthcare_chatbot_project/
├── app.py                 ← Main backend (updated)
├── requirements.txt       ← Dependencies (updated)
├── chat_history.db        ← Database (auto-created)
├── AUTHENTICATION.md      ← Full documentation
├── SETUP_SUMMARY.md       ← Implementation details
├── QUICK_START.md         ← This file
├── knowledge_base.json    ← AI knowledge
├── symptom.json          ← Symptom data
├── response_engine.py    ← AI engine (unchanged)
├── nlp.py                ← NLP helper (unchanged)
├── static/
│   ├── main.js           ← Chat JavaScript
│   ├── style.css         ← Chat styling
│   └── ...
└── templates/
    ├── login.html        ← Login page (NEW)
    ├── register.html     ← Registration page (NEW)
    ├── index.html        ← Chat interface (updated)
    └── history.html      ← History page (updated)
```

---

## 🎓 Learn More

- **Full Documentation**: Read `AUTHENTICATION.md`
- **Implementation Details**: Read `SETUP_SUMMARY.md`
- **Flask Docs**: https://flask.palletsprojects.com/
- **Flask-Login Docs**: https://flask-login.readthedocs.io/

---

## ✨ Next Steps

After confirming everything works:

1. ✅ Test registration and login
2. ✅ Test chat functionality
3. ✅ Test history isolation (multi-user)
4. ✅ Change the secret key
5. ✅ Test on different browsers/devices
6. 📝 Customize styling if needed
7. 🚀 Deploy to production

---

## 💡 Tips

- **Password Strength**: Use mix of uppercase, lowercase, numbers, and symbols
- **Dark Mode**: Click 🌙 button to toggle dark/light theme
- **Mobile Friendly**: All pages work on mobile devices
- **No Email Required**: System doesn't validate email (you can use fake one for testing)

---

**Happy Chatting! 🏥**

Questions? Check `AUTHENTICATION.md` for detailed docs.
