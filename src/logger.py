import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name = "jira_app", log_level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with a rotating file handler.
    
    Args:
        log_level (str): The logging level to set. Default is "INFO".
    
    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create a custom logger
    logger = logging.getLogger(name)

    # Convert log_level string to actual logging level
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Define log format
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    os.makedirs("logs", exist_ok=True)
    # Create a rotating file handler that logs even debug messages
    handler = RotatingFileHandler("logs/jira_app.log", maxBytes=1024 * 1024 * 5, backupCount=5)
    handler.setLevel(log_level)
    handler.setFormatter(log_format)

    # Add the handler to the logger (if not already added)
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
