import logging

class Publisher:
    # address of current client whose message is being processed
    _client_addr = None

    # reference to server for current client
    _server = None

    # for 'subscriptions" like the {start/stop}_listen addresses
    _listeners = {}

    def __init__(self):
        self.logger = logging.getLogger("abletonosc")

    def setCurrentMessageEndpoints(self, server, client_addr):
        self._server = server
        self._client_addr = client_addr

    def add_listener(self, key):
        if not key in self._listeners:
            self._listeners[key] = []
        self._listeners[key].append((self._server, self._client_addr))
        self.logger.info("added listener %s" % str(self._client_addr))
        self.logger.info("num listeners for %s is now %d" % (str(key), len(self._listeners[key])) )

    def hasListeners(self, key):
        return key in self._listeners

    def remove_listener(self, key):
        self._listeners[key].remove((self._server, self._client_addr))
        self.logger.info(self._listeners[key])
        self.logger.info("removed listener %s" % str(self._client_addr))
        self.logger.info("num listeners for %s is now %d" % (str(key), len(self._listeners[key])) )
        if len(self._listeners[key]) == 0:
            self._listeners.pop(key)
        

    def publish(self, key, message):
        if key in self._listeners:
            for (server, client_addr) in self._listeners[key]:
                try:
                    server.send(message, client_addr)
                except Exception as e:
                    self.logger.info(e)
                    self.remove_listener(key)
