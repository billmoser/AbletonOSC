from ableton.v2.control_surface import ControlSurface

from . import abletonosc

import importlib
import traceback
import logging
from . import constants

logger = logging.getLogger(constants.LOGGER_NAME)
logger.setLevel(constants.LOG_LEVEL)

if constants.LOG_FILE is not None:
    file_handler = logging.FileHandler(constants.LOG_FILE)
#    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('(%(asctime)s) [%(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

class Manager(ControlSurface):

    def __init__(self, c_instance, servers):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            self.handlers = []
            self.logger = logger
            self.logger.info('Server starting up')

            self.osc_server = abletonosc.OSCServer()
            for server in servers:
                server.setLogger(self.logger)
                server.setProcessor(self.osc_server)
                server.open()

            self.servers = servers
            self.init_api()

    def init_api(self):
        def test_callback(params):
            self.show_message("Received OSC OK")
            self.osc_server.send("/live/test", ("ok",))
        def reload_callback(params):
            self.reload_imports()
        
        self.osc_server.add_handler("/live/test", test_callback)
        self.osc_server.add_handler("/live/reload", reload_callback)

        with self.component_guard():
            self.handlers = [
                abletonosc.SongHandler(self),
                abletonosc.ApplicationHandler(self),
                abletonosc.ClipHandler(self),
                abletonosc.ClipSlotHandler(self),
                abletonosc.TrackHandler(self),
                abletonosc.DeviceHandler(self)
            ]

    def clear_api(self):
        self.osc_server.clear_handlers()
        for handler in self.handlers:
            handler.clear_api()

    def update_display(self):
        for server in self.servers:
            server.update()
        super().update_display()

    def reload_imports(self):
        try:
            importlib.reload(abletonosc.application)
            importlib.reload(abletonosc.clip)
            importlib.reload(abletonosc.clip_slot)
            importlib.reload(abletonosc.device)
            importlib.reload(abletonosc.handler)
            #importlib.reload(abletonosc.osc_server)
            importlib.reload(abletonosc.song)
            importlib.reload(abletonosc.track)
            importlib.reload(abletonosc)
        except Exception as e:
            exc = traceback.format_exc()
            logging.warning(exc)

        if self.handlers:
            self.clear_api()
            self.init_api()
        self.logger.info("Reloaded code")

    def disconnect(self):
        self.logger.info('Server shutting down')
        for server in self.servers:
            server.close()
        super().disconnect()
