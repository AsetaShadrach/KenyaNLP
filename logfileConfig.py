import logging
import logging.config
import yaml
import os
from pathlib import Path

file_path = "process.log"

def logmaker(filename=file_path):
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path, filename)
    return logging.FileHandler(path)


def mk_log(LOGGER):
    # The file's path
    path = os.path.dirname(os.path.realpath(__file__))

    # Config file relative to this file
    loggingConf = open('{0}/log_config.yml'.format(path), 'r')
    logging.config.dictConfig(yaml.safe_load(loggingConf.read()))
    loggingConf.close()
    logger = logging.getLogger(LOGGER)
    
    return logger


def get_last_tweet_id(file_path, logger):
    # Add how to check incase the last entry was not the tweet , eg. an error
    last_id_logged = None 

    try:
        last_line = Path(file_path).read_text().splitlines()[-1]
        last_id_logged = int(last_line.split(" ")[-1])
    except Exception as e:
        logger.error("The last line did not contain the Tweet ID for the last entry")

    return last_id_logged


