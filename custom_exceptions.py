import os
import logging

class LearningError(Exception):
    pass

class DatabaseError(Exception):
    pass

def verify_file_read(file_path):
    """
    Verify if the file at the specified path can be read.
    
    :param file_path: The path to the file to verify.
    :return: True if the file exists and can be read, False otherwise.
    """
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)

def log_error(e):
    """
    Log the details of the exception.
    
    :param e: The exception to log.
    """
    logging.exception(e)
