import zipfile
from pathlib import Path

def extract(run_id: str, zip_path: Path, store):
    last = store.get(run_id, "EXTRACT")

    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if last and name <= last:
                continue

            with zf.open(name) as f:
                yield from _read_lines(f)

            store.set(run_id, "EXTRACT", name)


def _read_lines(fileobj):
    for line in fileobj:
        yield line.decode("utf-8")
