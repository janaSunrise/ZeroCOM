class Message:
    def __init__(self, header, data) -> None:
        self.header = header
        self.data = data

    def __str__(self):
        return self.data.decode()
