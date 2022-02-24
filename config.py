from . import servers

UDP_ADDRESS = ('127.0.0.1', 11000)
WS_ADDRESS = ('127.0.0.1', 55455)

server_list = [
    servers.UdpServer(UDP_ADDRESS),
    servers.WsServer(WS_ADDRESS)
]
