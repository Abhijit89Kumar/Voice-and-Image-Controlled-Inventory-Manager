import logging
from logging.handlers import RotatingFileHandler
import inspect

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define a custom log format
log_format = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'

# Create a rotating file handler with a maximum file size of 1 GB and 5 backup files
handler = RotatingFileHandler('inventory.log', maxBytes=1024*1024*1024, backupCount=5)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(log_format))

# Add the rotating file handler to the logger
logger.addHandler(handler)

def log_function_call(func):
    def wrapper(*args, **kwargs):
        caller = inspect.stack()[1][3]  # Get the name of the calling function
        logging.info(f"Function call: {caller}")
        return func(*args, **kwargs)
    return wrapper