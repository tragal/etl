import logging
import sys
import threading
import time


class ProgressBar:
    """Single-line interactive progress bar that coexists with console logs."""

    def __init__(self, width: int = 24, stream=None):
        self.width = width
        self.stream = stream or sys.stdout
        self._lock = threading.RLock()
        self._active = False
        self._last = ""

    def _render(self, percent: float, prefix: str = "") -> str:
        percent = max(0.0, min(100.0, percent))
        w = self.width
        filled = int(w * percent / 100.0)

        if percent >= 100.0:
            inside = "=" * w
        elif filled <= 0:
            inside = ">" + (" " * (w - 1))
        else:
            inside = ("=" * (filled - 1)) + ">" + (" " * (w - filled))

        bar = f"[{inside}] {percent:5.1f}%"
        return f"{prefix} {bar}".rstrip()

    def update(self, percent: float, prefix: str = ""):
        with self._lock:
            self._active = True
            line = self._render(percent, prefix=prefix)
            # carriage return + clear line + redraw (no newline)
            self.stream.write("\r\033[2K" + line)
            self.stream.flush()
            self._last = line

    def clear(self):
        with self._lock:
            if self._active:
                self.stream.write("\r\033[2K")
                self.stream.flush()
                self._active = False
                self._last = ""

    def finish(self, final_line: str | None = None):
        """Optionally print a final line and end with newline."""
        with self._lock:
            if self._active:
                self.stream.write("\r\033[2K")
            if final_line:
                self.stream.write(final_line)
            self.stream.write("\n")
            self.stream.flush()
            self._active = False
            self._last = ""


class ProgressAwareConsoleHandler(logging.StreamHandler):
    """
    Console log handler that doesn't corrupt the interactive progress bar.
    It temporarily clears the bar, prints the log line, then redraws the bar.
    """

    def __init__(self, progress: ProgressBar, stream=None):
        super().__init__(stream or sys.stdout)
        self.progress = progress

    def emit(self, record):
        with self.progress._lock:
            had = self.progress._active
            last = self.progress._last

            if had:
                self.progress.clear()

            super().emit(record)

            if had and last:
                self.stream.write("\r\033[2K" + last)
                self.stream.flush()
                self.progress._active = True
                self.progress._last = last


def setup_logger(log_path: str, progress: ProgressBar) -> logging.Logger:
    logger = logging.getLogger("etl")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    # File handler (persistent record)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)

    # Console handler (human output, progress-safe)
    ch = ProgressAwareConsoleHandler(progress)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

    return logger


if __name__ == "__main__":
    progress = ProgressBar(width=28)
    logger = setup_logger("etl.log", progress)

    logger.info("Started erase on disk6")

    for i in range(101):
        progress.update(i, prefix="disk6")
        if i in (10, 35, 70):
            logger.info(f"Checkpoint reached: {i}%")
        time.sleep(0.03)

    progress.finish("disk6 erase complete")
    logger.info("All done (also in file).")
