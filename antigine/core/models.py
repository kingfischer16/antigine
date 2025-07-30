"""
models.py
#########

Central reference for AI chat models and embedding models used in the project.
Instantiates the Google Generative AI chat model and embedding model for use
in the application.

This module cannot import from other modules in this package to avoid
circular dependencies.
"""

# Imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# Model names to use
EMBEDDING_MODEL_NAME = "gemini-embedding-001"
LITE_MODEL_NAME = "gemini-2.5-flash-lite"  # Lightweight model for focused tasks
STANDARD_MODEL_NAME = "gemini-2.5-flash"  # Balanced model for general use
PRO_MODEL_NAME = "gemini-2.5-pro"  # Most capable model for complex tasks

# Variables
LITE_MODEL_TEMPERATURE = 0.2  # Temperature for focused tasks
STANDARD_MODEL_TEMPERATURE = 0.3  # Temperature for balanced creativity/focus
PRO_MODEL_TEMPERATURE = 0.4  # Temperature for complex creative tasks

# Instantiate model instances by complexity level
lite_model = ChatGoogleGenerativeAI(
    model=LITE_MODEL_NAME, temperature=LITE_MODEL_TEMPERATURE, thinking_budget=0, verbose=False
)

standard_model = ChatGoogleGenerativeAI(
    model=STANDARD_MODEL_NAME, temperature=STANDARD_MODEL_TEMPERATURE, thinking_budget=0, verbose=False
)

pro_model = ChatGoogleGenerativeAI(
    model=PRO_MODEL_NAME, temperature=PRO_MODEL_TEMPERATURE, thinking_budget=0, verbose=False
)

# Instantiate the embedding model
# This model is used to convert text into embeddings for vector storage
embedding_model = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME)
