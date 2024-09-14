import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_level=logging.INFO):
    # Use /tmp directory for logs
    log_dir = '/tmp/mypia_logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File handler (info level and above)
    file_handler = RotatingFileHandler(os.path.join(log_dir, 'mypia.log'), maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Console handler (warning level and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(console_formatter)

    # Error file handler (error level and above)
    error_file_handler = RotatingFileHandler(os.path.join(log_dir, 'error.log'), maxBytes=10*1024*1024, backupCount=5)
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(file_formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_file_handler)

    return logger
