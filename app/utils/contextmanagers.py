import time
import typing as t
from types import TracebackType


class Timer:
    def __init__(self, display_func: t.Callable) -> None:
        self.display_func = display_func
        self.start_time = time.perf_counter()

    def __enter__(self) -> None:
        ...

    def __exit__(
        self,
        exc_type: t.Optional[TracebackType],
        exc_val: t.Optional[BaseException],
        exc_tb: t.Optional[TracebackType]
    ) -> None:
        end_time = time.perf_counter()
        duration = round((end_time - self.start_time) * 1000, 2)

        self.display_func(duration)
