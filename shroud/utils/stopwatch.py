import time
from dataclasses import dataclass

@dataclass
class Stopwatch:
    start: float | None = None
    end: float | None = None

    def __enter__(self) -> "Stopwatch":
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.end = time.perf_counter()

    @property
    def elapsed(self) -> float:
        if self.start is None:
            return 0.0
        end = self.end if self.end is not None else time.perf_counter()
        return end - self.start

    @property
    def elapsed_ms(self) -> int:
        return int(self.elapsed * 1000)
