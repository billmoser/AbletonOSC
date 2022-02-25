from typing import Tuple, Any, Callable
from ..lib.pythonosc.osc_message import OscMessage, ParseError
from ..lib.pythonosc.osc_message_builder import OscMessageBuilder, BuildError

import logging
import traceback

class OSCServer:

    # address of current client whose message is being processed
    _client_addr = None

    # reference to server for current client
    _server = None

    # for 'subscriptions" like the {start/stop}_listen addresses
    _listeners = {}

    def __init__(self):
        self._callbacks = {}
        self.logger = logging.getLogger("abletonosc")

    def add_handler(self, address: str, handler: Callable):
        self._callbacks[address] = handler

    def clear_handlers(self):
        self._callbacks = {}
        self._client_addr = None
        self._server = None
        self._listeners = {}

    def toOscMessage(self, address: str, params: Tuple[Any] = ()):
        """
        Builds and returns an OSC message.

        Args:
            address: The OSC address (e.g. /frequency)
            params: A tuple of zero or more OSC params
        """
        msg_builder = OscMessageBuilder(address)
        for param in params:
            msg_builder.add_arg(param)

        msg = None
        try:
            msg = msg_builder.build()
            msg = msg.dgram
        except BuildError:
            self.logger.info("AbletonOSC: OSC build error: %s" % (traceback.format_exc()))

        return msg

    def process(self, data, client_addr, server):
        self._client_addr = client_addr
        self._server = server
        rv = None
        try:
            message = OscMessage(data)

            if message.address in self._callbacks:
                callback = self._callbacks[message.address]
                rv = callback(message.params)
            else:
                self.logger.info("AbletonOSC: Unknown OSC address: %s" % message.address)

        except ParseError:
            self.logger.info("AbletonOSC: OSC parse error: %s" % (traceback.format_exc()))

        except Exception as e:
            self.logger.info("AbletonOSC: Error handling message: %s" % (traceback.format_exc()))

        if rv != None:
            if (type(rv) is not tuple) and (type(rv) is not list):
                rv = (rv,)
            rv = self.toOscMessage(message.address, rv)

        return rv

    #
    ##  These next few are all to support pub sub (start/stop _listener addresses)
    #

    def add_listener(self, key):
        if not key in self._listeners:
            self._listeners[key] = []
        self._listeners[key].append((self._server, self._client_addr))
        self.logger.info(self._listeners[key] )

    def hasListeners(self, key):
        return key in self._listeners

    def remove_listener(self, key, server = None, client_addr = None):
        if server == None:
            server = self._server
        if client_addr == None:
            client_addr = self._client_addr
        self._listeners[key].remove((self._server, self._client_addr))
        self.logger.info(self._listeners[key])
        if len(self._listeners[key]) == 0:
            self._listeners.pop(key)

    def publish(self, key, address, args):
        removeList = []
        if key in self._listeners:
            value = self.toOscMessage(address, args)
            for (server, client_addr) in self._listeners[key]:
                if server.has_client(client_addr):
                    server.send(value, client_addr)
                else:
                    removeList.append((server, client_addr))
            for (server, client_addr) in removeList:
                self.remove_listener(key, server, client_addr)

