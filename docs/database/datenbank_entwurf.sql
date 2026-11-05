
PRAGMA foreign_keys = ON;

-- module wird zu modul
Create Table if not exists modul (
    id text primary Key not NULL
        check (length(trim(id)) > 0),
    title text not NULL
        Check( length(trim(title)) > 0),
    description TEXT,
    ects Real not NULL
        check (typeof(ects) IN ('integer', 'real') AND ects > 0),
    exam_type text, 
    completed_on text,
    -- neu hinzugefügt Lernziele merge mit Modul
    start_date text,
    end_date text,
    status text not NULL DEFAULT 'not_started'
        check (status in('not_started', 'in_progress', 'completed', 'overdue')
        ),

    check(
        completed_on is NULL OR (
            length(completed_on) = 10
            AND date(completed_on, '+0 days') IS completed_on
        ) 
    ),
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
    check( start_date is NULL OR end_date is NULL OR end_date >= start_date)
);


Create table if not exists zwischenziel (
    id integer primary key,
    title text not NULL 
        check (length(trim(title))>0),
    description text,
    modul_id text not NULL,
    start_date text,
    end_date text,
    end_time text,
    planned_study_time integer NOT NULL DEFAULT 0
        check(typeof(planned_study_time) = 'integer'
        AND planned_study_time >= 0
        ),
    status text not NULL DEFAULT 'not_started'
        check (status IN('not_started', 'in_progress','completed', 'overdue')),

    foreign key (modul_id) REFERENCES modul(id) on DELETE RESTRICT,
    UNIQUE (id, modul_id),
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
        check (
            start_date is NULL OR end_date is NULL OR end_date >= start_date
        ),
        check (end_time is NULL OR end_date is NOT NULL)
);
Create table if not exists wochenbudget (
   week_start text primary key NOT NULL,
   budget_minutes integer NOT NULL
    check(typeof(budget_minutes)= 'integer'AND budget_minutes >= 0)
);

--Speicherung der Lernzeiten jetzt geplante lernzeit!
Create table if not exists geplante_lernzeit (
    id integer primary key,
    modul_id text not NULL,
    zwischenziel_id integer,
    starts_at text NOT NULL,
    duration integer NOT NULL
        check (typeof(duration) = 'integer' AND duration > 0),
    status text NOT NULL DEFAULT 'planned'
        check(status in('planned','completed', 'cancelled')),
    
    foreign key (modul_id) REFERENCES modul(id) on DELETE RESTRICT,
    foreign key (zwischenziel_id, modul_id)
        REFERENCES zwischenziel (id, modul_id) on DELETE RESTRICT
);
Create table if not EXISTS lernzeit (
    id integer primary key,
    modul_id text NOT NULL,
    zwischenziel_id integer,
    date text NOT NULL,
    duration REAL not NULL
        check (typeof(duration) in ('integer','real') AND duration > 0),
    geplante_lernzeit_id integer,
foreign key (geplante_lernzeit_id)
    REFERENCES geplante_lernzeit(id) on DELETE RESTRICT,
foreign key (modul_id) REFERENCES modul(id) on DELETE RESTRICT,
foreign key (zwischenziel_id,modul_id)
    REFERENCES zwischenziel(id,modul_id) on DELETE RESTRICT,
        check(length(date) = 10 AND date(date, '+0 days') IS date)
);
Create INDEX if not EXISTS idx_zwischenziel_faelligkeit
    ON zwischenziel(end_date, end_time);

Create INDEX if not EXISTS idx_modul_enddatum
    ON modul(end_date);

Create INDEX if not EXISTS idx_lernzeit_modul_datum
    ON lernzeit(modul_id, date);

Create INDEX if not EXISTS idx_lernzeit_zwischenziel_id
    ON lernzeit(zwischenziel_id);

Create INDEX if not EXISTS idx_geplante_lernzeit_beginn
    ON geplante_lernzeit(starts_at);

Create INDEX if not EXISTS idx_geplante_lernzeit_modul
    ON geplante_lernzeit(modul_id, starts_at);

Create INDEX if not EXISTS idx_geplante_lernzeit_zwischenziel
    ON geplante_lernzeit(zwischenziel_id);

Create INDEX if not EXISTS idx_lernzeit_planung
    ON lernzeit(geplante_lernzeit_id);
