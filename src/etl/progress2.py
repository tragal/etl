import sys
import time
import itertools


def arrow_bar(
    percent: float, width: int = 24, fill: str = "=", head: str = ">", empty: str = " "
):
    percent = max(0.0, min(100.0, percent))
    # width is the inside width (not counting brackets)
    filled = int(width * percent / 100.0)

    if percent >= 100.0:
        inside = fill * width
    elif filled <= 0:
        # head at the start
        inside = head + (empty * (width - 1))
    else:
        # fill up to filled-1, then head, then empty
        inside = (fill * (filled - 1)) + head + (empty * (width - filled))

    return f"[{inside}] {percent:5.1f}%"


def demo():
    for p in range(0, 101):
        sys.stdout.write("\r" + arrow_bar(p, width=24))
        sys.stdout.flush()
        time.sleep(0.03)
    print()  # newline


if __name__ == "__main__":
    demo()
