import logging
from syntask.settings import LOG_FILE_NAME

def get_logger():
    """Retruns logger with log file configuration"""

    logging.basicConfig(filename=LOG_FILE_NAME,
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.ERROR)
    
    logger = logging.getLogger()
    return logger