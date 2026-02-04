import typer
from etl.run import run_etl

app = typer.Typer()

@app.command()
def run(run_id: str):
    run_etl(run_id)

if __name__ == "__main__":
    print("ETL CLI")
    # app()


# python -m etl.cli run --pipeline customers --run-id 2026-02-01