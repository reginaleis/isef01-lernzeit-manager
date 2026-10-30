"""
Verify that the SQL schema and SQLAlchemy metadata describe the same structure.
Used in CICD.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from sqlalchemy import Column, MetaData, Table
from sqlalchemy.dialects.sqlite import dialect

ROOT = Path(__file__).resolve().parents[1]
SQL_FILE = ROOT / "docs" / "database" / "datenbank_entwurf.sql"


def sqlite_schema() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.executescript(SQL_FILE.read_text())
    return connection


def normalize_type(value: str) -> str:
    value = value.upper().split("(", 1)[0].strip()
    if any(token in value for token in ("CHAR", "CLOB", "TEXT")):
        return "TEXT"
    if any(token in value for token in ("REAL", "FLOA", "DOUB")):
        return "REAL"
    if "INT" in value:
        return "INTEGER"
    return value


def sqlalchemy_type(column: Column[object]) -> str:
    return normalize_type(column.type.compile(dialect=dialect()))


def sql_foreign_keys(
    connection: sqlite3.Connection, table_name: str
) -> set[tuple[tuple[str, ...], str, tuple[str, ...]]]:
    rows = connection.execute(f'PRAGMA foreign_key_list("{table_name}")').fetchall()
    grouped: dict[int, list[tuple[int, str, str]]] = {}
    for constraint_id, sequence, _target, source, referenced, *_ in rows:
        grouped.setdefault(constraint_id, []).append((sequence, source, referenced))
    return {
        (
            tuple(source for _, source, _ in sorted(columns)),
            target,
            tuple(referenced for _, _, referenced in sorted(columns)),
        )
        for constraint_id, columns in grouped.items()
        for target in [next(row[2] for row in rows if row[0] == constraint_id)]
    }


def model_foreign_keys(
    table: Table,
) -> set[tuple[tuple[str, ...], str, tuple[str, ...]]]:
    return {
        (
            tuple(element.parent.name for element in constraint.elements),
            constraint.elements[0].target_fullname.split(".", 1)[0],
            tuple(element.column.name for element in constraint.elements),
        )
        for constraint in table.foreign_key_constraints
    }


def sql_indexes(
    connection: sqlite3.Connection, table_name: str
) -> set[tuple[tuple[str, ...], bool]]:
    indexes = connection.execute(f'PRAGMA index_list("{table_name}")').fetchall()
    return {
        (
            tuple(
                row[2]
                for row in connection.execute(
                    f'PRAGMA index_info("{index[1]}")'
                ).fetchall()
            ),
            bool(index[2]),
        )
        for index in indexes
        if not index[1].startswith("sqlite_autoindex_")
    }


def model_indexes(table: Table) -> set[tuple[tuple[str, ...], bool]]:
    return {
        (tuple(column.name for column in index.columns), index.unique)
        for index in table.indexes
    }


def compare(connection: sqlite3.Connection, metadata: MetaData) -> list[str]:
    errors: list[str] = []
    sql_tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
        if not row[0].startswith("sqlite_")
    }
    model_tables = set(metadata.tables)
    if sql_tables != model_tables:
        errors.append(
            f"tables differ: SQL={sorted(sql_tables)}, "
            f"SQLAlchemy={sorted(model_tables)}"
        )

    for table_name in sorted(sql_tables | model_tables):
        if table_name not in sql_tables or table_name not in model_tables:
            continue
        sql_columns = {
            row[1]: (normalize_type(row[2]), bool(row[3]) or bool(row[5]), bool(row[5]))
            for row in connection.execute(f'PRAGMA table_info("{table_name}")')
        }
        model_table = metadata.tables[table_name]
        model_columns = {
            column.name: (
                sqlalchemy_type(column),
                not column.nullable,
                column.primary_key,
            )
            for column in model_table.columns
        }
        if sql_columns != model_columns:
            errors.append(
                f"{table_name} columns differ: SQL={sql_columns}, "
                f"SQLAlchemy={model_columns}"
            )

        sql_fks = sql_foreign_keys(connection, table_name)
        model_fks = model_foreign_keys(model_table)
        if sql_fks != model_fks:
            errors.append(
                f"{table_name} foreign keys differ: SQL={sorted(sql_fks)}, "
                f"SQLAlchemy={sorted(model_fks)}"
            )

        sql_index_set = sql_indexes(connection, table_name)
        model_index_set = model_indexes(model_table)
        if sql_index_set != model_index_set:
            errors.append(
                f"{table_name} indexes differ: SQL={sorted(sql_index_set)}, "
                f"SQLAlchemy={sorted(model_index_set)}"
            )
    return errors


def main() -> int:
    from isef01_lernzeit_manager.persistence.models import Base

    errors = compare(sqlite_schema(), Base.metadata)
    if errors:
        print("Database schema mismatch:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Database schema matches SQLAlchemy metadata.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
