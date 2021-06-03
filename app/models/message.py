import typing as t


class Message:
    def __init__(self, header: t.Optional[bytes], data: bytes) -> None:
        self.header = header
        self.data = data

    def __str__(self):
        return self.data.decode()
