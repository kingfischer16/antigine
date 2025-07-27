from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

"""
models.py
#########

Central reference for AI chat models and embedding models used in the project.
Instantiates the Google Generative AI chat model and embedding model for use in the application.

This module cannot import from other modules in this package to avoid circular dependencies.
"""

# Imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# Model names to use
EMBEDDING_MODEL_NAME = "gemini-embedding-001"
GEMINI_CHAT_MODEL_NAME = "gemini-2.5-flash-lite" # "gemini-2.5-flash-lite-latest"

# Variables
CHAT_MODEL_TEMPERATEURE = 0.2  # Temperature for the chat model, controlling randomness in responses

# Instantiate the chat model
# This model is used for generating chat responses based on user input
chat_model = ChatGoogleGenerativeAI(model=GEMINI_CHAT_MODEL_NAME, temperature=CHAT_MODEL_TEMPERATEURE, thinking_budget=0, verbose=False)

# Instanitate the embedding model
# This model is used to convert text into embeddings for vector storage and similarity search
embedding_model = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME, verbose=False)
