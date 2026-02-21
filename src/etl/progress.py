import sys
import time
import threading
import random
from dataclasses import dataclass, field

CSI = "\x1b["  # ANSI Control Sequence Introducer


@dataclass
class TaskState:
    name: str
    percent: float = 0.0
    status: str = "running"
    spinner_i: int = 0
    done: bool = False


class MultiProgress:
    def __init__(self, refresh_hz: float = 10.0, bar_width: int = 40):
        self.refresh_s = 1.0 / refresh_hz
        self.bar_width = bar_width
        self._lock = threading.Lock()
        self._tasks: dict[str, TaskState] = {}
        self._render_thread = None
        self._stop = threading.Event()
        self._lines_rendered = 0
        self._spinner = ["|", "/", "-", "\\"]

    def add_task(self, task_id: str, name: str):
        with self._lock:
            self._tasks[task_id] = TaskState(name=name)

    def update(
        self,
        task_id: str,
        percent: float | None = None,
        status: str | None = None,
        done: bool | None = None,
    ):
        with self._lock:
            t = self._tasks.get(task_id)
            if not t:
                return
            if percent is not None:
                t.percent = max(0.0, min(100.0, percent))
            if status is not None:
                t.status = status
            if done is not None:
                t.done = done
                if done:
                    t.status = "done"
                    t.percent = 100.0

    def remove_task(self, task_id: str):
        with self._lock:
            self._tasks.pop(task_id, None)

    def start(self):
        if self._render_thread is not None:
            return
        # Hide cursor for nicer UI
        sys.stdout.write(CSI + "?25l")
        sys.stdout.flush()

        self._render_thread = threading.Thread(target=self._render_loop, daemon=True)
        self._render_thread.start()

    def stop(self):
        self._stop.set()
        if self._render_thread:
            self._render_thread.join(timeout=1.0)
        # Move cursor to end, show cursor again
        self._move_cursor_down(self._lines_rendered)
        sys.stdout.write("\n" + CSI + "?25h")
        sys.stdout.flush()

    def _render_loop(self):
        while not self._stop.is_set():
            self.render()
            time.sleep(self.refresh_s)

    def render(self):
        with self._lock:
            tasks = list(self._tasks.items())

        # Sort stable by name (or task_id)
        tasks.sort(key=lambda kv: kv[1].name)

        lines = []
        running = sum(1 for _, t in tasks if not t.done)
        total = len(tasks)
        lines.append(f"Tasks running: {running} / total: {total}")

        for task_id, t in tasks:
            spin = self._spinner[t.spinner_i % len(self._spinner)]
            t.spinner_i += 1

            bar = self._bar(t.percent, spin if not t.done else "✓")
            lines.append(f"{bar} {t.percent:6.1f}%  {t.status:7s}  {t.name}")

        # Redraw block in-place
        self._move_cursor_up(self._lines_rendered)
        for line in lines:
            sys.stdout.write(self._clear_line() + line + "\n")

        # Clear any leftover lines from previous render (if tasks shrink)
        extra = self._lines_rendered - len(lines)
        for _ in range(max(0, extra)):
            sys.stdout.write(self._clear_line() + "\n")

        sys.stdout.flush()
        self._lines_rendered = len(lines)

    def _bar(self, percent: float, head: str):
        w = self.bar_width
        filled = int(w * percent / 100.0)
        filled = min(filled, w)
        bar = ["." for _ in range(w)]
        if percent < 100.0:
            bar[min(filled, w - 1)] = head
        else:
            bar[w - 1] = head

        # Add milestone labels like 0%, 10%, 20%...
        for m in range(0, 101, 10):
            pos = int(w * m / 100.0)
            label = f"{m}%"
            if pos + len(label) <= w:
                bar[pos : pos + len(label)] = list(label)

        return "[ " + "".join(bar) + " ]"

    def _move_cursor_up(self, n: int):
        if n > 0:
            sys.stdout.write(CSI + f"{n}A")

    def _move_cursor_down(self, n: int):
        if n > 0:
            sys.stdout.write(CSI + f"{n}B")

    def _clear_line(self):
        return CSI + "2K\r"


# --- Demo showing 5 tasks, then 4, then 6, etc. ---
def demo():
    mp = MultiProgress(refresh_hz=12, bar_width=45)
    mp.start()

    # Start with 5 tasks
    for i in range(5):
        mp.add_task(f"t{i}", f"layer {i}: pulling")

    def worker(task_id: str):
        p = 0.0
        while p < 100.0:
            p += random.uniform(0.5, 3.5)
            mp.update(task_id, percent=p, status="running")
            time.sleep(random.uniform(0.03, 0.15))
        mp.update(task_id, done=True)

    threads = []
    for i in range(5):
        th = threading.Thread(target=worker, args=(f"t{i}",), daemon=True)
        th.start()
        threads.append(th)

    # Dynamically remove/add tasks to mimic “5 then 4 then 6…”
    time.sleep(1.5)
    mp.remove_task("t1")  # e.g., task disappears from UI

    time.sleep(1.0)
    for j in range(5, 7):  # add two more
        mp.add_task(f"t{j}", f"layer {j}: extracting")
        th = threading.Thread(target=worker, args=(f"t{j}",), daemon=True)
        th.start()
        threads.append(th)

    # Wait for all threads to finish
    for th in threads:
        th.join()

    mp.stop()


if __name__ == "__main__":
    demo()
