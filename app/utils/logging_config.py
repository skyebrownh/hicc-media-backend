import logging
import sys

def setup_logging():
    """
    Configure logging for the application.
    
    Sets up basic logging configuration with INFO level, formatted output
    to stdout including timestamp, logger name, log level, and message.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )