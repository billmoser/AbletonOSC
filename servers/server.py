import logging

class Server:

    def __init__(self, tag):
        self.tag = tag
        self.logger = logging.getLogger("Server-" + tag)
        self.logger.info('init')

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

    