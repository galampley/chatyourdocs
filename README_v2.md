### **Document QnA GPT**

#### **Introduction**
Welcome to Document QnA GPT - a user-friendly tool designed to elevate your interaction with ChatGPT by eliminating the concerns over its context window limitations. Simply upload your documents, and the app will facilitate detailed responses to your queries based on the content of the uploaded documents.

#### **File Descriptions**
- **app_v2.py**: This is the heart of the application, powered by Streamlit, orchestrating the user interface and functionalities.
- **functions_v2.py**: Houses core functions responsible for database connections, document learning, and query answering.
- **database_v2.py**: Maintains functions to initialize the database and manage the conversation history.
- **knowledgebase.db**: The SQLite database where document details, embeddings, and conversation histories are stored, structured through the functionalities defined in other files.

#### **Setup and Installation**
Ensure you have Python 3.8 or later installed. Setup involves installing necessary Python packages and setting up environment variables for OpenAI API credentials. Refer to the installation guide for detailed steps.

#### **Usage**
Running the app is as simple as executing `streamlit run app_v2.py` in your terminal. Upload PDF or TXT files, and start asking questions to get insightful answers derived from the content of the uploaded documents.

#### **Function Descriptions**
A brief overview of the primary functions in `functions_v2.py`:
- **Database Management**: Functions to initialize the database and handle conversation histories.
- **Document Learning**: Functions to "learn" from documents involve reading the content of uploaded PDF or TXT files, extracting text data, and storing it along with generated embeddings into the database.
- **Query Answering**: The query answering function utilizes OpenAI's `gpt-3.5-turbo` to answer user queries. It first identifies the most relevant text snippets from the uploaded documents using cosine similarity of embeddings, then forms a context from these snippets for the GPT model to generate a detailed answer based on the document content and the user query.

#### **Contributions**
We welcome contributions to enhance the app's functionalities. Feel free to fork the repository and open pull requests.

#### **License**
MIT License. See LICENSE file for more details.

