"""
Logging configuration for the email parser.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional


def configure_logging(
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    include_timestamp: bool = True,
) -> None:
    """
    Configure logging for the email parser.

    Args:
        log_level: Logging level (default: INFO)
        log_file: Optional file path for log output
        log_format: Optional custom log format
        include_timestamp: Whether to include timestamp in log format
    """
    # Create logger
    logger = logging.getLogger("email_parser")
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers = []

    # Default log format
    if not log_format:
        if include_timestamp:
            log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        else:
            log_format = "[%(levelname)s] %(name)s: %(message)s"

    formatter = logging.Formatter(log_format)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler if log file is specified
    if log_file:
        try:
            # Ensure directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to set up log file {log_file}: {str(e)}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Name of the module

    Returns:
        Logger instance
    """
    return logging.getLogger(f"email_parser.{name}")


class EmailProcessingLogAdapter(logging.LoggerAdapter):
    """
    Custom log adapter for email processing.

    Adds email ID and other contextual information to log messages.
    """

    def __init__(self, logger: logging.Logger, extra: Dict[str, Any]):
        """
        Initialize the log adapter.

        Args:
            logger: Logger to adapt
            extra: Dictionary of extra contextual information
        """
        super().__init__(logger, extra)

    # def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
    def process(self, msg, kwargs: MutableMapping[str, Any]):
        """
        Process the log message to add contextual information.
        
        Args:
            msg: Log message
            kwargs: Logging kwargs
            
        Returns:
            Tuple of (modified message, kwargs)
        """
        email_id = self.extra.get("email_id", "unknown") if self.extra else "unknown"
        component = self.extra.get("component", "") if self.extra else ""
        
        if component:
            context = f"[Email: {email_id}, Component: {component}]"
        else:
            context = f"[Email: {email_id}]"
            
        return f"{context} {msg}", kwargs
