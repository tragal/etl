import requests
from pathlib import Path
from etl.config.settings import settings

def download(run_id: str, store):
    target = settings.temp_dir / f"{run_id}.zip"
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        return target

    with requests.get("https://example.com/data.zip", stream=True, timeout=settings.request_timeout) as r:
        r.raise_for_status()
        with open(target, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    return target
