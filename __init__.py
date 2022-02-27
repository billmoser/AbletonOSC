try:
    from .manager import Manager
except ImportError as e:
    # This is needed for unit tests to work through pytest.
    # Otherwise, pytest will attempt and fail to import this __init__.py
    exception_str = str(e)
    if "bad magic number" in exception_str:
        pass
    if "No module named \'past\'" in exception_str:
        pass
    else:
        raise e
else:
    from . import constants
    from . import servers
    def create_instance(c_instance):
        return Manager(c_instance, [
            servers.UdpServer(constants.UDP_ADDRESS, constants.UDP_CLIENT_ADDRESS),
            servers.WsServer(constants.WS_ADDRESS)
        ])
