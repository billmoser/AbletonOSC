from ..lib.simple_websocket_server.SimpleWebSocketServer import WebSocket, SimpleWebSocketServer
from .server import Server

TAG = 'WS'
inQueue = []

class QueueingHandler(WebSocket):
    def handleMessage(self):
        inQueue.append(('data', self, self.data))

    def handleConnected(self):
        inQueue.append(('connected', self))

    def handleClose(self):
        inQueue.append(('closed', self))

class WsServer(Server):

    def __init__(self, addr):
        super().__init__(TAG)
        self._addr = addr

    def update(self):
        self.server.serveonce()

        while len(inQueue) > 0:
            item = inQueue.pop(0)
            if (item[0] == 'data'):
                sock = item[1]
                data = item[2]
                self.logger.info('processing ' + self.tag + " - " + str(sock) + ', ' + str(data))
                self.publisher.setCurrentMessageEndpoints(self, sock)
                result = self.processor.process(data)
                if result != None:
                    self.send(result, sock)
            else:
                q = item[1]
                self.logger.info(self.tag + " - " + item[0] + ':: ' +
                    str(q.server) + ', ' + str(q.client) + ', ' + str(q.address))

    def send(self, message, destination):
        self.logger.info(self.tag + " sending: " + str(message) + ', ' + str(destination))
        try:
            destination.sendMessage(message)
        except Exception as e:
            raise e

    def open(self):
        #bloop = self.logger
        try:
            host, port = self._addr
            self.server = SimpleWebSocketServer(host.encode('utf-8'), port, QueueingHandler)
        except Exception as e:
            self.logger.info(e)
        else:
            self.logger.info(self.tag + ' Connected: %s:%d' % self._addr)

    def close(self):
        self.server.close()
