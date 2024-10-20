import os
from .logger import setup_logger

LOGGER = setup_logger(__name__)

def make_directories(dir_list):
    for _dir_ in dir_list:
        if os.path.exists(_dir_):
            continue
        os.makedirs(_dir_)
        LOGGER.info("Directory {0} created".format(_dir_))
