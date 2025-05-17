"""
Local LLM Integration module for Semantic OS.

This module provides natural language understanding and generation capabilities
by integrating a lightweight, local LLM using Hugging Face Transformers.
"""

from .model_manager import ModelManager
from .context_manager import ContextManager
from .prompt_engineer import PromptEngineer
from .inference_engine import InferenceEngine
from .llm_api import LocalLLM

__all__ = ['ModelManager', 'ContextManager', 'PromptEngineer', 'InferenceEngine', 'LocalLLM']
