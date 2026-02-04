from sqlalchemy import text

class RunStore:
    def __init__(self, session):
        self.session = session

    def start(self, run_id: str):
        self.session.execute(
            text("""
            INSERT INTO etl_run (run_id, status, current_phase)
            VALUES (:run_id, 'RUNNING', 'INIT')
            ON CONFLICT (run_id) DO NOTHING
            """),
            {"run_id": run_id},
        )
        self.session.commit()

    def set_phase(self, run_id: str, phase: str):
        self.session.execute(
            text("""
            UPDATE etl_run
            SET current_phase = :phase
            WHERE run_id = :run_id
            """),
            {"run_id": run_id, "phase": phase},
        )
        self.session.commit()

    def fail(self, run_id: str, message: str):
        self.session.execute(
            text("""
            UPDATE etl_run
            SET status = 'FAILED', error_message = :msg
            WHERE run_id = :run_id
            """),
            {"run_id": run_id, "msg": message},
        )
        self.session.commit()

    def complete(self, run_id: str):
        self.session.execute(
            text("""
            UPDATE etl_run
            SET status = 'COMPLETED'
            WHERE run_id = :run_id
            """),
            {"run_id": run_id},
        )
        self.session.commit()
