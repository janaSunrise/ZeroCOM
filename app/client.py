import errno
import select
import sys

from .models.client import Client
from .utils.contextmanagers import Timer

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python -m client <SERVER_IP> <PORT> <USERNAME> <PASSWORD>")
        sys.exit(1)

    _, SERVER_IP, PORT, USERNAME, PASSWORD = sys.argv
    PORT = int(PORT)

    # Initialize the client object
    client = Client((SERVER_IP, PORT), USERNAME)

    # Connect and initialize
    client.connect()
    client.initialize()

    # Print the initial message logging.
    client.logger.flash("Welcome to the chat. CTRL+C to disconnect. Happy chatting!\n")
    client.logger.message("ME", "", end="")

    while True:
        SOCKETS = [sys.stdin, client.socket]

        try:
            ready_to_read, ready_to_write, in_error = select.select(SOCKETS, [], [])
        except KeyboardInterrupt:
            print()
            client.logger.info("Disconnecting, hold on.")

            with Timer(
                lambda x: client.logger.success(f"Disconnected successfully in {x}ms.")
            ):
                client.disconnect()

            sys.exit(0)

        for run_sock in ready_to_read:
            if run_sock == client.socket:
                try:
                    username, message = client.receive_message()

                    print()
                    client.logger.message(username, message)
                    client.logger.message("ME", "", end="")

                    sys.stdout.flush()
                except IOError as e:
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                        client.logger.error(f"Error occured while reading: {str(e)}")
                        sys.exit()

                    continue
            else:
                message = sys.stdin.readline()
                client.logger.message("ME", "", end="")
                sys.stdout.flush()

                client.send_message(message)
