import sqlite3

class ChatLearner:
    def __init__(self, db_name='chat_learner.db'):
        # Connect to the SQLite database (or create it if it doesn't exist)
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        
        # Create a table for storing messages and sentiments
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                sentiment REAL NOT NULL
            )
        ''')
        self.connection.commit()

    def learn_from_message(self, message_data):
        """
        Learn from a new message by storing it and its associated sentiment.
        
        Args:
            message_data (dict): A dictionary containing 'message' and 'sentiment'.
        """
        message = message_data.get('message')
        sentiment = message_data.get('sentiment')

        # Store the message and its sentiment in the database
        if message and sentiment is not None:
            self.cursor.execute('''
                INSERT INTO messages (message, sentiment) VALUES (?, ?)
            ''', (message, sentiment))
            self.connection.commit()
            print(f"Learned message: '{message}' with sentiment: {sentiment}")
        else:
            print("Invalid message data. Message and sentiment must be provided.")

    def get_learned_messages(self):
        """Return the learned messages from the database."""
        self.cursor.execute('SELECT message, sentiment FROM messages')
        return self.cursor.fetchall()

    def close(self):
        """Close the database connection."""
        self.connection.close()

# Example usage
if __name__ == "__main__":
    learner = ChatLearner()
    
    # Learning from a message
    learner.learn_from_message({'message': 'I love programming!', 'sentiment': 0.9})
    learner.learn_from_message({'message': 'I am feeling sad.', 'sentiment': -0.6})

    # Retrieving learned messages
    learned_messages = learner.get_learned_messages()
    print("Learned Messages and Sentiments:")
    for msg, sentiment in learned_messages:
        print(f"Message: '{msg}', Sentiment: {sentiment}")

    # Close the learner
    learner.close()
