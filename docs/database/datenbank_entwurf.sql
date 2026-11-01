-- LERNZEIT_MANAGER_ENTWURF


PRAGMA foreign_keys = ON;
Begin Transaction;



Create Table if not exists module (
    id text primary Key not NULL
        check (length(trim(id)) > 0),
    title text not NULL
        Check( length(trim(title)) > 0),
    ects Real not NULL
        check (typeof(ects) IN ('integer', 'real') AND ects > 0),
    exam_type text,
    completed_on text,

    -- NULL ==> Modul wurde (noch) nicht abgeschlossen

    check(
        completed_on is NULL OR (
            length(completed_on) = 10
            AND date(completed_on, '+0 days') IS completed_on
        )
    )
);


Create Table if not exists lernziele (
    id integer primary key,
    title text not NULL
        check(length(trim(title)) > 0),

    description text,
    module_id text not NULL,

    start_date text,
    end_date text,

    accumulated_study_time_min integer not NULL DEFAULT 0
        check(
            typeof(accumulated_study_time_min) = 'integer'
            AND accumulated_study_time_min >= 0
        ),

    status text not NULL DEFAULT 'not_started'
        check (status in('not_started', 'in_progress', 'completed', 'overdue')),


    foreign key (module_id) REFERENCES module(id) ON DELETE RESTRICT,
    check (
        start_date is NULL OR (
            length(start_date) = 10
            AND date(start_date, '+0 days') IS start_date
        )
    ),
    check ( end_date is NULL OR(
        length(end_date) = 10
        AND date(end_date,'+0 days') is end_date
    )
    ),
    check (start_date is NULL OR end_date is NULL OR end_date >= start_date)
);


Create table if not exists zwischenziele (
    id integer primary key,
    title text not NULL
        check (length(trim(title))>0),
    description text,
    lernziel_id integer not NULL,
        start_date text,
        end_date text,
        accumulated_study_time_min integer not NULL DEFAULT 0
        check (
            typeof(accumulated_study_time_min) = 'integer'
            AND accumulated_study_time_min >= 0
        ),
    status text not NULL DEFAULT 'not_started'
        check (status IN('not_started', 'in_progress','completed', 'overdue')),

    foreign key (lernziel_id) REFERENCES lernziele(id) on DELETE RESTRICT,

    UNIQUE (id, lernziel_id),
        check(
            start_date is NULL OR (
                length(start_date)= 10
                AND date(start_date, '+0 days') is start_date
            )
        ),
        check (
            end_date is NULL OR (
                length(end_date) = 10
                AND date(end_date, '+0 days') is end_date
            )
        ),
        check (start_date is NULL OR end_date is NULL OR end_date >= start_date)
);

--Speicherung der Lernzeiten
Create table if not exists lernzeiten (
    id integer primary key,
    lernziel_id integer not NULL,
    zwischenziel_id integer,
    date text not NULL,
    duration integer not NULL
        check (typeof(duration) = 'integer' AND duration >0),

    foreign key (lernziel_id) REFERENCES lernziele(id) on DELETE RESTRICT,
    foreign key (zwischenziel_id, lernziel_id)

    REFERENCES zwischenziele (id, lernziel_id) on DELETE RESTRICT,
    check (length(date) = 10 AND date(date,'+0 days') IS date)

);

Create INDEX if not EXISTS idx_lernziele_module_id
    ON lernziele(module_id);

Create INDEX if not EXISTS idx_zwischenziele_lernziel_id
    ON zwischenziele(lernziel_id);

Create INDEX if not EXISTS idx_lernzeiten_lernziel_datum
    ON lernzeiten(lernziel_id, date);

Create INDEX if not EXISTS idx_lernzeiten_zwischenziel_id
    ON lernzeiten(zwischenziel_id);

COMMIT;
