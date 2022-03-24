import select
import sys

from .config import IP, MAX_CONNECTIONS, PORT
from .models.server import Server
from .utils.contextmanagers import Timer

if __name__ == "__main__":
    # Initialize the socket
    server = Server((IP, PORT), MAX_CONNECTIONS)

    # Connect to the server
    server.connect()

    while True:
        try:
            ready_to_read, _, in_error = select.select(server.sockets_list, [], server.sockets_list)
        except KeyboardInterrupt:
            server.logger.info("Server stopping...")

            with Timer(lambda x: server.logger.success(f"Server stopped successfully in {x}ms.")):
                server.disconnect()

            sys.exit(0)

        for socket_ in ready_to_read:
            if socket_ == server.socket:
                server.process_connection()
            else:
                server.process_message(socket_)

        # Remove errored connections
        server.remove_errored_sockets(in_error)
