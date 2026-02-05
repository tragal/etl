CREATE TABLE etl_run (
    run_id          TEXT PRIMARY KEY,
    status          TEXT NOT NULL, -- RUNNING | FAILED | COMPLETED
    current_phase   TEXT NOT NULL, -- DOWNLOAD | EXTRACT | TRANSFORM | LOAD
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    error_message   TEXT
);
