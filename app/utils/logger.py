"""
Logger setup for Excel AI Assistant.
"""

import datetime
import logging
import os
from pathlib import Path


def setup_logger(name, level="INFO", log_to_file=True, log_dir=None):
    """
    Set up a logger with console and file handlers

    Args:
        name: Logger name
        level: Logging level
        log_to_file: Whether to log to file
        log_dir: Directory for log files (default: logs in user home)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)

    # Set level from string or int
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(console_handler)

    # Add file handler if requested
    if log_to_file:
        # Create log directory if it doesn't exist
        if log_dir is None:
            log_dir = os.path.join(str(Path.home()), '.excel-ai-assistant', 'logs')

        os.makedirs(log_dir, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")

        # Create file handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        # Add file handler to logger
        logger.addHandler(file_handler)

    return logger


def get_log_files(log_dir=None):
    """
    Get list of log files

    Args:
        log_dir: Directory containing log files

    Returns:
        List of log file paths
    """
    if log_dir is None:
        log_dir = os.path.join(str(Path.home()), '.excel-ai-assistant', 'logs')

    if not os.path.exists(log_dir):
        return []

    # Get all .log files in the directory
    log_files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith('.log')]

    # Sort by modification time (newest first)
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    return log_files
