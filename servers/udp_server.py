import socket
import errno
from ..lib.pythonosc.osc_message_builder import OscMessageBuilder, BuildError
from .server import Server

TAG = 'UDP'
BUFFER_SIZE = 65536


msg_builder = OscMessageBuilder("/ping")
ping_dgram = None
try:
    ping_dgram= msg_builder.build().dgram
except BuildError as e:
    raise e


class UdpServer(Server):

    _queue = []

    _clients = {}

    _client_error = False

    def __init__(self, addr):
        super().__init__(TAG)
        self._addr = addr

    def update(self):

        if self._client_error:
            self.revise_clients()
        self._client_error = False

        for (data, addr) in self._queue:
            result = self.processor.process(data, addr, self)
            if result != None:
                self.send(result, addr)
        self._queue = []

        while True:
            try:
                (data, addr) = self.socket.recvfrom(BUFFER_SIZE)
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    return
                else:
                    self._client_error = True
                    raise Exception('udp receive error', err)
            else:
                self._clients[addr] = 1 # just assign something
                result = self.processor.process(data, addr, self)
                if result != None:
                    self.send(result, addr)
        

    def send(self, message, destination):
        if destination in self._clients:
            self.logger.info(self.tag + " sending: " + str(message) + ', ' + str(destination))
            try:
                self.socket.sendto(message, destination)
            except Exception as e:
                raise e
        else:
            self.logger.warning(self.tag + ' cannot send to %s:%d' % destination)

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

    def has_client(self, client_addr):
        return client_addr in self._clients

    def revise_clients(self):
        remove_list = []
        for client_addr in self._clients:
            self.socket.sendto(ping_dgram, client_addr)
            try:
                (data, addr) = self.socket.recvfrom(BUFFER_SIZE)
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    pass
                else:
                    self.logger.warning(self.tag + ' Removing: %s:%d' % client_addr)
                    remove_list.append(client_addr)
            else:
                self._queue.append((data, addr))

        for client_addr in remove_list:
            del self._clients[client_addr]
                    

