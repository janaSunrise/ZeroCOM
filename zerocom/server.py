from __future__ import annotations

import logging
import select
import sys
from typing import NoReturn

from zerocom.config import Config
from zerocom.network.server import Server

log = logging.getLogger(__name__)


def start_server(host: str, port: int) -> NoReturn:
    server = Server((host, port))

    while True:
        try:
            ready_to_read, _, in_error = select.select(server.socket_list, [], server.socket_list)
        except KeyboardInterrupt:
            log.info("Stopping the server...")
            server.stop()
            sys.exit(0)

        for socket_ in ready_to_read:
            if socket_ is server.socket:
                server.process_connection()
            else:
                server.process_message(socket_)

        for socket_ in in_error:
            if socket_ is not server.socket:
                server.disconnect_client(socket_)
            else:
                log.error("Server socket in error!")


if __name__ == "__main__":
    start_server(Config.IP, Config.PORT)
