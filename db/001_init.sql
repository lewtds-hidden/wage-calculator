BEGIN TRANSACTION;

CREATE TABLE employee (
    employee_id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE work_session (
    employee_id TEXT REFERENCES employee (employee_id),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    CONSTRAINT end_time_after_start_time CHECK (datetime(end_time) > datetime(start_time)),
    CONSTRAINT sessions_not_overlapping UNIQUE (employee_id, start_time)
);

COMMIT;