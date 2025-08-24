import time

class Stopwatch:
    """
    Simple stopwatch utility for timing code execution.
    """
    def __init__(self):
        self._start_time = None

    def start(self):
        """Start the timer."""
        self._start_time = time.time()

    def stop(self) -> float:
        """Stop the timer and return elapsed seconds."""
        if self._start_time is None:
            return 0.0
        elapsed = time.time() - self._start_time
        self._start_time = None
        return elapsed
