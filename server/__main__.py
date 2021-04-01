# -- Imports --
import select
import sys
import time

from utils.logger import get_logging
from utils.config import IP, PORT
from server import Server

if __name__ == "__main__":
    # -- Perf counter --
    start = time.perf_counter()

    # Initialize the socket object
    server = Server((IP, PORT))
    server.start()

    # Try the connection
    server.connect()

    while True:
        try:
            ready_to_read, _, in_error = select.select(server.sockets_list, [], server.sockets_list)
        except KeyboardInterrupt:
            print(get_logging("info", "Server stopping."))

            start = time.perf_counter()

            # Close the connection
            server.disconnect()

            # Calculate the timing.
            end = time.perf_counter()
            duration = round((end - start) * 1000, 2)

            print(get_logging("success", f"Server stopped successfully in {duration}s."))
            sys.exit(0)

        for socket_ in ready_to_read:
            if socket_ == server.socket:
                server.process_connection()
            else:
                server.process_message(socket_)

        # Remove errored connections
        server.remove_errored_sockets(in_error)
