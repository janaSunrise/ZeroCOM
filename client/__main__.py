# -- Imports --
import errno
import select
import sys
import time

from client import Client
from utils.logger import get_logging, get_message_logging

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

    # Initialize the connection, If connected
    client.initialize()

    # Print the initial message logging.
    print(get_logging("flash", "Welcome to the chat. CTRL+C to disconnect. Happy chatting\n"))

    print(get_message_logging("ME", ""), end="")

    while True:
        SOCKETS = [sys.stdin, client.socket]

        try:
            ready_to_read, ready_to_write, in_error = select.select(SOCKETS, [], [])
        except KeyboardInterrupt:
            print("\n" + get_logging("info", "Disconnecting, hold on."))

            start = time.perf_counter()

            # Close the connection
            client.disconnect()

            # Calculate the timing.
            end = time.perf_counter()
            duration = round((end - start) * 1000, 2)

            print(get_logging("success", f"Disconnected successfully in {duration}s."))
            sys.exit(0)

        for run_sock in ready_to_read:
            if run_sock == client.socket:
                try:
                    username, message = client.receive_message()

                    print("\n" + get_message_logging(username, message))
                    print(get_message_logging("ME", ""), end="")
                    sys.stdout.flush()

                except IOError as e:
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                        print(get_logging("error", f"Reading Error occurred! {str(e)}"))
                        sys.exit()

                    continue
            else:
                message = sys.stdin.readline()
                print(get_message_logging("ME", ""), end="")
                sys.stdout.flush()

                client.send_message(message)
