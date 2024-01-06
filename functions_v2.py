import os
import numpy as np
import sqlite3
# from PyPDF2 import PdfReader
import openai
# from openai.embeddings_utils import get_embedding, cosine_similarity
from pypdf import PdfReader

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_embedding(text, model="text-embedding-ada-002"): # model = "deployment_name"
    return openai.embeddings.create(input = [text], model=model).data[0].embedding

# Function to create a connection to the SQLite database
def create_connection():
    try:
        conn = sqlite3.connect("knowledgebase.db")
        return conn
    except Exception as e:
        raise Exception(f"Error connecting to the database: {str(e)}")

def chunk_content(content, max_words=1000):
    words = content.split()
    chunks = []
    for start_idx in range(0, len(words), max_words):
        chunk = ' '.join(words[start_idx:start_idx + max_words])
        chunks.append(chunk)
    return chunks

# Function to read PDF files and return text content
def read_pdf(file_path):
    content_chunks = []
    pdf_file = open(file_path, 'rb')
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        page_content = page.extract_text()
        content_chunks.extend(chunk_content(page_content))
    return content_chunks

# Function to read TXT files and return text content
def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return chunk_content(content)

# Main function to learn from a document and store text and embeddings in the SQLite database
def learn_document(file_path, file_name, file_type):
    content_extraction_method = {
        "pdf": read_pdf,
        "txt": read_txt
    }

    if file_type not in content_extraction_method:
        raise ValueError(f"Unsupported file type: {file_type}")

    try:
        content_chunks = content_extraction_method[file_type](file_path)
    except Exception as e:
        raise Exception(f"Error reading {file_name}: {str(e)}")

    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO documents (name, type) VALUES (?, ?)", (file_name, file_type))

        conn.commit()  # Commit to get the newly inserted document_id

        # Retrieve the last inserted document_id
        cursor.execute("SELECT last_insert_rowid()")
        document_id = cursor.fetchone()[0]

        for page_number, content in enumerate(content_chunks):
            embedding_list = get_embedding(content)
            
            if len(embedding_list)!=1536:
                raise ValueError(f"Embedding for {document_name} page {page_number} is not of shape (1536,0). Actual shape: ({len(embedding_list)},)")

            embedding_array = np.array(embedding_list)  # Convert the list to a NumPy array
            embedding_bytes = embedding_array.tobytes()  # Convert the array to bytes
            cursor.execute("INSERT INTO embeddings (document_id, page_number, text, embedding) VALUES (?, ?, ?, ?)",
                        (document_id, page_number, content, embedding_bytes))
        conn.commit()
    except Exception as e:
        raise Exception(f"Error storing {file_name} in the database: {str(e)}")
    finally:
        conn.close()

    return document_id  # Return the ID of the newly inserted document

# Function to get conversation history from the database
def get_conversation_history():
    conn = create_connection()
    if conn is None:
        print("Failed to create database connection.")
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_query, bot_response FROM conversation")
        conversation_history = cursor.fetchall()
        if not conversation_history:
            print("Conversation history is empty.")
        return conversation_history
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        conn.close()

conversation_history = get_conversation_history()
formatted_conversation = "\n".join([
    f"Human: {entry[0]}\nAgent: {entry[1]}\n" for entry in conversation_history
])

# Function to answer user queries based on stored documents
def Answer_from_documents(user_query):
    user_query_embedding_response = get_embedding(user_query)
    user_query_vector = np.array(user_query_embedding_response[:1536]) # Trim to shape (1536,)

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT text, embedding FROM embeddings")  # Select all embeddings
    data = cursor.fetchall()
    similarities = []

    for text, embedding_bytes in data:
        embedding = np.frombuffer(embedding_bytes, dtype=np.float32)[:1536] # Trim to shape (1536,)
        similarity = cosine_similarity(embedding, user_query_vector)
        similarities.append((text, similarity))

    sorted_data = sorted(similarities, key=lambda x: x[1], reverse=True)
    context = ''
    for text, _ in sorted_data[:2]:  # Include the top 2 relevant texts
        context += text

    myMessages = [
        {"role": "system", "content": f"You're a helpful Assistant for question answering over my documents.\n\nUpdated log of the user and bot chat history for conversational memory. Don't reference this unless explicitly necessary for the conversation:{formatted_conversation}."},
        {"role": "user", "content": f"The following is text from one or multiple documents:\n{context}\n\n If possible, answer the following 'query' according to the provided 'context'. \
            Reference the name/s of the relevant document/s when 'context' is not empty. If the following user query is irrelevant to context, make that known and answer to best of your ability. \
            Make sure all responses are complete and under 200 tokens. \n\nquery: {user_query}."}
    ]

    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=myMessages,
        max_tokens=200,
    )

    bot_response = response.choices[0].message.content
    #response['choices'][0]['message']['content']
    return bot_response

# Function to save the uploaded file to the local directory (unchanged)
def save_uploaded_file(uploaded_file):
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
