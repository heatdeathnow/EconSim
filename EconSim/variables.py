from __future__ import annotations
from logging import Logger, FileHandler, StreamHandler, Formatter, DEBUG, WARNING
from enum import StrEnum
from os import getcwd

TESTING = False

class Strata(StrEnum):
    LOWER  = 'lower'
    MIDDLE = 'middle'
    UPPER  = 'upper'

log_file = 'EconSim.log'
log_formatter = Formatter(fmt = '%(levelname)s at %(asctime)s -> %(message)s', datefmt = 'day: %d, time: %H°%M\'%S"')

log_file_handler = FileHandler(filename = log_file, encoding = 'utf-8')
log_file_handler.setFormatter(log_formatter)
log_file_handler.setLevel(DEBUG)

log_stream_handler = StreamHandler()
log_stream_handler.setFormatter(log_formatter)
log_stream_handler.setLevel(WARNING)

logger = Logger('EconSim')
logger.addHandler(log_file_handler)
logger.addHandler(log_stream_handler)
logger.setLevel(DEBUG)

# Items will be added on other modules in order to prevent circular importing.
BIOMES = {}
GOODS = {}

working_directory = getcwd()

