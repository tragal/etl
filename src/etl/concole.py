import sys
import time
import itertools


def render_progress(percent, spinner_char, width=50):
    percent = max(0.0, min(100.0, percent))

    filled = int(width * percent / 100)
    bar = ["."] * width

    # Place spinner at current position (if not complete)
    if percent < 100:
        bar[min(filled, width - 1)] = spinner_char

    # Insert milestone labels (0%, 10%, 20%, ...)
    for milestone in range(0, 101, 10):
        pos = int(width * milestone / 100)
        label = f"{milestone}%"
        if pos + len(label) <= width:
            bar[pos : pos + len(label)] = list(label)

    return f"[ {''.join(bar)} ] {percent:5.1f}%"


def simulate_erase(disk_name):
    print(f"Started erase on {disk_name}")

    spinner = itertools.cycle(["|", "/", "-", "\\"])

    for i in range(101):
        line = render_progress(i, next(spinner))
        sys.stdout.write("\r" + line)
        sys.stdout.flush()
        time.sleep(0.05)

    print("\nErase complete.")


if __name__ == "__main__":
    simulate_erase("disk6")
