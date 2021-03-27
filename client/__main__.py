# -- Imports --
import socket
import sys
import time

from utils.utils import get_color, on_startup
from utils.logger import get_logging

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python -m client <SERVER_IP> <PORT> <USERNAME> <PASSWORD>")
        sys.exit(1)

    # -- Perf counter --
    start = time.perf_counter()

    _, SERVER_IP, PORT, USERNAME, PASSWORD = sys.argv
    PORT = int(PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((SERVER_IP, PORT))
    except ConnectionRefusedError:
        on_startup("Client")
        print(get_logging("error", True) + f"{get_color('RED')}Connection could not be established. Invalid HOST/PORT.")
        sys.exit()
    else:
        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        on_startup("Client", duration)

        print(get_logging("success", True) + f"{get_color('GREEN')}Connected to remote host.")

    sock.setblocking(False)  # So it doesn't block connections.
