python -m etl.cli --help
python -m etl.cli --show-completion bash
python -m etl.cli "$(date)"
python -m etl.cli "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
printenv | sort
cd etl/
alembic init alembic
alembic current
alembic init alembic
alembic revision --autogenerate -m "initial tables"
alembic upgrade head
alembic downgrade -1