import socket
import errno
from .server import Server

TAG = 'UDP'
BUFFER_SIZE = 65536

class UdpServer(Server):

    def __init__(self, addr, client_addr):
        super().__init__(TAG)
        self._addr = addr
        self._client_addr = client_addr

    def update(self):

        while True:
            try:
                (data, addr) = self.socket.recvfrom(BUFFER_SIZE)
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    return
                else:
                    raise Exception('udp receive error', err)
            else:
                self.publisher.setCurrentMessageEndpoints(self, self._client_addr)
                result = self.processor.process(data)
                if result != None:
                    self.send(result, self._client_addr)
        

    def send(self, message, destination):
        self.logger.info(self.tag + " sending: " + str(message) + ', ' + str(destination))
        try:
            self.socket.sendto(message, destination)
        except Exception as e:
                raise e

    def open(self):
        try:
            self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.socket.bind(self._addr)
            self.socket.setblocking(0)
            self._queue = []
            self._client_error = False
        except Exception as e:
            raise e
        else:
            self.logger.info(self.tag + ' Connected: %s:%d' % self._addr)

    def close(self):
        self.socket.close()

