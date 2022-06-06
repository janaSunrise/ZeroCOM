def get_header(message: bytes, header_length: int) -> bytes:
    return f"{len(message):<{header_length}}".encode()
