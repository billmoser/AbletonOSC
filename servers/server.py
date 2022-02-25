import logging
from .. import constants

class Server:

    logger = None

    def __init__(self, tag):
        self.tag = tag

    def setLogger(self, logger):
        self.logger = logger
    
    def setProcessor(self, processor):
        self.processor = processor

    def update(self):
        pass

    def send(self, message, destination):
        pass

    def open(self):
        pass

    def close(self):
        pass
    