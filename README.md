# AI Healthcare Chatbot - Academic Demo

## Overview
Simple AI Healthcare Chatbot for academic demonstration. The bot uses basic keyword matching to provide preliminary health guidance.

## Files
- app.py : Flask web application
- response_engine.py : loads knowledge base and finds responses
- nlp.py : simple preprocessing utilities
- knowledge_base.json : symptom-response data
- templates/index.html : web UI
- static/* : CSS and JavaScript for UI
- chat_history.db : created at runtime to store interactions
- requirements.txt : Python dependencies

## How to run (locally)
1. Create a virtual environment (recommended).
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `python app.py`
4. Open `http://127.0.0.1:5000` in your browser.

## Notes
- This is a rule-based educational demo. It is NOT a medical device or diagnostic tool.
- For improved NLP, you can integrate spaCy or train an intent classifier.