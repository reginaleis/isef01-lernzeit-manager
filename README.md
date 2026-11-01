# isef01-lernzeit-manager

## Contribute

Install dependencies

```
pip install uv
uv venv
source .venv/bin/activate
uv sync
```

### CI/CD

Every push and and PR to main will run some code quality checks (ruff linting, formatting and mypy typing).

A pre-commit hook is in place:
```
pip install pre-commit
pre-commit install
```

### Manually Deploy and Test UI

Run App
```
uvicorn isef01_lernzeit_manager.main:app --reload
```

### Code Architecture & Project Structure

This section describes the code architecture under `src/isef01_lernzeit_manager`

```mermaid
flowchart TB
    API["API Layer"]
    Services["Business Logic / Services"]
    DAL["Data Access Layer"]
    Frontend["Frontend<br>(Client)"]
    Database[("Database")]

    API --> Services
    Services --> DAL
    DAL --> Database
    Frontend --> API

    style Frontend color:#ffffff,fill:#a78bfa,stroke:#a78bfa
    style Services color:#ffffff,stroke-width:0px,stroke-dasharray:0,fill:#2dd4bf
    style DAL color:#ffffff,fill:#6a8cf2,stroke-width:0px,stroke-dasharray:0
    style API color:#ffffff,fill:#fb923c,stroke:#FFE0B2
    style Database color:#334155,fill:#e2e8f0,stroke:#64748b
```




| Block | Location in this project | Stack | Responsibility |
| --- | --- | --- | --- |
| **Frontend** | [`templates/`](src/isef01_lernzeit_manager/templates/index.html) and [`static/`](src/isef01_lernzeit_manager/static/) | HTML, CSS and JavaScript | Renders pages & sends HTTP requests to  `/api/...`. |
| **API Layer** | [`main.py`](src/isef01_lernzeit_manager/main.py) and module specific routes in [`/api`](src/isef01_lernzeit_manager/api/) | Python and FastAPI | Defines HTTP routes, converts HTTP input/output, and calls business-logic services. |
| **Validation Schemas** | `tbd` | Pydantic | Validation and serialization for API Operations|
| **Business Logic** | [`/services`](src/isef01_lernzeit_manager/services/) | Python | Contains use cases and domain rules. No direct HTTP or SQL logic. |
| **Data Access Layer** | [`/persistence/data_access`](src/isef01_lernzeit_manager/persistence/data_access/) | Python | Translates domain operations into database queries. |
| **Database** | [`/persistence`](src/isef01_lernzeit_manager/persistence/) | SqlAlchemy & Sqlite | Configuration of database. |

### Database schema

The database design is defined in [`datenbank_entwurf.sql`](docs/database/datenbank_entwurf.sql).

```mermaid
erDiagram
    module ||--o{ lernziele : "contains"
    lernziele ||--o{ zwischenziele : "contains"
    lernziele ||--o{ lernzeiten : "records"
    zwischenziele o|--o{ lernzeiten : "optionally records"

    module {
        TEXT id PK
        TEXT title
        REAL ects
        TEXT exam_type
        TEXT completed_on
    }

    lernziele {
        INTEGER id PK
        TEXT title
        TEXT description
        TEXT module_id FK
        TEXT start_date
        TEXT end_date
        INTEGER accumulated_study_time_min
        TEXT status
    }

    zwischenziele {
        INTEGER id PK
        TEXT title
        TEXT description
        INTEGER lernziel_id FK
        TEXT start_date
        TEXT end_date
        INTEGER accumulated_study_time_min
        TEXT status
    }

    lernzeiten {
        INTEGER id PK
        INTEGER lernziel_id FK
        INTEGER zwischenziel_id FK
        TEXT date
        INTEGER duration
    }
```
The SQL and SQLAlchemy definitions are compared in CI with:

```bash
uv run python scripts/check_schema.py
```


### Tests

tbd
