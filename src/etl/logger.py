import logging
import sys
import threading
import time


class ProgressConsole:
    """
    Writes an in-place progress bar to stdout, while allowing normal log lines
    to appear cleanly above it.
    """

    def __init__(self, stream=None, width=28):
        self.stream = stream or sys.stdout
        self.width = width
        self._lock = threading.RLock()
        self._active = False
        self._last_line = ""

    def _bar(self, percent: float) -> str:
        percent = max(0.0, min(100.0, percent))
        w = self.width
        filled = int(w * percent / 100.0)

        if percent >= 100.0:
            inside = "=" * w
        elif filled <= 0:
            inside = ">" + (" " * (w - 1))
        else:
            inside = ("=" * (filled - 1)) + ">" + (" " * (w - filled))

        return f"[{inside}] {percent:5.1f}%"

    def update(self, percent: float, prefix: str = ""):
        with self._lock:
            self._active = True
            line = (prefix + " " if prefix else "") + self._bar(percent)
            # \r return, clear line, print, no newline
            self.stream.write("\r\033[2K" + line)
            self.stream.flush()
            self._last_line = line

    def clear(self):
        with self._lock:
            if self._active:
                self.stream.write("\r\033[2K")
                self.stream.flush()
                self._last_line = ""
                self._active = False

    def newline(self):
        """Commit the progress line (print newline) and keep progress inactive."""
        with self._lock:
            if self._active:
                self.stream.write("\n")
                self.stream.flush()
                self._active = False
                self._last_line = ""


class ProgressAwareStreamHandler(logging.StreamHandler):
    """
    A console handler that clears/redraws the progress line around log records,
    so log messages don't overwrite the progress bar.
    """

    def __init__(self, progress: ProgressConsole, stream=None):
        super().__init__(stream or sys.stdout)
        self.progress = progress

    def emit(self, record):
        with self.progress._lock:
            # Remove progress line, print log line, then redraw progress line if needed
            had_progress = self.progress._active
            last = self.progress._last_line

            if had_progress:
                self.progress.clear()

            super().emit(record)

            if had_progress and last:
                # redraw exactly what was there (best-effort)
                self.stream.write("\r\033[2K" + last)
                self.stream.flush()
                self.progress._active = True
                self.progress._last_line = last


def setup_logger(log_path: str):
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    # File logger (normal)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)

    # Console logger (progress-aware)
    progress = ProgressConsole(width=24)
    ch = ProgressAwareStreamHandler(progress)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

    return logger, progress


if __name__ == "__main__":
    logger, progress = setup_logger("app.log")

    logger.info("Started erase on disk6")

    for i in range(101):
        progress.update(i, prefix="disk6")
        if i in (10, 35, 70):
            logger.info(f"Checkpoint reached: {i}%")
        time.sleep(0.03)

    progress.newline()
    logger.info("Erase complete.")
