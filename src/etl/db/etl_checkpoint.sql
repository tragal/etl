CREATE TABLE etl_checkpoint (
    run_id      TEXT NOT NULL,
    phase       TEXT NOT NULL,
    cursor      TEXT NOT NULL,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, phase)
);
