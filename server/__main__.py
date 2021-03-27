# -- Imports --
import select
import socket
import sys
import time

from utils.utils import on_startup, get_color
from utils.logger import get_logging
from utils.config import HEADER_LENGTH, IP, PORT

SOCKETS = []
CLIENTS = {}

if __name__ == "__main__":
    # -- Perf counter --
    start = time.perf_counter()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((IP, PORT))
    except OSError:
        on_startup("Server")
        print(get_logging("error", True) + f"{get_color('RED')}Server could not be initialized. Check the PORT.")
        sys.exit(1)
    else:
        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        on_startup("Server", duration, ip=IP, port=PORT)
        server_sock.listen()

        SOCKETS.append(server_sock)

        print(get_logging("success", True) + f"{get_color('GREEN')}Server started. Listening for connections.")

    while True:  # Main loop
        try:
            ready_to_read, ready_to_write, in_error = select.select(SOCKETS, [], SOCKETS)
        except KeyboardInterrupt:
            print(get_logging("info", True) + f"{get_color('MAGENTA')} Server stopping.")

            for socket in SOCKETS:
                socket.close()
            time.sleep(1)

            print(get_logging("success", True) + f"{get_color('GREEN')} Server stopped successfully.")
            sys.exit(0)
