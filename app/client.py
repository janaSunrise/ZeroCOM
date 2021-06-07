import errno
import select
import sys
import time

from .models.client import Client

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python -m client <SERVER_IP> <PORT> <USERNAME> <PASSWORD>")
        sys.exit(1)

    # -- Perf counter --
    start = time.perf_counter()

    _, SERVER_IP, PORT, USERNAME, PASSWORD = sys.argv
    PORT = int(PORT)

    # Initialize the client object
    client = Client((SERVER_IP, PORT), USERNAME)

    # Try the connection
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

            start = time.perf_counter()

            # Close the connection
            client.disconnect()

            # Calculate the timing.
            end = time.perf_counter()
            duration = round((end - start) * 1000, 2)

            client.logger.success(f"Disconnected successfully in {duration}s.")
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
                        client.logger.error(f"Reading Error occurred! {str(e)}")
                        sys.exit()

                    continue
            else:
                message = sys.stdin.readline()
                client.logger.message("ME", "", end="")
                sys.stdout.flush()

                client.send_message(message)
