import select
import sys
import time

from .config import IP, MAX_CONNECTIONS, PORT
from .models.server import Server

if __name__ == "__main__":
    # -- Perf counter --
    start = time.perf_counter()

    # Initialize the socket object
    server = Server((IP, PORT), MAX_CONNECTIONS)

    # Try the connection
    server.connect()

    while True:
        try:
            ready_to_read, _, in_error = select.select(
                server.sockets_list, [], server.sockets_list
            )
        except KeyboardInterrupt:
            server.logger.info("Server stopping...")

            start = time.perf_counter()

            # Close the connection
            server.disconnect()

            # Calculate the timing.
            end = time.perf_counter()
            duration = round((end - start) * 1000, 2)

            server.logger.success(f"Server stopped successfully in {duration}s.")
            sys.exit(0)

        for socket_ in ready_to_read:
            if socket_ == server.socket:
                server.process_connection()
            else:
                server.process_message(socket_)

        # Remove errored connections
        server.remove_errored_sockets(in_error)
