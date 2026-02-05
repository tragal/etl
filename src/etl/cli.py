import typer
from etl.run import run_etl

app = typer.Typer()


@app.command()
def run(run_id: str):
    run_etl(run_id)


if __name__ == "__main__":
    app()


# python -m etl.cli run --pipeline customers --run-id 2026-02-01
# python -m etl.cli "$(date +"%Y-%m-%dT%H:%M:%S")"
# python -m etl.cli "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
# python -m etl.cli "$(date +%s)"
