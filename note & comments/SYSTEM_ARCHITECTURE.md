# 🎨 User Flow Diagram & System Architecture

## User Journey Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     VISITOR ARRIVES                              │
│                   (http://localhost:5000)                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Check if     │
                    │ logged in?   │
                    └──────┬───────┘
                   ┌───────┤
                   │       │
            YES    │       │ NO
                   │       │
                   ▼       ▼
            ┌──────────┐  ┌────────────────┐
            │CHAT PAGE │  │  LOGIN PAGE    │
            │/         │  │  /login        │
            └──────────┘  └────────┬───────┘
                                   │
                          ┌────────┴────────┐
                          │                 │
                      LOGIN          REGISTER
                        │                 │
                        ▼                 ▼
                   ┌──────────┐  ┌──────────────┐
                   │ Verify   │  │ CREATE       │
                   │ Email &  │  │ ACCOUNT      │
                   │ Password │  │ /register    │
                   └────┬─────┘  └──────┬───────┘
                        │               │
                   VALID│               │SUCCESS
                        │               │
                        └───────┬───────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │ CREATE SESSION   │
                        │ LOGIN USER       │
                        │ Redirect to /    │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   CHAT SCREEN    │
                        │ (Protected Route)│
                        └────────┬─────────┘
              ┌────────────────┬─┴──────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌─────────┐    ┌──────────┐    ┌──────────────┐
        │  SEND   │    │  VIEW    │    │    DARK      │
        │ MESSAGE │    │ HISTORY  │    │    MODE      │
        └────┬────┘    └────┬─────┘    └──────────────┘
             │               │
             └──────┬────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │   USER MESSAGES     │
         │  SAVED TO DATABASE  │
         │  (user_id linked)   │
         └─────────────────────┘

                    LOGOUT
                      │
                      ▼
            ┌─────────────────────┐
            │ DESTROY SESSION     │
            │ REDIRECT TO /login  │
            └─────────────────────┘
```

---

## Authentication State Diagram

```
                    ┌──────────────────┐
                    │   NOT LOGGED IN   │
                    │ (Anonymous User)  │
                    └────────┬──────────┘
                             │
                ┌────────────┼────────────┐
                │                         │
                ▼                         ▼
            ┌─────────┐            ┌──────────┐
            │ Provide │            │ Provide  │
            │ Email & │            │ User Info│
            │Password │            │& Password│
            └────┬────┘            └────┬─────┘
                 │                      │
                 │ Verify              │ Validate
                 │ Password            │ Form
                 │                      │
                 ▼                      ▼
          ┌────────────┐         ┌──────────────┐
          │  PASSWORD  │         │    CREATE    │
          │   CORRECT  │         │    ACCOUNT   │
          │            │         │   HASH PWD   │
          └─────┬──────┘         └─────┬────────┘
                │                      │
           YES  │                      │ SUCCESS
                │                      │
                └──────────┬───────────┘
                           │
                           ▼
                    ┌──────────────────┐
                    │  CREATE SESSION  │
                    │  GENERATE COOKIE │
                    │  SET FLASK_LOGIN │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   LOGGED IN      │
                    │ (Authenticated)  │
                    └────────┬─────────┘
                             │
               ┌─────────────┤─────────────┐
               │             │             │
               ▼             ▼             ▼
            ACCESS       CHAT             VIEW
            CHAT PAGE    HISTORY          HISTORY
            `/`          `/chat`          `/history-page`
               │             │             │
               └─────────────┼─────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ DATA FILTERED BY │
                    │   USER ID        │
                    │ (Privacy)        │
                    └──────────────────┘
```

---

## Database Schema Relationship

```
┌────────────────────────────────────────┐
│              USERS TABLE               │
├─────────────────────────────────────────┤
│ id          (PRIMARY KEY)               │
│ username    (UNIQUE)                    │
│ email       (UNIQUE)                    │
│ password    (HASHED)                    │
│ gender                                  │
│ age                                     │
│ created_at                              │
└────────┬───────────────────────────────┘
         │ (Foreign Key)
         │ user_id
         │
         ▼
┌────────────────────────────────────────┐
│          INTERACTIONS TABLE            │
├────────────────────────────────────────┤
│ id          (PRIMARY KEY)               │
│ user_id     (FOREIGN KEY → users.id)    │
│ user_text                               │
│ bot_text                                │
│ timestamp                               │
│ ON DELETE CASCADE                       │
└────────────────────────────────────────┘
```

**Privacy Enforcement**:
- Each message has user_id
- Queries filtered: `WHERE user_id = current_user.id`
- User A cannot see User B's messages

---

## Application Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   WEB BROWSER                                │
│         (Login, Register, Chat, History Pages)              │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP Requests
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 FLASK APPLICATION                            │
│                  (app.py)                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────┐            │
│  │   ROUTE HANDLERS                           │            │
│  ├────────────────────────────────────────────┤            │
│  │ • @app.route("/login")     [GET/POST]     │            │
│  │ • @app.route("/register")  [GET/POST]     │            │
│  │ • @app.route("/logout")    [GET]          │            │
│  │ • @app.route("/")          [@login_required
│  │ • @app.route("/chat")      [@login_required
│  │ • @app.route("/history")   [@login_required            │
│  └────────────────────────────────────────────┘            │
│           │ Database Operations                │            │
│           ▼                                    │            │
│  ┌────────────────────────────────────────────┐            │
│  │   AUTHENTICATION LAYER                     │            │
│  ├────────────────────────────────────────────┤            │
│  │ • Flask-Login (Session Management)        │            │
│  │ • Werkzeug (Password Hashing)             │            │
│  │ • @login_required decorator               │            │
│  │ • User loader callback                    │            │
│  └────────────────────────────────────────────┘            │
│           │                                    │            │
└───────────┼────────────────────────────────────┘            │
            │                                    
            ▼                                    
┌─────────────────────────────────────────────────────────────┐
│                SQLITE DATABASE                              │
│            (chat_history.db)                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐           ┌──────────────────┐           │
│  │ users table  │◄──────────┤interactions table│           │
│  ├──────────────┤ user_id   ├──────────────────┤           │
│  │ id       (PK)│           │ id           (PK)│           │
│  │ username     │           │ user_id      (FK)│           │
│  │ email        │           │ user_text        │           │
│  │ password     │           │ bot_text         │           │
│  │ gender       │           │ timestamp        │           │
│  │ age          │           │ ON DELETE CASCADE│           │
│  │ created_at   │           │                  │           │
│  └──────────────┘           └──────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow for Chat Message

```
┌─────────────────────────┐
│  User types message in  │
│  browser chat box       │
└────────────┬────────────┘
             │
             │ JSON: {message: "I have headache"}
             ▼
┌─────────────────────────────────────────┐
│  main.js sends to /chat endpoint        │
│  (POST request with AJAX)               │
└────────────┬─────────────────────────────┘
             │
             │ HTTP POST /chat
             ├─ @login_required checks session
             ├─ If not logged in → Redirect to /login
             │
             ▼
┌─────────────────────────────────────────┐
│  Flask receives POST /chat              │
│  • Extract message from JSON            │
│  • Get current_user.id from session     │
│  • Call ResponseEngine (AI processing)  │
│  • Get bot response                     │
└────────────┬─────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  save_interaction()                     │
│  INSERT INTO interactions               │
│  (user_id, user_text, bot_text,         │
│   timestamp) VALUES (?, ?, ?, ?)        │
│  ↑ user_id links message to user        │
└────────────┬─────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Database saves conversation            │
│  only THIS user can see it              │
└────────────┬─────────────────────────────┘
             │
             │ JSON: {reply: "Take aspirin..."}
             ▼
┌─────────────────────────────────────────┐
│  Browser receives response              │
│  Display in chat box                    │
│  • User message (blue)                  │
│  • Bot response (green)                 │
└─────────────────────────────────────────┘
```

---

## Security Checks at Each Step

```
REQUEST ARRIVES
    │
    ▼
┌────────────────────────────┐
│ 1. ROUTE MATCHING          │
│ Check if endpoint exists   │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ 2. @login_required?        │
│ YES → Check session cookie │
│ NO → Proceed               │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ 3. LOAD USER FROM SESSION  │
│ Verify user_id exists      │
│ Load User object           │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ 4. INPUT VALIDATION        │
│ Check JSON format          │
│ Validate field types       │
│ Check required fields      │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ 5. SQL PARAMETERIZATION    │
│ cur.execute(SQL, (params)) │
│ Prevent SQL injection      │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ 6. DATA ISOLATION FILTERING│
│ WHERE user_id = ?          │
│ Only current_user.id data  │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ 7. RESPONSE SENT           │
│ Only authenticated user    │
│ receives data              │
└────────────────────────────┘
```

---

## Comparison: Before vs After

```
╔════════════════════════════════════════════════════════════╗
║                    BEFORE THIS UPDATE                       ║
╠════════════════════════════════════════════════════════════╣
║ Feature               │ Status                               ║
║ User Login            │ ❌ No authentication                 ║
║ User Registration     │ ❌ No account system                 ║
║ Chat History          │ ✅ Yes, but shared among all users   ║
║ User Privacy          │ ❌ Everyone sees everyone's history  ║
║ Password Security     │ ❌ No passwords                      ║
║ User Identification   │ ❌ No user info                      ║
║ Database              │ ⚠️ Basic interactions table only      ║
╚════════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════════════╗
║                    AFTER THIS UPDATE                       ║
╠════════════════════════════════════════════════════════════╣
║ Feature               │ Status                             ║
║ User Login            │ ✅ Email + Password authentication ║
║ User Registration     │ ✅ Full account creation system    ║
║ Chat History          │ ✅ User-specific, private history  ║
║ User Privacy          │ ✅ Each user sees only their own   ║
║ Password Security     │ ✅ Hashed with Werkzeug            ║
║ User Identification   │ ✅ Username, email, age, gender    ║
║ Database              │ ✅ Users + Interactions with FK    ║
╚════════════════════════════════════════════════════════════╝
```

---

**This diagram shows the complete system flow and architecture of your authenticated healthcare chatbot.**
