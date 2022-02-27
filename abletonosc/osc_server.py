from typing import Tuple, Any, Callable
from ..lib.pythonosc.osc_message import OscMessage, ParseError
from ..lib.pythonosc.osc_message_builder import OscMessageBuilder, BuildError
import logging
import traceback

def toOscMessage(address: str, params: Tuple[Any] = ()):
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
    except BuildError as e:
        ##self.logger.info("AbletonOSC: OSC build error: %s" % (traceback.format_exc()))
        raise e

    return msg

class OSCServer:

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

    def process(self, data): ## client_addr, server):
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
            rv = toOscMessage(message.address, rv)
            

        return rv