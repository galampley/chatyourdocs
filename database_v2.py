import sqlite3
import os
from functions_v2 import create_connection  # Import the create_connection function

def initialize_database():
    '''
    # Delete existing db file it it exists
    if os.path.exists("knowledgebase.db"):
        os.remove("knowledgebase.db")
    '''
    
    create_documents_table = """
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL
    );
    """

    create_embeddings_table = """
    CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        page_number INTEGER,
        text TEXT NOT NULL,
        embedding BLOB NOT NULL,
        FOREIGN KEY (document_id) REFERENCES documents (id)
    );
    """

    create_conversation_table = """
    CREATE TABLE IF NOT EXISTS conversation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_query TEXT NOT NULL,
        bot_response TEXT NOT NULL
    );
    """

    conn = sqlite3.connect("knowledgebase.db")
    cursor = conn.cursor()
    cursor.execute(create_documents_table)
    cursor.execute(create_embeddings_table)
    cursor.execute(create_conversation_table)  # Create the conversation table
    conn.commit()
    conn.close()

def save_conversation_history(conversation):
    conn = create_connection()
    cursor = conn.cursor()
    for user_query, bot_response in conversation:
        cursor.execute("INSERT INTO conversation (user_query, bot_response) VALUES (?, ?)", (user_query, bot_response))
    conn.commit()
    conn.close()

# Function to get conversation history from the database
def get_conversation_history():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_query, bot_response FROM conversation")
    conversation_history = cursor.fetchall()
    conn.close()
    return conversation_history

def clear_conversation_history():
    conn = sqlite3.connect("knowledgebase.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversation")
    conn.commit()
    conn.close()