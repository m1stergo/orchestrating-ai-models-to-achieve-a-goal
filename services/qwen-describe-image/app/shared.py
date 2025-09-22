"""
Shared module for global variables and instances.

This module creates and manages shared resources used across the application,
such as the AI model handler. It serves as a central place for singletons
to help avoid circular imports between app modules and ensure proper
initialization order.

The main component exported is the 'handler' instance which provides access
to the AI model for inference throughout the application.
"""
from .handler import QwenHandler  # Import the specific handler implementation
from .config import settings     # Import application settings

# Create a global singleton instance of the model handler
# This ensures the model is loaded only once and shared across the application
handler = QwenHandler(settings.QWEN_MODEL_NAME)  # Initialize with model name from settings
