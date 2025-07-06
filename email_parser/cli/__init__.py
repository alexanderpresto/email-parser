"""CLI components for email parser."""

from .interactive import InteractiveCLI, main as interactive_main
from .main import main

__all__ = ['InteractiveCLI', 'interactive_main', 'main']