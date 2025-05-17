"""
Natural Language Interface module for Semantic OS.

This module provides a terminal-based chat interface that allows users to interact
with the system conversationally using natural language.
"""

from .terminal_ui import TerminalUI
from .input_processor import InputProcessor
from .response_formatter import ResponseFormatter
from .session_manager import SessionManager
from .interface_api import NaturalLanguageInterface

__all__ = ['TerminalUI', 'InputProcessor', 'ResponseFormatter', 'SessionManager', 'NaturalLanguageInterface']
