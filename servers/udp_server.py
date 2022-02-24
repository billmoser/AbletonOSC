import socket
import errno
from .server import Server

TAG = 'udp'
BUFFER_SIZE = 65536

class UdpServer(Server):

    def __init__(self, addr):
        super().__init__(TAG)
        self._addr = addr

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
                result = self.processor.process(data, addr, self)
                if result != None:
                    self.send(result, addr)

    def send(self, message, destination):
        self.socket.sendto(message, destination)

    def open(self):
        try:
            self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(self._addr)
            self.socket.setblocking(0)
        except Exception as e:
            self.logger('Error: ', e)
        else:
            self.logger.info('Connected: %s:%d' % self._addr)

    def close(self):
        self.socket.close()
