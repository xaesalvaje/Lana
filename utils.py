import os
import pandas as pd
import logging

def read_csv(filepath):
    """Reads the CSV file into a pandas dataframe."""
    df = pd.read_csv(filepath, header=0, index_col=0, parse_dates=True)
    df.sort_index(inplace=True)
    return df

def create_logger():
    """Creates a logger to output messages to the console and a log file."""
    logger = logging.getLogger('my_bot_logger')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Create a console handler and set level to INFO
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create a file handler and set level to DEBUG
    log_file = os.path.join(os.getcwd(), 'my_bot.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
