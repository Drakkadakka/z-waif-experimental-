# Ensure Flask is installed in your environment
# Run the following command in your terminal:
# pip install Flask

import sqlite3
import time
from textblob import TextBlob  # For sentiment analysis
import random  # For dynamic personality shaping
from transformers import pipeline  # Import the transformers library
from flask import Flask, request, jsonify

class ChatLearner:
    def __init__(self, db_name='chat_learner.db'):
        # Connect to the SQLite database (or create it if it doesn't exist)
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        
        # Create tables for messages, personality templates, emotional states, and user profiles
        self.create_tables()
        self.prune_old_messages()  # Clean up old messages on initialization
        
        # Initialize the emotion recognition model
        self.emotion_recognizer = pipeline("text-classification", model="bhadresh-savani/bert-base-uncased-emotion")

    def create_tables(self):
        """Create necessary tables in the database."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                sentiment REAL NOT NULL,
                timestamp INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                context TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS personality_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotional_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                emotion TEXT NOT NULL,
                FOREIGN KEY (message_id) REFERENCES messages (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                personality TEXT,
                preferences TEXT
            )
        ''')
        
        self.connection.commit()

    def learn_from_message(self, message_data):
        """
        Learn from a new message by storing it and its associated sentiment.
        
        Args:
            message_data (dict): A dictionary containing 'message', 'sentiment', 'emotion', 'user_id', and 'context'.
        """
        message = message_data.get('message')
        sentiment = message_data.get('sentiment')
        emotion = message_data.get('emotion')
        user_id = message_data.get('user_id')
        context = message_data.get('context', '')  # Optional context field
        timestamp = int(time.time())

        if message and sentiment is not None:
            try:
                self.cursor.execute('''
                    INSERT INTO messages (message, sentiment, timestamp, user_id, context) VALUES (?, ?, ?, ?, ?)
                ''', (message, sentiment, timestamp, user_id, context))
                message_id = self.cursor.lastrowid
                
                if emotion:
                    self.cursor.execute('''
                        INSERT INTO emotional_states (message_id, emotion) VALUES (?, ?)
                    ''', (message_id, emotion))
                self.connection.commit()
                print(f"Learned message: '{message}' with sentiment: {sentiment} and emotion: {emotion} from user: {user_id}")
            except Exception as e:
                print(f"Error learning message: {e}")

    def analyze_sentiment(self, message):
        """Analyze the sentiment of a given message."""
        analysis = TextBlob(message)
        return analysis.sentiment.polarity  # Returns a value between -1 (negative) and 1 (positive)

    def recognize_emotion(self, message):
        """Recognize emotion from the message using a pre-trained model."""
        # Use the emotion recognition model to predict the emotion
        predictions = self.emotion_recognizer(message)
        # Extract the emotion with the highest score
        emotion = max(predictions, key=lambda x: x['score'])
        return emotion['label']  # Return the predicted emotion label

    def generate_personalized_response(self, user_id, message):
        """Generate a personalized response based on user profile and message context."""
        profile = self.get_user_profile(user_id)
        if profile:
            personality = profile[0]
            # Generate a response based on personality and message context
            if personality == 'Friendly':
                return f"{message} 😊 How can I help you further?"
            elif personality == 'Formal':
                return f"{message} How may I assist you today?"
        return message  # Default response if no profile found

    def dynamic_personality_shaping(self, user_id, feedback):
        """Adjust the user's personality based on feedback."""
        # Placeholder for dynamic personality shaping logic
        # In a real implementation, you might analyze feedback and adjust personality accordingly
        if feedback == 'positive':
            self.update_user_profile(user_id, personality='Friendly')
        elif feedback == 'negative':
            self.update_user_profile(user_id, personality='Formal')

    def update_user_profile(self, user_id, personality=None, preferences=None):
        """Update the user profile with new personality or preferences."""
        try:
            self.cursor.execute('''
                INSERT INTO user_profiles (user_id, personality, preferences) VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET personality = ?, preferences = ?
            ''', (user_id, personality, preferences, personality, preferences))
            self.connection.commit()
            print(f"User profile for {user_id} updated.")
        except Exception as e:
            print(f"Error updating user profile: {e}")

    def get_user_profile(self, user_id):
        """Retrieve a user profile by user ID."""
        self.cursor.execute('SELECT personality, preferences FROM user_profiles WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()

    def prune_old_messages(self):
        """Remove messages and emotional states older than 365 days."""
        one_year_ago = int(time.time()) - (365 * 24 * 60 * 60)

        self.cursor.execute('''
            DELETE FROM emotional_states
            WHERE message_id IN (
                SELECT id FROM messages WHERE timestamp < ?
            )
        ''', (one_year_ago,))

        self.cursor.execute('DELETE FROM messages WHERE timestamp < ?', (one_year_ago,))
        self.connection.commit()
        print("Pruned messages and emotional states older than 365 days.")

    def close(self):
        """Close the database connection."""
        self.connection.close()

# API Support Skeleton
app = Flask(__name__)
learner = ChatLearner()

@app.route('/learn', methods=['POST'])
def learn():
    data = request.json
    learner.learn_from_message(data)
    return jsonify({"status": "success", "message": "Message learned."})

@app.route('/generate_response', methods=['POST'])
def generate_response():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    response = learner.generate_personalized_response(user_id, message)
    return jsonify({"response": response})

@app.route('/user_profile/<user_id>', methods=['GET'])
def user_profile(user_id):
    profile = learner.get_user_profile(user_id)
    return jsonify({"profile": profile})

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    user_id = data.get('user_id')
    feedback = data.get('feedback')
    learner.dynamic_personality_shaping(user_id, feedback)
    return jsonify({"status": "success", "message": "Personality updated based on feedback."})

if __name__ == "__main__":
    app.run(debug=True)