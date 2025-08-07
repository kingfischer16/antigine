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
import os
from typing import Optional
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

# Global model instances (initialized lazily)
_lite_model: Optional[ChatGoogleGenerativeAI] = None
_standard_model: Optional[ChatGoogleGenerativeAI] = None
_pro_model: Optional[ChatGoogleGenerativeAI] = None
_embedding_model: Optional[GoogleGenerativeAIEmbeddings] = None


def _initialize_models() -> bool:
    """
    Initialize model instances with proper error handling for CI/testing environments.

    Returns:
        bool: True if models were successfully initialized, False otherwise
    """
    global _lite_model, _standard_model, _pro_model, _embedding_model

    # Check if we're in a testing environment or if API keys are missing
    if os.getenv("TESTING") == "1" or os.getenv("CI") == "true" or not os.getenv("GOOGLE_API_KEY"):
        return False

    try:
        _lite_model = ChatGoogleGenerativeAI(
            model=LITE_MODEL_NAME, temperature=LITE_MODEL_TEMPERATURE, thinking_budget=0, verbose=False
        )

        _standard_model = ChatGoogleGenerativeAI(
            model=STANDARD_MODEL_NAME, temperature=STANDARD_MODEL_TEMPERATURE, thinking_budget=0, verbose=False
        )

        _pro_model = ChatGoogleGenerativeAI(
            model=PRO_MODEL_NAME, temperature=PRO_MODEL_TEMPERATURE, thinking_budget=0, verbose=False
        )

        _embedding_model = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME)

        return True

    except Exception:
        # Models couldn't be initialized (likely due to missing credentials)
        return False


def get_lite_model() -> Optional[ChatGoogleGenerativeAI]:
    """Get the lite model instance, initializing if necessary."""
    if _lite_model is None:
        _initialize_models()
    return _lite_model


def get_standard_model() -> Optional[ChatGoogleGenerativeAI]:
    """Get the standard model instance, initializing if necessary."""
    if _standard_model is None:
        _initialize_models()
    return _standard_model


def get_pro_model() -> Optional[ChatGoogleGenerativeAI]:
    """Get the pro model instance, initializing if necessary."""
    if _pro_model is None:
        _initialize_models()
    return _pro_model


def get_embedding_model() -> Optional[GoogleGenerativeAIEmbeddings]:
    """Get the embedding model instance, initializing if necessary."""
    if _embedding_model is None:
        _initialize_models()
    return _embedding_model


# Module-level references that are safe to import in testing/CI environments
# These will be None until explicitly initialized
lite_model: Optional[ChatGoogleGenerativeAI] = None
standard_model: Optional[ChatGoogleGenerativeAI] = None
pro_model: Optional[ChatGoogleGenerativeAI] = None
embedding_model: Optional[GoogleGenerativeAIEmbeddings] = None

# Auto-initialize only in production environments (not testing/CI)
if not (os.getenv("TESTING") == "1" or os.getenv("CI") == "true" or os.getenv("PYTEST_CURRENT_TEST")):
    try:
        if _initialize_models():
            lite_model = _lite_model
            standard_model = _standard_model
            pro_model = _pro_model
            embedding_model = _embedding_model
    except Exception:
        # Initialization failed, models remain None which is fine for testing
        pass


class LLMManager:
    """Simple wrapper for LLM operations."""
    
    def __init__(self, model_type: str = "lite"):
        """
        Initialize LLM manager.
        
        Args:
            model_type (str): Type of model to use ("lite", "standard", "pro")
        """
        self.model_type = model_type
        
    def generate_response(
        self, 
        prompt: str, 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response using the configured model.
        
        Args:
            prompt (str): Input prompt
            temperature (float, optional): Override default temperature
            max_tokens (int, optional): Maximum tokens (not used with Gemini)
            
        Returns:
            str: Generated response
        """
        if self.model_type == "lite":
            model = get_lite_model()
        elif self.model_type == "pro":
            model = get_pro_model()
        else:
            model = get_standard_model()
            
        if not model:
            raise RuntimeError("Failed to initialize LLM model")
            
        if temperature is not None:
            # Create a new model instance with custom temperature
            # Get the model name from the original instance
            original_model_name = getattr(model, 'model', 'gemini-2.5-flash')
            model = model.__class__(
                model=original_model_name,
                temperature=temperature,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
            
        response = model.invoke(prompt)
        # Ensure we return a string regardless of response type
        if hasattr(response, 'content'):
            content = response.content
            return str(content) if content is not None else ""
        return str(response)
