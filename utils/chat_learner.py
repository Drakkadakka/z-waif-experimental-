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
from utils.performance_metrics import track_performance
from utils.memory_manager import MemoryManager  # Import the new class

# Ensure apscheduler is installed in your environment
# Run: pip install apscheduler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatLearner:
    def __init__(self, db_name='chat_learner.db', rag_processor=None):
        log_info("Initializing ChatLearner.")
        self.connection = sqlite3.connect(db_name)
        self.memory_manager = MemoryManager(rag_processor)
        self.setup_database()
        self.user_histories = {}
        self.emotional_states = {}

    def setup_database(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                user_id TEXT,
                timestamp DATETIME,
                message TEXT,
                response TEXT,
                emotion TEXT,
                context TEXT
            )
        ''')
        self.connection.commit()

    def learn_from_message(self, message_data):
        log_info(f"Learning from message: {message_data}.")
        user_id = message_data.get('user_id')
        message = message_data.get('message')
        platform = message_data.get('platform')
        
        # Analyze message sentiment and context
        sentiment = TextBlob(message).sentiment
        context = self.get_user_context(user_id)
        
        # Generate personalized response
        response = self.generate_personalized_response(user_id, message)
        
        # Store interaction
        self.store_interaction(user_id, message, response, sentiment.polarity)
        
        return response

    def generate_personalized_response(self, user_id, message):
        # Get user history and preferences
        user_history = self.get_user_history(user_id)
        emotional_state = self.get_emotional_state(user_id)
        
        # Use transformer pipeline for response generation
        generator = pipeline('text-generation')
        
        # Create context-aware prompt
        prompt = self.create_context_prompt(user_history, emotional_state, message)
        
        # Generate response
        response = generator(prompt, max_length=150)[0]['generated_text']
        
        return self.post_process_response(response, emotional_state)

    def get_user_history(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT message, response, emotion, timestamp 
            FROM interactions 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (user_id,))
        return cursor.fetchall()

    def store_interaction(self, user_id, message, response, emotion):
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO interactions 
            (user_id, timestamp, message, response, emotion) 
            VALUES (?, datetime('now'), ?, ?, ?)
        ''', (user_id, message, response, emotion))
        self.connection.commit()

    def get_emotional_state(self, user_id):
        return self.emotional_states.get(user_id, {
            'baseline_mood': 'neutral',
            'recent_emotions': [],
            'interaction_count': 0
        })

    def update_emotional_state(self, user_id, new_emotion):
        if user_id not in self.emotional_states:
            self.emotional_states[user_id] = {
                'baseline_mood': 'neutral',
                'recent_emotions': [],
                'interaction_count': 0
            }
        
        state = self.emotional_states[user_id]
        state['recent_emotions'].append(new_emotion)
        state['interaction_count'] += 1
        
        # Update baseline mood based on recent interactions
        if len(state['recent_emotions']) > 5:
            state['baseline_mood'] = self.calculate_dominant_emotion(
                state['recent_emotions'][-5:]
            )

    def dynamic_personality_shaping(self, user_id, feedback):
        """Adjust response style based on user feedback"""
        current_state = self.get_emotional_state(user_id)
        
        # Update personality parameters based on feedback
        if feedback.get('style_preference'):
            current_state['style_preference'] = feedback['style_preference']
        
        if feedback.get('topic_interests'):
            current_state['interests'] = feedback['topic_interests']
        
        self.emotional_states[user_id] = current_state

    def prune_old_messages(self):
        """Remove messages and emotional states older than 365 days"""
        cursor = self.connection.cursor()
        cursor.execute('''
            DELETE FROM interactions 
            WHERE timestamp < datetime('now', '-365 days')
        ''')
        self.connection.commit()

# API Support Skeleton
app = Flask(__name__)
learner = ChatLearner()

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(learner.prune_old_messages, IntervalTrigger(days=365))  # Schedule cleanup every 365 days
scheduler.start()

# Assuming you have memory_manager and chat_learner defined somewhere in your code
memory_manager = MemoryManager()  # Initialize as needed
chat_learner = ChatLearner()  # Initialize as needed

# Initialize PersonalizedResponseGenerator with the required arguments
response_generator = PersonalizedResponseGenerator(memory_manager, chat_learner)  # Pass the required arguments

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