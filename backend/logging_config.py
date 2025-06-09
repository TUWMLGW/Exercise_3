import logging
import os
from datetime import datetime
import glob

def setup_logging():
    """Sets up the logging configuration."""
    logging_dir = "logs"
    log_file_pattern = os.path.join(logging_dir, "breakout_logs_*.log")

    if os.path.exists(logging_dir):
        old_log_files = glob.glob(log_file_pattern)
        for old_file in old_log_files:
            try:
                os.remove(old_file)
            except OSError as e:
                print(f"Error deleting old log file {old_file}: {e}")
    log_filename = datetime.now().strftime("breakout_logs_%Y%m%d_%H%M%S.log")
    log_filepath = os.path.join(logging_dir, log_filename)
    os.makedirs(logging_dir, exist_ok=True)

    # Basic logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Log all messages to a file
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root.addHandler(file_handler)

    # Log INFO+ to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)

    # Specific loggers
    logging.getLogger('app').setLevel(logging.INFO)
    logging.getLogger('rlagent').setLevel(logging.INFO)
    logging.getLogger('gamelogic').setLevel(logging.INFO)

    # Avoid writing down logs from Flask
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.propagate = False 

    # Confirm setup
    root.info(f"Logging setup complete. Logs being written to {log_filepath}")