from typing import Optional
from sqlalchemy import text


class CheckpointStore:
    def __init__(self, session):
        self.session = session

    def get(self, run_id: str, phase: str) -> Optional[str]:
        row = self.session.execute(
            text(
                """
            SELECT cursor FROM etl_checkpoint
            WHERE run_id = :run_id AND phase = :phase
            """
            ),
            {"run_id": run_id, "phase": phase},
        ).fetchone()
        return row[0] if row else None

    def set(self, run_id: str, phase: str, cursor: str):
        self.session.execute(
            text(
                """
            INSERT INTO etl_checkpoint (run_id, phase, cursor)
            VALUES (:run_id, :phase, :cursor)
            ON CONFLICT (run_id, phase)
            DO UPDATE SET cursor = EXCLUDED.cursor
            """
            ),
            {"run_id": run_id, "phase": phase, "cursor": cursor},
        )
        self.session.commit()
