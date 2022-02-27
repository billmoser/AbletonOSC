import logging

LOGGER_NAME = "abletonosc"

# set this to location for the log file, or None for logging to Live's default file
#LOG_FILE = None
LOG_FILE = "/tmp/" + LOGGER_NAME + ".log"

LOG_LEVEL = logging.INFO

LOG_FORMAT = '(%(asctime)s) [%(levelname)s] %(message)s'

UDP_ADDRESS = ('127.0.0.1', 11000)
UDP_CLIENT_ADDRESS = ('127.0.0.1', 11001)

WS_ADDRESS = ('127.0.0.1', 55455)
