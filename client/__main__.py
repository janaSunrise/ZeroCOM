# -- Imports --
import errno
import select
import socket
import sys
import time

from client import get_header, receive_message, send_message
from utils.utils import get_color, on_startup
from utils.logger import get_logging, get_message_logging

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python -m client <SERVER_IP> <PORT> <USERNAME> <PASSWORD>")
        sys.exit(1)

    # -- Perf counter --
    start = time.perf_counter()

    _, SERVER_IP, PORT, USERNAME, PASSWORD = sys.argv
    PORT = int(PORT)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_IP, PORT))
    except ConnectionRefusedError:
        on_startup("Client")
        print(get_logging("error") + f"{get_color('RED')}Connection could not be established. Invalid HOST/PORT.")
        sys.exit(1)
    else:
        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        on_startup("Client", duration)

        print(get_logging("success") + f"{get_color('GREEN')}Connected to remote host@[{SERVER_IP}:{PORT}].")

    client_socket.setblocking(False)  # So it doesn't block connections.

    # Send the specified uname.
    uname = USERNAME.encode("utf-8")
    uname_header = get_header(uname)

    # Send the message
    client_socket.send(uname_header + uname)

    print(get_message_logging("ME", ""), end="")

    while True:  # Main loop
        SOCKETS = [sys.stdin, client_socket]

        try:
            ready_to_read, ready_to_write, in_error = select.select(SOCKETS, [], [])
        except KeyboardInterrupt:
            print("\n" + get_logging("info") + f"{get_color('MAGENTA')} Disconnecting, hold on.")

            start = time.perf_counter()
            client_socket.close()
            end = time.perf_counter()
            duration = round((end - start) * 1000, 2)

            print(get_logging("success") + f"{get_color('GREEN')} Disconnected successfully in {duration}s.")
            sys.exit(0)

        for run_sock in ready_to_read:
            if run_sock == client_socket:
                try:
                    username, message = receive_message(client_socket)

                    print("\n" + get_message_logging(username, message))
                    print(get_message_logging("ME", ""), end="")
                    sys.stdout.flush()

                except IOError as e:
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                        print(get_logging("error") + f"Reading Error occurred! {str(e)}")
                        sys.exit()

                    continue
            else:
                message = sys.stdin.readline()
                print(get_message_logging("ME", ""), end="")
                sys.stdout.flush()

                send_message(message, client_socket)
