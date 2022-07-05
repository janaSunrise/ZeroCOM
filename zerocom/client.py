import errno
import logging
import select
import sys
from typing import NoReturn

from zerocom.network.client import Client

log = logging.getLogger(__name__)


def run_client(host: str, port: int, username: str) -> NoReturn:
    client = Client(username, (host, port))

    print("Welcome to the chat. CTRL+C to disconnect. Happy chatting.")
    print("\nME: ", end="")

    while True:
        io_descriptors = [sys.stdin, client.socket]
        try:
            ready_read, ready_write, ready_error = select.select(io_descriptors, [], [])
        except KeyboardInterrupt:
            log.info("Connection ended")
            client.socket.close()
            sys.exit(0)

        for notified_descriptor in ready_read:
            if notified_descriptor == client.socket:
                try:
                    msg = client.receive()
                except IOError as e:
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                        log.critical(f"Error occurred while reading: {e!r}")
                        sys.exit(1)
                    continue
                else:
                    log.info(f"Received message: {msg}")
                    print("ME: ", end="")
                    sys.stdout.flush()
            else:
                message = sys.stdin.readline()
                client.send(message)

                print("ME: ", end="")
                sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) != 5:
        log.critical("Usage: python -m client <SERVER_IP> <PORT> <USERNAME> <PASSWORD>")
        sys.exit(1)

    _, SERVER_IP, PORT, USERNAME, PASSWORD = sys.argv
    PORT = int(PORT)

    # NOTE: Password is currently unused, because it's not yet implemented
    run_client(SERVER_IP, PORT, USERNAME)
