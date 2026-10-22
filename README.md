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
    Frontend["Frontend"] -- HTTP Requests --> APILayer
    APILayer["API Layer"] -- Calls --> ServiceLayer["Business Logic<br>()"]
    ServiceLayer -- Uses --> DataAccessLayer["Data Access Layer"]
    DataAccessLayer -- Reads/Writes --> Database[("Database")]

    style Frontend color:#334155,fill:#e2e8f0,stroke:#64748b
    style APILayer color:#ffffff,fill:#a78bfa,stroke:#a78bfa
    style ServiceLayer color:#ffffff,stroke-width:0px,stroke-dasharray:0,fill:#2dd4bf
    style DataAccessLayer color:#ffffff,fill:#6a8cf2,stroke-width:0px,stroke-dasharray:0
    style Database color:#ffffff,fill:#fb923c,stroke:#FFE0B2
```




| Block | Location in this project | Stack | Responsibility |
| --- | --- | --- | --- |
| **Frontend** | [`templates/`](src/isef01_lernzeit_manager/templates/index.html) and [`static/`](src/isef01_lernzeit_manager/static/) | HTML and CSS | Renders pages & sends HTTP requests to  `/api/...`. |
| **API Layer** | [`main.py`](src/isef01_lernzeit_manager/main.py) | Python and FastAPI | Defines HTTP routes, converts HTTP input/output, and calls business-logic services. |
| **Business Logic** | [`services/`](src/isef01_lernzeit_manager/services/) | Python | Contains use cases and domain rules. No direct HTTP or SQL logic. |
| **Data Access Layer** | [`persistence/`](src/isef01_lernzeit_manager/persistence/) | Python | Translates domain operations into database queries. |
| **Database** |  tbd | tbd | Configuration or public test data. |


### Tests

tbd
