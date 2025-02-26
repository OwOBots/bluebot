import logging


def setup_logger(name, log_file, level=logging.DEBUG):
    """Function to setup a logger with the specified name, log file, and log level."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Check if the logger already has handlers
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger
