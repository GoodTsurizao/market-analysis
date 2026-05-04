from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

from psycopg.rows import dict_row

from export_postgres_dml import DEFAULT_OUTPUT_DIR, DEFAULT_TABLES, find_table
from postgres_connector import connect_postgres


COPY_HEADER_RE = re.compile(r'^COPY\s+"(?P<schema>[^"]+)"\."(?P<table>[^"]+)"\s+\((?P<columns>.*)\)\s+FROM stdin;$')


def unquote_copy_columns(columns_text: str) -> list[str]:
    columns: list[str] = []
    for match in re.finditer(r'"((?:[^"]|"")*)"', columns_text):
        columns.append(match.group(1).replace('""', '"'))
    return columns


def table_columns(conn, schema_name: str, table_name: str) -> list[str]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT a.attname AS column_name
            FROM pg_attribute a
            JOIN pg_class c ON c.oid = a.attrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = %(schema_name)s
              AND c.relname = %(table_name)s
              AND a.attnum > 0
              AND NOT a.attisdropped
            ORDER BY a.attnum
            """,
            {"schema_name": schema_name, "table_name": table_name},
        )
        return [row["column_name"] for row in cur.fetchall()]


def table_row_count(conn, schema_name: str, table_name: str) -> int:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(f'SELECT count(*) AS row_count FROM "{schema_name}"."{table_name}"')
        return cur.fetchone()["row_count"]


def exported_copy_info(path: Path) -> tuple[list[str], int]:
    copy_columns: list[str] | None = None
    data_rows = 0
    in_copy = False

    with path.open(encoding="utf-8", newline="") as file:
        for line in file:
            line = line.rstrip("\r\n")
            if in_copy:
                if line == r"\.":
                    return copy_columns or [], data_rows
                data_rows += 1
                continue

            match = COPY_HEADER_RE.match(line)
            if match:
                copy_columns = unquote_copy_columns(match.group("columns"))
                in_copy = True

    raise RuntimeError(f"COPY terminator not found: {path}")


def parse_table_arg(value: str) -> tuple[str | None, str]:
    parts = value.split(".", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return None, value


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check exported PostgreSQL DML files.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument("--schema", help="Default schema for unqualified table names.")
    parser.add_argument(
        "tables",
        nargs="*",
        default=list(DEFAULT_TABLES),
        help="Tables to check. Use table or schema.table.",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    had_diff = False

    with connect_postgres() as conn:
        for table_arg in args.tables:
            schema_name, table_name = parse_table_arg(table_arg)
            table = find_table(conn, table_name, schema_name or args.schema)
            schema_name = table["schema_name"]
            table_name = table["table_name"]
            path = args.output_dir / f"{schema_name}.{table_name}.sql"

            expected_columns = table_columns(conn, schema_name, table_name)
            expected_rows = table_row_count(conn, schema_name, table_name)
            actual_columns, actual_rows = exported_copy_info(path)

            print(
                f"{schema_name}.{table_name}: "
                f"rows expected={expected_rows} actual={actual_rows}; "
                f"columns expected={len(expected_columns)} actual={len(actual_columns)}"
            )

            if expected_rows != actual_rows:
                had_diff = True
                print("  row count mismatch")
            if expected_columns != actual_columns:
                had_diff = True
                print("  column mismatch")
                print(f"  expected: {expected_columns}")
                print(f"  actual:   {actual_columns}")

    return 1 if had_diff else 0


if __name__ == "__main__":
    raise SystemExit(main())
