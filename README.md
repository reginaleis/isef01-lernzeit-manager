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
 subgraph s1["Modules"]
        n1["API Layer (api.py)"]
        n2["Business Logic (service.py)"]
        n3["Data Access Layer (data_access.py)"]
        n4["API Validation<br>(schemas.py)"]
        n5["Tables (models.py)"]
  end
    n1 ----> n2
    n2 -- uses ---> n3
    n3 --> Database[("Database")]
    n5 --> Database
    Frontend["Frontend<br>(Client)"] --> n1
    n4 --> n1

    n4@{ shape: diam}
    n5@{ shape: internal-storage}
     n3:::Peach
     n4:::Peach
     n5:::Class_02
    classDef Peach stroke-width:1px, stroke-dasharray:none, stroke:#FBB35A, fill:#FFEFDB, color:#8F632D
    classDef Class_02 fill:#BBDEFB, color:#256090, stroke:#5c84c0
    style n1 color:#ffffff,fill:#a78bfa,stroke:#a78bfa
    style n2 color:#ffffff,stroke-width:0px,stroke-dasharray:0,fill:#2dd4bf
    style n3 color:#ffffff,fill:#6a8cf2,stroke-width:0px,stroke-dasharray:0
    style Database color:#ffffff,fill:#fb923c,stroke:#FFE0B2
    style Frontend color:#334155,fill:#e2e8f0,stroke:#64748b
```




| Block | Location in this project | Stack | Responsibility |
| --- | --- | --- | --- |
| **Frontend** | [`templates/`](src/isef01_lernzeit_manager/templates/index.html) and [`static/`](src/isef01_lernzeit_manager/static/) | HTML and CSS | Renders pages & sends HTTP requests to  `/api/...`. |
| **API Layer** | [`main.py`](src/isef01_lernzeit_manager/main.py) and module specific routes in `api.py` | Python and FastAPI | Defines HTTP routes, converts HTTP input/output, and calls business-logic services. |
| **Validation Schemas** | module specific schemas in `schemas.py` | Pydantic | Validation and serialization for API Operations|
| **Business Logic** | module specific `service.py` | Python | Contains use cases and domain rules. No direct HTTP or SQL logic. |
| **Data Access Layer** | module specific `data_access.py` | Python | Translates domain operations into database queries. |
| **Database** | [`core/database.py`](src/isef01_lernzeit_manager/core/database.py) | SqlAlchemy & Sqlite | Configuration of database. |
| **Database Tables** | module specific `models.py`  | SqlAlchemy & Sqlite | Model definition that is saved in DB as tables. |


### Tests

tbd
