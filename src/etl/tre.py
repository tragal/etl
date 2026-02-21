import logging
import sys
import time
import threading
import random
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

CSI = "\x1b["  # ANSI escape prefix


@dataclass
class TaskState:
    name: str
    percent: float = 0.0
    status: str = "running"
    done: bool = False


class MultiProgress:
    """
    Multi-line progress UI (one line per task). Safe to call update() from worker threads.
    A dedicated render thread redraws the block periodically.
    """

    def __init__(self, bar_width: int = 24, refresh_hz: float = 10.0, stream=None):
        self.bar_width = bar_width
        self.refresh_s = 1.0 / refresh_hz
        self.stream = stream or sys.stdout

        self._lock = threading.RLock()
        self._tasks: dict[str, TaskState] = {}

        self._stop = threading.Event()
        self._render_thread: threading.Thread | None = None
        self._lines_rendered = 0

        self._active = False  # UI block currently displayed

    # ---------- Task lifecycle ----------
    def add_task(self, task_id: str, name: str):
        with self._lock:
            self._tasks[task_id] = TaskState(name=name)

    def update(
        self, task_id: str, percent: float | None = None, status: str | None = None
    ):
        with self._lock:
            t = self._tasks.get(task_id)
            if not t:
                return
            if percent is not None:
                t.percent = max(0.0, min(100.0, float(percent)))
            if status is not None:
                t.status = status

    def mark_done(self, task_id: str, status: str = "done"):
        with self._lock:
            t = self._tasks.get(task_id)
            if not t:
                return
            t.done = True
            t.status = status
            t.percent = 100.0

    def remove_task(self, task_id: str):
        with self._lock:
            self._tasks.pop(task_id, None)

    # ---------- UI control ----------
    def start(self):
        if self._render_thread is not None:
            return
        self._active = True
        # hide cursor
        self.stream.write(CSI + "?25l")
        self.stream.flush()
        self._render_thread = threading.Thread(target=self._render_loop, daemon=True)
        self._render_thread.start()

    def stop(self):
        self._stop.set()
        if self._render_thread:
            self._render_thread.join(timeout=1.0)

        # clear UI block
        with self._lock:
            self._move_cursor_up(self._lines_rendered)
            for _ in range(self._lines_rendered):
                self.stream.write(self._clear_line() + "\n")
            self.stream.flush()
            self._lines_rendered = 0
            self._active = False

        # show cursor
        self.stream.write(CSI + "?25h")
        self.stream.flush()

    def _render_loop(self):
        while not self._stop.is_set():
            self.render()
            time.sleep(self.refresh_s)

    def render(self):
        with self._lock:
            items = list(self._tasks.items())

        # stable display order
        items.sort(key=lambda kv: kv[1].name)

        running = sum(1 for _, t in items if not t.done)
        total = len(items)

        lines: list[str] = []
        lines.append(f"Threads running: {running}/{total}")

        for task_id, t in items:
            bar = self._bar(t.percent)
            lines.append(f"{bar} {t.percent:6.1f}%  {t.status:8s}  {t.name}")

        with self._lock:
            # redraw block in-place
            self._move_cursor_up(self._lines_rendered)

            for line in lines:
                self.stream.write(self._clear_line() + line + "\n")

            # clear leftover lines if UI shrank
            extra = self._lines_rendered - len(lines)
            for _ in range(max(0, extra)):
                self.stream.write(self._clear_line() + "\n")

            self.stream.flush()
            self._lines_rendered = len(lines)
            self._active = True

    def clear_once(self):
        """Clear the UI block (used by console logging handler)."""
        with self._lock:
            if not self._active:
                return
            self._move_cursor_up(self._lines_rendered)
            for _ in range(self._lines_rendered):
                self.stream.write(self._clear_line() + "\n")
            self.stream.flush()
            self._move_cursor_up(self._lines_rendered)

    # ---------- Bar rendering ----------
    def _bar(self, percent: float) -> str:
        percent = max(0.0, min(100.0, percent))
        w = self.bar_width
        filled = int(w * percent / 100.0)

        if percent >= 100.0:
            inside = "=" * w
        elif filled <= 0:
            inside = ">" + (" " * (w - 1))
        else:
            inside = ("=" * (filled - 1)) + ">" + (" " * (w - filled))

        return "[" + inside + "]"

    # ---------- ANSI helpers ----------
    def _move_cursor_up(self, n: int):
        if n > 0:
            self.stream.write(CSI + f"{n}A")

    def _clear_line(self) -> str:
        return CSI + "2K\r"


class UIAwareConsoleHandler(logging.StreamHandler):
    """
    Clears the UI block before printing a log line, then re-renders the UI.
    """

    def __init__(self, ui: MultiProgress, stream=None):
        super().__init__(stream or sys.stdout)
        self.ui = ui

    def emit(self, record):
        with self.ui._lock:
            self.ui.clear_once()
            super().emit(record)
            # re-render immediately after the log line
            self.ui.render()


def setup_logger(log_path: str, ui: MultiProgress) -> logging.Logger:
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)

    ch = UIAwareConsoleHandler(ui)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

    return logger


# ---- Example worker using per-thread progress updates ----
def worker(task_id: str, ui: MultiProgress, logger: logging.Logger) -> str:
    ui.update(task_id, percent=0.0, status="running")

    # Simulate work in chunks (replace with your real job)
    p = 0.0
    steps = random.randint(25, 60)
    for _ in range(steps):
        # do work...
        time.sleep(random.uniform(0.02, 0.12))

        p += 100.0 / steps
        ui.update(task_id, percent=p)

        # occasional log line
        if random.random() < 0.03:
            logger.info(f"{task_id}: processed chunk")

    ui.mark_done(task_id)
    return f"{task_id} OK"


def main():
    ui = MultiProgress(bar_width=24, refresh_hz=12)
    logger = setup_logger("etl.log", ui)

    ui.start()
    logger.info("Starting threaded jobs...")

    task_ids = [f"t{i}" for i in range(6)]  # e.g., 6 concurrent jobs

    # Register tasks in the UI
    for tid in task_ids:
        ui.add_task(tid, name=f"job {tid}")

    results = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        future_to_tid = {ex.submit(worker, tid, ui, logger): tid for tid in task_ids}

        for fut in as_completed(future_to_tid):
            tid = future_to_tid[fut]
            try:
                res = fut.result()
                results.append(res)
                logger.info(f"Completed: {tid}")
            except Exception as e:
                ui.update(tid, status="error")
                logger.info(f"Failed: {tid} ({e})")

    logger.info("All jobs finished.")
    ui.stop()

    # Print final results (optional)
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
