import logging

# Configure the main logger
logger = logging.getLogger("main_logger")
logger.setLevel(logging.DEBUG)  # Adjust as needed

def setup_logger():
    # Clear default handlers
    logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)