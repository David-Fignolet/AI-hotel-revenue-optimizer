# src/utils/logger.py
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from ..utils.config import settings

def setup_logging():
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = RotatingFileHandler(
        log_dir / "hotel_revenue.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Set log level based on environment
    if settings.env == "development":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    # Suppress noisy loggers
    for logger_name in ['urllib3', 'asyncio']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    return logger

# Create logger instance
logger = logging.getLogger(__name__)