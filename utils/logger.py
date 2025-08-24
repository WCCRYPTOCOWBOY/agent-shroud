import logging

def get_logger(name: str) -> logging.Logger:
    """
    Create and return a configured logger.
    Each logger has a StreamHandler with a simple formatter.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
