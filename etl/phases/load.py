from sqlalchemy.dialects.postgresql import insert
from etl.db.models import Customer
from etl.config.settings import settings

def load(run_id, rows, session, store):
    buffer = []
    last_key = store.get(run_id, "LOAD")

    for row in rows:
        if last_key and row["external_id"] <= last_key:
            continue

        buffer.append(row)

        if len(buffer) >= settings.chunk_size:
            _flush(buffer, session)
            store.set(run_id, "LOAD", buffer[-1]["external_id"])
            buffer.clear()

    if buffer:
        _flush(buffer, session)
        store.set(run_id, "LOAD", buffer[-1]["external_id"])


def _flush(rows, session):
    stmt = insert(Customer).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["external_id"],
        set_={
            "name": stmt.excluded.name,
            "email": stmt.excluded.email,
            "updated_at": stmt.excluded.updated_at,
        },
    )
    session.execute(stmt)
    session.commit()
