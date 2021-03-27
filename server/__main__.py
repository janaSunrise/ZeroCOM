# -- Imports --
import select
import socket
import sys
import time

from utils.utils import on_startup, get_color
from utils.logger import get_logging
from utils.config import IP, PORT
from server import process_conn, process_message

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
        print(get_logging("error") + f"{get_color('RED')}Server could not be initialized. Check the PORT.")
        sys.exit(1)
    else:
        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        on_startup("Server", duration, ip=IP, port=PORT)
        server_sock.listen()

        SOCKETS.append(server_sock)

        print(get_logging("success") + f"{get_color('GREEN')}Server started. Listening for connections.")

    while True:  # Main loop
        try:
            ready_to_read, ready_to_write, in_error = select.select(SOCKETS, [], SOCKETS)
        except KeyboardInterrupt:
            print(get_logging("info") + f"{get_color('MAGENTA')} Server stopping.")

            start = time.perf_counter()
            for socket in SOCKETS:
                socket.close()
            end = time.perf_counter()
            duration = round((end - start) * 1000, 2)

            print(get_logging("success") + f"{get_color('GREEN')} Server stopped successfully in {duration}s.")
            sys.exit(0)

        for socket_ in ready_to_read:
            if socket_ == server_sock:
                process_conn(socket_, SOCKETS, CLIENTS)
            else:
                process_message(socket_, SOCKETS, CLIENTS)

        for errored_socket in in_error:
            client = CLIENTS[errored_socket]
            print(
                get_logging("warning") + f"{get_color('YELLOW')}Exception occurred. Location {client.username} "
                                         f"[{client.address}]"
            )

            SOCKETS.remove(errored_socket)
            CLIENTS.pop(errored_socket)
