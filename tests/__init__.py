import time
import pytest
import threading
from collections.abc import Iterable
from typing import Union
from ..lib.pythonosc.dispatcher import Dispatcher
from ..lib.pythonosc.osc_server import ThreadingOSCUDPServer
from ..lib.pythonosc.osc_message_builder import OscMessageBuilder

REMOTE_PORT = 11000
SERVER_PORT = 11001

# Live tick is 100ms. Wait for this long plus a short additional buffer.
#TICK_DURATION = 0.11
TICK_DURATION = 0.15 # because Windows 11 is a dog

def send_message(server, address: str, value: Union[int, float, bytes, str, bool, tuple, list]) -> None:
        """Build :class:`OscMessage` from arguments and send to server

        Args:
            address: OSC address the message shall go to
            value: One or more arguments to be added to the message
        """
        builder = OscMessageBuilder(address=address)
        if value is None:
            values = []
        elif not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
            values = [value]
        else:
            values = value
        for val in values:
            builder.add_arg(val)
        msg = builder.build()
        server.socket.sendto(msg.dgram,('127.0.0.1', REMOTE_PORT))

@pytest.fixture(scope="module")
def server():
    dispatcher = Dispatcher()
    server = ThreadingOSCUDPServer(("127.0.0.1", SERVER_PORT), dispatcher)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    yield server

    server.shutdown()
    server_thread.join()

def query_and_await(server, address, fn):
    send_message(server, address, [])
    return await_reply(server, address, fn)

def await_reply(server, address, fn, timeout=TICK_DURATION):
    event = threading.Event()
    def received_response(address, *params):
        print("RECEIVED: %s" % str(params))
        if fn(address, *params):
            nonlocal event
            event.set()
    server.dispatcher.map(address, received_response)
    event.wait(timeout)
    print(timeout)
    return event.is_set()

def wait_one_tick():
    time.sleep(TICK_DURATION)
