from etl.db.database import Session
from etl.metadata.run_store import RunStore
from etl.metadata.checkpoint_store import CheckpointStore
from etl.phases.download import download
from etl.phases.extract import extract
from etl.phases.transform import transform
from etl.phases.load import load

import sys
import sqlalchemy

# def run_etl(run_id: str, pipeline_name: str):
#     pipeline = load_pipeline(pipeline_name)
#
#     for phase_name, phase_fn in pipeline:
#         run_phase(run_id, phase_name, phase_fn)


def run_etl(run_id: str):
    session = Session()
    run_store = RunStore(session)
    checkpoint = CheckpointStore(session)

    try:
        # If the DB is unreachable, catch the connection error here and bail out
        try:
            run_store.start(run_id)
        except sqlalchemy.exc.OperationalError as db_exc:
            print(
                f"Database connection error while starting run: {db_exc}",
                file=sys.stderr,
            )
            return

        run_store.set_phase(run_id, "DOWNLOAD")
        zip_path = download(run_id, checkpoint)

        run_store.set_phase(run_id, "EXTRACT")
        lines = extract(run_id, zip_path, checkpoint)

        run_store.set_phase(run_id, "TRANSFORM")
        rows = transform(lines)

        run_store.set_phase(run_id, "LOAD")
        load(run_id, rows, session, checkpoint)

        run_store.complete(run_id)

    except Exception as exc:
        # run_store.fail(run_id, str(exc))
        # Try to record the failure in the DB, but don't allow DB errors here to explode
        try:
            run_store.fail(run_id, str(exc))
        except sqlalchemy.exc.SQLAlchemyError as db_exc:
            print(
                f"Database error while recording run failure: {type(db_exc).__name__}: {db_exc}",
                file=sys.stderr,
            )
            return
        except Exception as err:
            print(
                f"Error while recording run failure: {type(err).__name__}: {db_exc}",
                file=sys.stderr,
            )
            return

        raise
    finally:
        session.close()
