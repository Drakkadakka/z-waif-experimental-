import sqlite3
import time
import logging
from textblob import TextBlob  # For sentiment analysis
import random  # For dynamic personality shaping
from transformers import pipeline  # Import the transformers library
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from utils.personalized_response import PersonalizedResponseGenerator  # Import the new class
from utils.emotion_recognizer import recognize_emotion_from_text
from utils.logging import log_info, log_error

# Ensure apscheduler is installed in your environment
# Run: pip install apscheduler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatLearner:
    def __init__(self, db_name='chat_learner.db'):
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_tables()
        self.prune_old_messages()  # Clean up old messages on initialization
        self.emotion_recognizer = pipeline("text-classification", model="bhadresh-savani/bert-base-uncased-emotion")

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            sentiment REAL NOT NULL,
            timestamp INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            context TEXT
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            personality TEXT,
            preferences TEXT
        )''')
        
        self.connection.commit()

    def learn_from_message(self, message_data):
        """Learn from a new message by storing it and its associated sentiment."""
        message = message_data.get('message')
        sentiment = message_data.get('sentiment')
        emotion = message_data.get('emotion')
        user_id = message_data.get('user_id')
        context = message_data.get('context', '')  # Optional context field
        timestamp = int(time.time())

        if message and sentiment is not None:
            try:
                # Recognize emotion from the message
                emotion = recognize_emotion_from_text(message)
                
                self.cursor.execute('''INSERT INTO messages (message, sentiment, timestamp, user_id, context) VALUES (?, ?, ?, ?, ?)''',
                                    (message, sentiment, timestamp, user_id, context))
                message_id = self.cursor.lastrowid
                
                self.cursor.execute('''INSERT INTO emotional_states (message_id, emotion) VALUES (?, ?)''', (message_id, emotion))
                self.connection.commit()
                log_info(f"Learned message: '{message}' with sentiment: {sentiment} and emotion: {emotion} from user: {user_id}")
            except Exception as e:
                log_error(f"Error learning message: {e}")

    def prune_old_messages(self):
        one_year_ago = int(time.time()) - (365 * 24 * 60 * 60)
        self.cursor.execute('DELETE FROM messages WHERE timestamp < ?', (one_year_ago,))
        self.connection.commit()
        log_info("Pruned messages and emotional states older than 365 days.")

# API Support Skeleton
app = Flask(__name__)
learner = ChatLearner()

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(learner.prune_old_messages, IntervalTrigger(days=365))  # Schedule cleanup every 365 days
scheduler.start()

# Initialize the personalized response generator
response_generator = PersonalizedResponseGenerator()

@app.route('/learn', methods=['POST'])
def learn():
    data = request.json
    learner.learn_from_message(data)
    return jsonify({"status": "success", "message": "Message learned."})

@app.route('/generate_response', methods=['POST'])
def generate_response():
    data = request.json
    user_id = data.get('user_id')
    user_message = data.get('message')
    
    # Generate a personalized response
    response = response_generator.generate_response(user_id, user_message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)