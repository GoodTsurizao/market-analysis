from __future__ import annotations

import sys
from pathlib import Path

from psycopg.rows import dict_row

from export_postgres_ddl import DEFAULT_OUTPUT_DIR, safe_filename, schema_filter_sql
from postgres_connector import connect_postgres


def list_files(directory: Path) -> set[str]:
    if not directory.exists():
        return set()
    return {path.name for path in directory.glob("*.sql")}


def expected_objects(conn) -> dict[str, set[str]]:
    where_n, params_n = schema_filter_sql(None, alias="n")
    where_ns, params_ns = schema_filter_sql(None, alias="ns")

    expected: dict[str, set[str]] = {
        "schemas": set(),
        "tables": set(),
        "views": set(),
        "sequences": set(),
        "indexes": set(),
        "foreign_keys": set(),
        "functions": set(),
        "triggers": set(),
        "comments": set(),
    }

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            f"""
            SELECT n.nspname AS schema_name
            FROM pg_namespace n
            WHERE {where_n}
            ORDER BY n.nspname
            """,
            params_n,
        )
        for row in cur.fetchall():
            expected["schemas"].add(safe_filename(row["schema_name"]))

        cur.execute(
            f"""
            SELECT n.nspname AS schema_name, c.relname AS object_name, c.relkind
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind IN ('r', 'p', 'v', 'm')
              AND {where_n}
            ORDER BY n.nspname, c.relname
            """,
            params_n,
        )
        relations = cur.fetchall()

        for relation in relations:
            filename = safe_filename(relation["schema_name"], relation["object_name"])
            if relation["relkind"] in ("r", "p"):
                expected["tables"].add(filename)
            else:
                expected["views"].add(filename)

        cur.execute(
            f"""
            SELECT n.nspname AS schema_name, c.relname AS sequence_name
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind = 'S'
              AND {where_n}
            ORDER BY n.nspname, c.relname
            """,
            params_n,
        )
        for row in cur.fetchall():
            expected["sequences"].add(safe_filename(row["schema_name"], row["sequence_name"]))

        cur.execute(
            f"""
            SELECT ns.nspname AS schema_name, tbl.relname AS table_name, idx.relname AS index_name
            FROM pg_index i
            JOIN pg_class idx ON idx.oid = i.indexrelid
            JOIN pg_class tbl ON tbl.oid = i.indrelid
            JOIN pg_namespace ns ON ns.oid = tbl.relnamespace
            WHERE {where_ns}
            ORDER BY ns.nspname, tbl.relname, idx.relname
            """,
            params_ns,
        )
        for row in cur.fetchall():
            expected["indexes"].add(
                safe_filename(row["schema_name"], row["table_name"], row["index_name"])
            )

        cur.execute(
            f"""
            SELECT n.nspname AS schema_name, c.relname AS table_name, con.conname AS constraint_name
            FROM pg_constraint con
            JOIN pg_class c ON c.oid = con.conrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE con.contype = 'f'
              AND {where_n}
            ORDER BY n.nspname, c.relname, con.conname
            """,
            params_n,
        )
        for row in cur.fetchall():
            expected["foreign_keys"].add(
                safe_filename(row["schema_name"], row["table_name"], row["constraint_name"])
            )

        cur.execute(
            f"""
            SELECT
                n.nspname AS schema_name,
                p.proname AS function_name,
                pg_get_function_identity_arguments(p.oid) AS identity_args
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            WHERE {where_n}
            ORDER BY n.nspname, p.proname, pg_get_function_identity_arguments(p.oid)
            """,
            params_n,
        )
        for row in cur.fetchall():
            expected["functions"].add(
                safe_filename(
                    row["schema_name"],
                    row["function_name"],
                    row["identity_args"] or "no_args",
                )
            )

        cur.execute(
            f"""
            SELECT n.nspname AS schema_name, c.relname AS table_name, t.tgname AS trigger_name
            FROM pg_trigger t
            JOIN pg_class c ON c.oid = t.tgrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE NOT t.tgisinternal
              AND {where_n}
            ORDER BY n.nspname, c.relname, t.tgname
            """,
            params_n,
        )
        for row in cur.fetchall():
            expected["triggers"].add(
                safe_filename(row["schema_name"], row["table_name"], row["trigger_name"])
            )

        cur.execute(
            f"""
            WITH relation_comments AS (
                SELECT c.oid, n.nspname AS schema_name, c.relname AS object_name
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relkind IN ('r', 'p', 'v', 'm')
                  AND {where_n}
                  AND obj_description(c.oid, 'pg_class') IS NOT NULL
            ),
            column_comments AS (
                SELECT c.oid, n.nspname AS schema_name, c.relname AS object_name
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                JOIN pg_attribute a ON a.attrelid = c.oid
                WHERE c.relkind IN ('r', 'p', 'v', 'm')
                  AND a.attnum > 0
                  AND NOT a.attisdropped
                  AND {where_n}
                  AND col_description(a.attrelid, a.attnum) IS NOT NULL
            ),
            constraint_comments AS (
                SELECT c.oid, n.nspname AS schema_name, c.relname AS object_name
                FROM pg_constraint con
                JOIN pg_class c ON c.oid = con.conrelid
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE con.contype IN ('p', 'u', 'c', 'x')
                  AND {where_n}
                  AND obj_description(con.oid, 'pg_constraint') IS NOT NULL
            )
            SELECT DISTINCT schema_name, object_name
            FROM (
                SELECT schema_name, object_name FROM relation_comments
                UNION ALL
                SELECT schema_name, object_name FROM column_comments
                UNION ALL
                SELECT schema_name, object_name FROM constraint_comments
            ) x
            ORDER BY schema_name, object_name
            """,
            params_n,
        )
        for row in cur.fetchall():
            expected["comments"].add(safe_filename(row["schema_name"], row["object_name"]))

    return expected


def main() -> int:
    output_dir = DEFAULT_OUTPUT_DIR
    with connect_postgres() as conn:
        expected = expected_objects(conn)

    had_diff = False
    for category, expected_files in expected.items():
        actual_files = list_files(output_dir / category)
        missing = sorted(expected_files - actual_files)
        extra = sorted(actual_files - expected_files)

        print(f"{category}: expected={len(expected_files)} actual={len(actual_files)}")
        if missing:
            had_diff = True
            print("  missing:")
            for name in missing:
                print(f"    {name}")
        if extra:
            had_diff = True
            print("  extra:")
            for name in extra:
                print(f"    {name}")

    return 1 if had_diff else 0


if __name__ == "__main__":
    raise SystemExit(main())
