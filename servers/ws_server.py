from ..lib.simple_websocket_server.SimpleWebSocketServer import WebSocket, SimpleWebSocketServer
from .server import Server

TAG = 'WS'
inQueue = []

class QueueingHandler(WebSocket):
    def handleMessage(self):
        inQueue.append((self, self.data))

    def handleConnected(self):
        pass

    def handleClose(self):
        pass

class WsServer(Server):

    def __init__(self, addr):
        super().__init__(TAG)
        self._addr = addr

    def update(self):
        self.server.serveonce()

        while len(inQueue) > 0:
            item = inQueue.pop(0)
            sock = item[0]
            data = item[1]
            result = self.processor.process(data, sock, self)
            if result != None:
                self.send(result, sock)

    def send(self, message, destination):
        self.logger.info(self.tag + " sending: " + str(message) + ', ' + str(destination))
        try:
            destination.sendMessage(message)
        except Exception as e:
            raise e

    def open(self):
        try:
            host, port = self._addr
            self.server = SimpleWebSocketServer(host.encode('utf-8'), port, QueueingHandler)
        except Exception as e:
            self.logger.info(e)
        else:
            self.logger.info(self.tag + ' Connected: %s:%d' % self._addr)

    def close(self):
        self.server.close()
